#!/usr/bin/env python3

import argparse
import glob
import importlib.util
import os
import re
import rrdtool
import sys

# load host monitoring station module - hms
spec = importlib.util.spec_from_file_location("hms", f"{os.getcwd()}/hms/__init__.py")
hms = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = hms
spec.loader.exec_module(hms)


class Bootstrap:
    def __init__(self, rrd_dir, step):
        self.rrd_dir = rrd_dir
        self.rrd_step = step

    def bootstrap_disk(self):
        """
        bootstrap disk stats information RRD databases
        """
        metrics = {
            "read_io": "COUNTER",
            "read_merge": "COUNTER",
            "read_sector": "COUNTER",
            "write_io": "COUNTER",
            "write_merge": "COUNTER",
            "write_sector": "COUNTER",
            "in_flight": "GAUGE",
        }
        disk_devices = hms.utils.get_disk_devices()

        for metric, compute in metrics.items():
            rrd_filename = self.rrd_dir + f"/disk-{metric}.rrd"
            rrdtool.create(
                rrd_filename,
                "--step",
                self.rrd_step,
                [f"DS:{disk_device}:{compute}:300:0:U" for disk_device in disk_devices],
                "RRA:AVERAGE:0.5:1m:1d",
                "RRA:AVERAGE:0.5:1h:6M",
                "RRA:AVERAGE:0.5:1d:1y",
            )

            print(f"RRD {rrd_filename} created.")

    def bootstrap_network(self):
        """
        bootstrap network stats information RRD databases
        """
        metrics = [
            "rx_bytes",
            "rx_errors",
            "rx_dropped",
            "tx_bytes",
            "tx_errors",
            "tx_dropped",
            "collisions",
        ]
        interfaces = hms.utils.get_network_interfaces()

        for metric in metrics:
            rrd_filename = self.rrd_dir + f"/network-{metric}.rrd"
            rrdtool.create(
                rrd_filename,
                "--step",
                self.rrd_step,
                [f"DS:{interface}:COUNTER:300:0:U" for interface in interfaces],
                "RRA:AVERAGE:0.5:1m:1d",
                "RRA:AVERAGE:0.5:1h:6M",
                "RRA:AVERAGE:0.5:1d:1y",
            )

            print(f"RRD {rrd_filename} created.")

    def bootstrap_memory(self):
        """
        bootstrap memory information RRD database
        """
        rrd_filename = self.rrd_dir + "/memory.rrd"
        rrdtool.create(
            rrd_filename,
            "--step",
            self.rrd_step,
            "DS:memory_total:GAUGE:300:0:U",
            "DS:memory_free:GAUGE:300:0:U",
            "DS:memory_avail:GAUGE:300:0:U",
            "DS:buffer:GAUGE:300:0:U",
            "DS:cache:GAUGE:300:0:U",
            "DS:swap_total:GAUGE:300:0:U",
            "DS:swap_free:GAUGE:300:0:U",
            "RRA:AVERAGE:0.5:1m:1d",
            "RRA:AVERAGE:0.5:1h:6M",
            "RRA:AVERAGE:0.5:1d:1y",
        )

        print(f"RRD {rrd_filename} created.")

    def bootstrap_os(self):
        """
        bootstrap OS information RRD database
        """
        rrd_filename = self.rrd_dir + "/os.rrd"
        rrdtool.create(
            rrd_filename,
            "--step",
            self.rrd_step,
            "DS:loadavg_1min:GAUGE:300:0:U",
            "DS:loadavg_5min:GAUGE:300:0:U",
            "DS:loadavg_15min:GAUGE:300:0:U",
            "DS:num_used_fd:GAUGE:300:0:U",
            "DS:num_total_procs:GAUGE:300:0:U",
            "DS:num_running_procs:GAUGE:300:0:U",
            "DS:num_blocked_procs:GAUGE:300:0:U",
            "DS:num_zombie_procs:GAUGE:300:0:U",
            "DS:num_context_switch:COUNTER:300:0:U",
            "RRA:AVERAGE:0.5:1m:1d",
            "RRA:AVERAGE:0.5:1h:6M",
            "RRA:AVERAGE:0.5:1d:1y",
        )

        print(f"RRD {rrd_filename} created.")


if __name__ == "__main__":
    # set up args
    parser = argparse.ArgumentParser(
        description="Host Monitoring Station RRD Database Bootstrap Tool"
    )
    parser.add_argument("--dir", type=str, required=True, help="RRD database directory")
    parser.add_argument(
        "--step",
        type=str,
        required=False,
        default="1m",
        help="RRD database step (default: 1m)",
    )
    args = parser.parse_args()

    # create bootstrap object
    bootstrap = Bootstrap(args.dir, args.step)
    bootstrap.bootstrap_disk()
    bootstrap.bootstrap_os()
    bootstrap.bootstrap_memory()
    bootstrap.bootstrap_network()
