#!/usr/bin/env python3


class Memory:
    def __init__(self):
        self.memory = self._get_memory()
        self.virtual_memory = self._get_virtual_memory()

    def _get_memory(self):
        """
        get memory usage information
        unit: kB
        """
        memory = {
            "memory_total": None,
            "memory_free": None,
            "memory_avail": None,
            "buffer": None,
            "cache": None,
            "swap_total": None,
            "swap_free": None,
            "page_tables": None,
        }

        memory_metrics_mapping = {
            "memory_total": "MemTotal",
            "memory_free": "MemFree",
            "memory_avail": "MemAvailable",
            "buffer": "Buffer",
            "cache": "Cached",
            "swap_total": "SwapTotal",
            "swap_free": "SwapFree",
            "page_tables": "PageTables",
        }

        try:
            with open("/proc/meminfo", "rt") as f:
                memory_lines = f.readlines()
        except:
            pass
        else:
            for line in memory_lines:
                for metric, entry in memory_metrics_mapping.items():
                    if line.startswith(entry):
                        memory[metric] = line.strip().split()[1]
                        break

        return memory

    def _get_virtual_memory(self):
        """
        get virtual memory information
        """
        virtual_memory = {
            "minor_page_faults": None,
            "major_page_faults": None,
            "total_page_faults": None,
        }

        virtual_memory_metrics_mapping = {
            "major_page_faults": "pgmajfault",
            "total_page_faults": "pgfault",
        }

        try:
            with open("/proc/vmstat", "rt") as f:
                memory_lines = f.readlines()
        except:
            pass
        else:
            for line in memory_lines:
                for metric, entry in virtual_memory_metrics_mapping.items():
                    if line.startswith(entry):
                        virtual_memory[metric] = line.strip().split()[1]
                        break

            # calculate minor_page_faults
            virtual_memory["minor_page_faults"] = int(
                virtual_memory["total_page_faults"]
            ) - int(virtual_memory["major_page_faults"])

        return virtual_memory
