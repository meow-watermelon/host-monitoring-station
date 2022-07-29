#!/usr/bin/env python3

import glob
import os
from . import utils

class Network():
    def __init__(self):
        self.interfaces = utils.get_network_interfaces()
        self.network = self._get_network()

    def _read_stats(self, interface, metric):
        """
        a function to read metric value from a specific file
        """
        value = None

        try:
            with open(f'/sys/class/net/{interface}/statistics/{metric}', 'rt') as f:
                metric_lines = f.readlines()
        except:
            pass
        else:
            value = metric_lines[0].strip()

        return value

    def _get_network(self):
        """
        get network interfaces stats data
        ref.: https://docs.kernel.org/networking/statistics.html
        """
        network = {}
        metrics = ['rx_bytes', 'rx_errors', 'rx_dropped', 'tx_bytes', 'tx_errors', 'tx_dropped', 'collisions']

        for metric in metrics:
            for interface in self.interfaces:
                if metric not in network:
                    network[metric] = {}

                network[metric][interface] = self._read_stats(interface, metric)

        return network
