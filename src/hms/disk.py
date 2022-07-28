#!/usr/bin/env python3

import glob
import os
import re

class Disk():
    def __init__(self):
        self.disk_devices = [os.path.basename(dir) for dir in glob.glob('/sys/class/block/*') if not re.match(r'^loop|^zram|^sr', os.path.basename(dir))]
        self.disk = self._get_disk()

    def _read_stats(self, disk_device):
        """
        a function to read metric values into a list from a specific file
        """
        values = []

        try:
            with open(f'/sys/class/block/{disk_device}/stat', 'rt') as f:
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
            'read_io': 0,
            'read_merge': 1,
            'read_sector': 2,
            'write_io': 4,
            'write_merge': 5,
            'write_sector': 6,
            'in_flight': 8,
        }

        for metric, index in metrics.items():
            for disk_device in self.disk_devices:
                if metric not in disk:
                    disk[metric] = {}

                disk[metric][disk_device] = self._read_stats(disk_device)[index]

        return disk
