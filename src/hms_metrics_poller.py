#!/usr/bin/env python3

import argparse
import importlib.util
import os
import rrdtool
import sys
import yaml

# load host monitoring station module - hms
spec = importlib.util.spec_from_file_location('hms', f'{os.getcwd()}/hms/__init__.py')
hms = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = hms
spec.loader.exec_module(hms)

class Metrics():
    def __init__(self, config_file):
        self.config = self._read_config(config_file)

    def _read_config(self, config_file):
        config = {}

        try:
            with open(config_file, 'rt') as f:
                config = yaml.load(f, Loader=yaml.FullLoader)
        except:
            pass

        return config

    def _rrd_update(self, metrics_list, metrics_values, rrd_filename):
        """
        update RRD database wrapper
        """
        # generating data source string
        rrd_ds = ':'.join(metrics_list)

        # metrics_values_bucket is used for generating final metrics string
        metrics_values_bucket = []

        for metric in metrics_list:
            if metrics_values[metric] is None:
                metrics_values_bucket.append('U')
            else:
                metrics_values_bucket.append(str(metrics_values[metric]))

        metrics_values_string = ':'.join(metrics_values_bucket)
        rrdtool.update(
            rrd_filename,
            '--template', rrd_ds,
            f'N:{metrics_values_string}',
        )

    def poll_disk_metrics(self):
        """
        populate disk devices stats information and write to disk RRD databases
        """
        # initialize environment variables
        metrics = ['read_io', 'read_merge', 'read_sector', 'write_io', 'write_merge', 'write_sector', 'in_flight']
        
        # populate metrics
        disk_obj = hms.disk.Disk()
        disk_devices = disk_obj.disk_devices
        disk = disk_obj.disk

        # update RRD databases
        for metric in metrics:
            rrd_filename = self.config['RRD_DB_PATH'] + f'/disk-{metric}.rrd'
            self._rrd_update(disk_devices, disk[metric], rrd_filename)

    def poll_memory_metrics(self):
        """
        populate memory information and write to memory RRD databases
        """
        # initialize environment variables
        metrics = ['memory_total', 'memory_free', 'memory_avail', 'buffer', 'cache', 'swap_total', 'swap_free']
        rrd_filename = self.config['RRD_DB_PATH'] + '/memory.rrd'

        # populate metrics
        memory = hms.memory.Memory().memory

        # update RRD database
        self._rrd_update(metrics, memory, rrd_filename)

    def poll_network_metrics(self):
        """
        populate network interface stats information and write to network RRD databases
        """
        # initialize environment variables
        metrics = ['rx_bytes', 'rx_errors', 'rx_dropped', 'tx_bytes', 'tx_errors', 'tx_dropped', 'collisions']
        
        # populate metrics
        network_obj = hms.network.Network()
        interfaces = network_obj.interfaces
        network = network_obj.network

        # update RRD databases
        for metric in metrics:
            rrd_filename = self.config['RRD_DB_PATH'] + f'/network-{metric}.rrd'
            self._rrd_update(interfaces, network[metric], rrd_filename)

    def poll_os_metrics(self):
        """
        populate OS information and write to OS RRD database
        """
        # initialize environment variables
        loadavg_metrics = ['loadavg_1min', 'loadavg_5min', 'loadavg_15min']
        fd_metrics = ['num_max_fd', 'num_used_fd']
        procs_metrics = ['num_total_procs', 'num_running_procs', 'num_blocked_procs', 'num_zombie_procs']
        context_switch_metrics = ['num_context_switch']
        rrd_filename = self.config['RRD_DB_PATH'] + '/os.rrd'

        # populate metrics
        loadavg = hms.os.OS().loadavg
        fd = hms.os.OS().fd
        procs = hms.os.OS().procs
        context_switch = hms.os.OS().context_switch

        # update RRD database
        self._rrd_update(loadavg_metrics, loadavg, rrd_filename)
        self._rrd_update(fd_metrics, fd, rrd_filename)
        self._rrd_update(procs_metrics, procs, rrd_filename)
        self._rrd_update(context_switch_metrics, context_switch, rrd_filename)

if __name__ == '__main__':
    # set up args
    parser = argparse.ArgumentParser(description='Host Monitoring Station Metrics Poller')
    parser.add_argument('--config', type=str, required=True, help='Host Monitoring Station config file')
    args = parser.parse_args()

    # create metrics object
    metrics = Metrics(args.config)

    # populate memory metrics
    metrics.poll_disk_metrics()
    metrics.poll_memory_metrics()
    metrics.poll_os_metrics()
    metrics.poll_network_metrics()
