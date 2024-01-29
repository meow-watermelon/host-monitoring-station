#!/usr/bin/env python3


class ARP:
    def __init__(self):
        self.arp = self._get_arp()

    def _get_arp(self):
        """
        get ARP cache entries information
        """
        arp = {
            "arp_cache_entries": 0,
        }

        try:
            with open("/proc/net/arp", "rt") as f:
                arp_lines = f.readlines()
        except:
            pass
        else:
            arp_cache_entries_counter = 0
            for line in arp_lines:
                if not line.startswith("IP address"):
                    arp_cache_entries_counter += 1

            arp["arp_cache_entries"] = arp_cache_entries_counter

        return arp
