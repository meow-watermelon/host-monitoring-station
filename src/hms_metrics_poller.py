#!/usr/bin/env python3

import argparse
import importlib.util
import os
import rrdtool
import sys

# load host monitoring station module - hms
spec = importlib.util.spec_from_file_location("hms", f"{os.getcwd()}/hms/__init__.py")
hms = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = hms
spec.loader.exec_module(hms)


class Metrics:
    def __init__(self, config_file):
        self.config = hms.utils.read_config(config_file)

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
        metrics = [
            "memory_total",
            "memory_free",
            "memory_avail",
            "buffer",
            "cache",
            "swap_total",
            "swap_free",
            "page_tables",
        ]
        rrd_filename = self.config["RRD_DB_PATH"] + "/memory.rrd"

        # populate metrics
        memory = hms.memory.Memory().memory
        metric_values = []

        for metric in metrics:
            metric_values.append(memory[metric])

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
        "--config", type=str, required=True, help="Host Monitoring Station config file"
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
