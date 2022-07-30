#!/usr/bin/env python3

import glob
import os
import re
from . import utils


class Disk:
    def __init__(self):
        self.disk_devices = utils.get_disk_devices()
        self.disk = self._get_disk()

    def _read_stats(self, disk_device):
        """
        a function to read metric values into a list from a specific file
        ref.: https://www.kernel.org/doc/Documentation/block/queue-sysfs.txt

        it's possible that iostats is not enabled on the device so all values in stat would be zero

        to enable iostats:

        # echo 1 > /sys/block/<disk_device>/queue/iostats
        """
        values = []

        try:
            with open(f"/sys/class/block/{disk_device}/stat", "rt") as f:
                metric_lines = f.readlines()
        except:
            pass
        else:
            values = metric_lines[0].strip().split()

        return values

    def _get_disk(self):
        """
        get disk devices stats data
        ref.: https://www.kernel.org/doc/Documentation/block/stat.txt
        """
        disk = {}
        # format: [metric name: metric index on stat]
        metrics = {
            "read_io": 0,
            "read_merge": 1,
            "read_sector": 2,
            "write_io": 4,
            "write_merge": 5,
            "write_sector": 6,
            "in_flight": 8,
        }

        for metric, index in metrics.items():
            for disk_device in self.disk_devices:
                if metric not in disk:
                    disk[metric] = {}

                disk[metric][disk_device] = self._read_stats(disk_device)[index]

        return disk
