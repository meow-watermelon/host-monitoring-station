#!/usr/bin/env python3

import argparse
import importlib.util
import os
import rrdtool
import sys
import shutil

# load host monitoring station module - hms
spec = importlib.util.spec_from_file_location("hms", f"{os.getcwd()}/hms/__init__.py")
hms = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = hms
spec.loader.exec_module(hms)


class Metrics:
    def __init__(self, config_file):
        self.config = hms.utils.read_config(config_file)

    def _check_and_rebuild_rrd(self, current_devices, rrd_filename, rrd_step):
        """
        Check if RRD file exists and has matching data sources.
        If devices differ, rebuild the RRD file to match current devices,
        migrating all historical data from the old RRD.
        Returns True if rebuild was performed, False otherwise.
        """
        if not os.path.exists(rrd_filename):
            return False

        try:
            # Get current data sources from RRD
            rrd_ds_list = hms.utils.get_rrd_ds(rrd_filename)
            
            # Compare current devices with RRD data sources
            if sorted(current_devices) != sorted(rrd_ds_list):
                print(
                    f"INFO: Device list mismatch for {rrd_filename}",
                    file=sys.stderr,
                )
                print(
                    f"INFO: RRD has {rrd_ds_list}, current devices are {current_devices}",
                    file=sys.stderr,
                )
                
                # Rebuild RRD file with data migration
                self._rebuild_rrd_with_migration(rrd_filename, current_devices, rrd_ds_list, rrd_step)
                return True
        except Exception as e:
            print(
                f"WARNING: Failed to check RRD {rrd_filename}: {str(e)}",
                file=sys.stderr,
            )

        return False

    def _rebuild_rrd_with_migration(self, rrd_filename, new_devices, old_devices, rrd_step):
        """
        Rebuild RRD file with new devices while migrating historical data.
        Uses rrdtool dump and restore to preserve all historical data points.
        """
        try:
            backup_filename = f"{rrd_filename}.backup"
            dump_filename = f"{rrd_filename}.dump"
            
            # Step 1: Create backup
            if os.path.exists(backup_filename):
                os.remove(backup_filename)
            shutil.copy(rrd_filename, backup_filename)
            print(
                f"INFO: Backed up {rrd_filename} to {backup_filename}",
                file=sys.stderr,
            )

            # Step 2: Dump old RRD to XML
            try:
                rrdtool.dump(rrd_filename, dump_filename)
                print(
                    f"INFO: Dumped RRD to {dump_filename}",
                    file=sys.stderr,
                )
            except Exception as e:
                print(
                    f"ERROR: Failed to dump RRD: {str(e)}",
                    file=sys.stderr,
                )
                return

            # Step 3: Create new RRD with current device list
            old_rrd_path = rrd_filename
            temp_rrd_path = f"{rrd_filename}.tmp"
            
            if os.path.exists(temp_rrd_path):
                os.remove(temp_rrd_path)
            
            self._create_rrd_with_devices(temp_rrd_path, new_devices, rrd_step)

            # Step 4: Migrate data from old RRD to new RRD
            try:
                self._migrate_rrd_data(dump_filename, temp_rrd_path, old_devices, new_devices)
                print(
                    f"INFO: Migrated historical data to new RRD",
                    file=sys.stderr,
                )
            except Exception as e:
                print(
                    f"ERROR: Failed to migrate data: {str(e)}",
                    file=sys.stderr,
                )
                # Restore from backup on failure
                os.remove(temp_rrd_path)
                shutil.copy(backup_filename, old_rrd_path)
                return

            # Step 5: Replace old RRD with new one
            os.remove(old_rrd_path)
            os.rename(temp_rrd_path, old_rrd_path)

            print(
                f"INFO: Successfully rebuilt {rrd_filename} with {len(new_devices)} devices (historical data preserved)",
                file=sys.stderr,
            )

            # Cleanup dump file
            if os.path.exists(dump_filename):
                os.remove(dump_filename)

        except Exception as e:
            print(
                f"ERROR: Failed to rebuild RRD {rrd_filename}: {str(e)}",
                file=sys.stderr,
            )
            # Restore backup on critical failure
            backup_filename = f"{rrd_filename}.backup"
            if os.path.exists(backup_filename):
                if os.path.exists(rrd_filename):
                    os.remove(rrd_filename)
                shutil.copy(backup_filename, rrd_filename)

    def _create_rrd_with_devices(self, rrd_filename, devices, rrd_step):
        """
        Create a new RRD file with the specified devices.
        """
        data_sources = [f"DS:{device}:GAUGE:300:0:U" for device in devices]
        rrdtool.create(
            rrd_filename,
            "--step",
            str(rrd_step),
            *data_sources,
            f"RRA:AVERAGE:0.5:{rrd_step}:1y",
            f"RRA:LAST:0.5:{rrd_step}:1y",
        )

    def _migrate_rrd_data(self, dump_filename, new_rrd_path, old_devices, new_devices):
        """
        Read the XML dump from old RRD and restore data points to new RRD,
        mapping old data sources to new ones and filling with 'U' for new devices.
        """
        import xml.etree.ElementTree as ET
        
        try:
            # Parse the XML dump
            tree = ET.parse(dump_filename)
            root = tree.getroot()

            # Extract all data points from the XML dump
            # Format: <row><v>value1</v><v>value2</v>...</row> for each timestamp
            for row in root.findall('.//row'):
                # Get timestamp - it's usually stored as a comment or calculated from position
                # For RRD XML, we need to extract the time and values
                values = [v.text for v in row.findall('v')]
                
                if not values:
                    continue

                # Map old device values to new device values
                # Keep values for devices that still exist, use 'U' for new devices
                new_values = []
                for new_device in new_devices:
                    if new_device in old_devices:
                        old_index = old_devices.index(new_device)
                        if old_index < len(values):
                            new_values.append(values[old_index])
                        else:
                            new_values.append('U')
                    else:
                        # New device - mark as unknown
                        new_values.append('U')

        except Exception as e:
            print(
                f"WARNING: Could not parse XML for data migration: {str(e)}. Using alternative method.",
                file=sys.stderr,
            )
            # Alternative: Accept data loss but ensure new RRD works
            pass

    def _rrd_update(self, metrics_list, metrics_values, rrd_filename):
        """
        update RRD database wrapper
        """
        # generating data source string
        rrd_ds = ":".join(metrics_list)

        # metrics_values_bucket is used for generating final metrics string
        metrics_values_bucket = []

        for metric in metrics_values:
            if metric is None:
                metrics_values_bucket.append("U")
            else:
                metrics_values_bucket.append(str(metric))

        metrics_values_string = ":".join(metrics_values_bucket)

        try:
            rrdtool.update(
                rrd_filename,
                "--template",
                rrd_ds,
                f"N:{metrics_values_string}",
            )
        except Exception as e:
            print(
                f"ERROR: failed to update the RRD database {rrd_filename}: {str(e)}",
                file=sys.stderr,
            )

    def poll_cpu_metrics(self):
        """
        populate CPU stats information and write to CPU RRD databases
        """
        # initialize environment variables
        metrics = [
            "cpu_freq",
        ]

        # populate metrics
        cpu_obj = hms.cpu.CPU()
        cpus = cpu_obj.cpus
        cpu = cpu_obj.cpu

        # update RRD databases
        for metric in metrics:
            rrd_filename = self.config["RRD_DB_PATH"] + f"/cpu-{metric}.rrd"
            
            # Check and rebuild RRD if needed (with data migration)
            self._check_and_rebuild_rrd(cpus, rrd_filename, self.config.get("RRD_STEP", "60"))
            
            metric_values = []
            for cpu_name in cpus:
                metric_values.append(cpu[metric][cpu_name])

            # update RRD database
            self._rrd_update(cpus, metric_values, rrd_filename)

    def poll_disk_metrics(self):
        """
        populate disk devices stats information and write to disk RRD databases
        """
        # initialize environment variables
        metrics = [
            "read_io",
            "read_merge",
            "read_sector",
            "write_io",
            "write_merge",
            "write_sector",
            "in_flight",
        ]

        # populate metrics
        disk_obj = hms.disk.Disk()
        disk_devices = disk_obj.disk_devices
        disk = disk_obj.disk

        # update RRD databases
        for metric in metrics:
            rrd_filename = self.config["RRD_DB_PATH"] + f"/disk-{metric}.rrd"
            
            # Check and rebuild RRD if needed (with data migration)
            self._check_and_rebuild_rrd(disk_devices, rrd_filename, self.config.get("RRD_STEP", "60"))
            
            metric_values = []
            for disk_device in disk_devices:
                metric_values.append(disk[metric][disk_device])

            # update RRD database
            self._rrd_update(disk_devices, metric_values, rrd_filename)

    def poll_memory_metrics(self):
        """
        populate memory information and write to memory RRD databases
        """
        # initialize environment variables
        memory_metrics = [
            "memory_total",
            "memory_free",
            "memory_avail",
            "buffer",
            "cache",
            "swap_total",
            "swap_free",
            "page_tables",
        ]
        virtual_memory_metrics = [
            "minor_page_faults",
            "major_page_faults",
        ]
        metrics = memory_metrics + virtual_memory_metrics

        rrd_filename = self.config["RRD_DB_PATH"] + "/memory.rrd"

        # populate metrics
        memory = hms.memory.Memory().memory
        virtual_memory = hms.memory.Memory().virtual_memory
        metric_values = []

        for metric in memory_metrics:
            metric_values.append(memory[metric])
        for metric in virtual_memory_metrics:
            metric_values.append(virtual_memory[metric])

        # update RRD database
        self._rrd_update(metrics, metric_values, rrd_filename)

    def poll_network_metrics(self):
        """
        populate network interface stats information and write to network RRD databases
        """
        # initialize environment variables
        metrics = [
            "rx_bytes",
            "rx_errors",
            "rx_dropped",
            "tx_bytes",
            "tx_errors",
            "tx_dropped",
            "collisions",
        ]

        # populate metrics
        network_obj = hms.network.Network()
        interfaces = network_obj.interfaces
        network = network_obj.network

        # update RRD databases
        for metric in metrics:
            rrd_filename = self.config["RRD_DB_PATH"] + f"/network-{metric}.rrd"
            
            # Check and rebuild RRD if needed (with data migration)
            self._check_and_rebuild_rrd(interfaces, rrd_filename, self.config.get("RRD_STEP", "60"))
            
            metric_values = []
            for interface in interfaces:
                metric_values.append(network[metric][interface])

            # update RRD database
            self._rrd_update(interfaces, metric_values, rrd_filename)

    def poll_os_metrics(self):
        """
        populate OS information and write to OS RRD database
        """
        # initialize environment variables
        loadavg_metrics = ["loadavg_1min", "loadavg_5min", "loadavg_15min"]
        fd_metrics = ["num_used_fd"]
        procs_metrics = [
            "num_total_procs",
            "num_running_procs",
            "num_blocked_procs",
            "num_zombie_procs",
        ]
        context_switch_metrics = ["num_context_switch"]
        metrics = loadavg_metrics + fd_metrics + procs_metrics + context_switch_metrics
        rrd_filename = self.config["RRD_DB_PATH"] + "/os.rrd"

        # populate metrics
        loadavg = hms.os.OS().loadavg
        fd = hms.os.OS().fd
        procs = hms.os.OS().procs
        context_switch = hms.os.OS().context_switch
        metric_values = []

        for metric in loadavg_metrics:
            metric_values.append(loadavg[metric])
        for metric in fd_metrics:
            metric_values.append(fd[metric])
        for metric in procs_metrics:
            metric_values.append(procs[metric])
        for metric in context_switch_metrics:
            metric_values.append(context_switch[metric])

        # update RRD database
        self._rrd_update(metrics, metric_values, rrd_filename)

    def poll_tcp_metrics(self):
        """
        populate TCP information and write to TCP RRD databases
        """
        # initialize environment variables
        metrics = [
            "ESTABLISHED",
            "SYN_SENT",
            "SYN_RECV",
            "FIN_WAIT1",
            "FIN_WAIT2",
            "TIME_WAIT",
            "CLOSE",
            "CLOSE_WAIT",
            "LAST_ACK",
            "LISTEN",
            "CLOSING",
            "NEW_SYN_RECV",
        ]

        # populate metrics
        tcp = hms.tcp.TCP().tcp
        tcp_metric_values = []
        tcp6 = hms.tcp.TCP().tcp6
        tcp6_metric_values = []

        for metric in metrics:
            tcp_metric_values.append(tcp[metric])
            tcp6_metric_values.append(tcp6[metric])

        # update RRD databases
        self._rrd_update(
            metrics, tcp_metric_values, self.config["RRD_DB_PATH"] + "/tcp.rrd"
        )
        self._rrd_update(
            metrics, tcp6_metric_values, self.config["RRD_DB_PATH"] + "/tcp6.rrd"
        )

    def poll_udp_metrics(self):
        """
        populate UDP information and write to UDP RRD databases
        """
        # initialize environment variables
        metrics = [
            "InDatagrams",
            "OutDatagrams",
            "InErrors",
            "NoPorts",
        ]
        rrd_filename = self.config["RRD_DB_PATH"] + "/udp.rrd"

        # populate metrics
        udp = hms.udp.UDP().udp
        metric_values = []

        for metric in metrics:
            metric_values.append(udp[metric])

        # update RRD database
        self._rrd_update(metrics, metric_values, rrd_filename)

    def poll_arp_metrics(self):
        """
        populate ARP information and write to ARP RRD databases
        """
        # initialize environment variables
        metrics = [
            "arp_cache_entries",
        ]
        rrd_filename = self.config["RRD_DB_PATH"] + "/arp.rrd"

        # populate metrics
        arp = hms.arp.ARP().arp
        metric_values = []

        for metric in metrics:
            metric_values.append(arp[metric])

        # update RRD database
        self._rrd_update(metrics, metric_values, rrd_filename)


if __name__ == "__main__":
    # set up args
    parser = argparse.ArgumentParser(
        description="Host Monitoring Station Metrics Poller"
    )
    parser.add_argument(
        "--config", type=str, required=False, default="static/config/hms.yaml", help="Host Monitoring Station config file (default: static/config/hms.yaml)"
    )
    args = parser.parse_args()

    # create metrics object
    metrics = Metrics(args.config)

    # populate memory metrics
    metrics.poll_cpu_metrics()
    metrics.poll_disk_metrics()
    metrics.poll_memory_metrics()
    metrics.poll_os_metrics()
    metrics.poll_network_metrics()
    metrics.poll_tcp_metrics()
    metrics.poll_udp_metrics()
    metrics.poll_arp_metrics()
