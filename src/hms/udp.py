#!/usr/bin/env python3


class UDP:
    def __init__(self):
        self.udp = self._get_udp()

    def _get_udp(self):
        """
        get UDP SNMP metrics information
        """
        udp = {
            "InDatagrams": None,
            "OutDatagrams": None,
            "InErrors": None,
            "NoPorts": None,
        }

        try:
            with open("/proc/net/snmp", "rt") as f:
                udp_lines = f.readlines()
        except:
            pass
        else:
            udp_metrics_bucket = []
            for line in udp_lines:
                if line.startswith("Udp: "):
                    output = line[5:].strip().split()
                    udp_metrics_bucket.append(output)

            udp_metrics = dict(zip(udp_metrics_bucket[0], udp_metrics_bucket[1]))

            for metric_name in udp:
                udp[metric_name] = udp_metrics[metric_name]

        return udp
