#!/usr/bin/env python3

from . import utils


class CPU:
    def __init__(self):
        self.cpus = utils.get_cpu()
        self.cpu = self._get_cpu()

    def _read_stats(self, metric_file_path, cpu_name):
        """
        a function to read CPU stats data
        """
        value = None

        try:
            with open(f"{metric_file_path}", "rt") as f:
                metric_lines = f.readlines()
        except:
            pass
        else:
            value = metric_lines[0].strip()

        return value

    def _get_cpu(self):
        """
        get cpu stats data
        """
        cpu = {}
        metrics = [
            "cpu_freq",
        ]

        for metric in metrics:
            for cpu_name in self.cpus:
                if metric not in cpu:
                    cpu[metric] = {}

                if metric == "cpu_freq":
                    cpu_freq_metric_file = (
                        f"/sys/devices/system/cpu/{cpu_name}/cpufreq/scaling_cur_freq"
                    )
                    cpu[metric][cpu_name] = self._read_stats(
                        cpu_freq_metric_file, cpu_name
                    )

        return cpu
