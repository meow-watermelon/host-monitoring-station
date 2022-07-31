#!/usr/bin/env python3

import collections
import rrdtool
from . import utils


class Graph:
    def __init__(self, rrd_db_dir, rrd_graph_dir, size, start, end):
        self.rrd_db_dir = rrd_db_dir
        self.rrd_graph_dir = rrd_graph_dir
        self.rrd_graph_format = "PNG"
        self.size = self._set_size(size)
        self.start = start
        self.end = end
        self.color_plate = [
            "#191970",
            "#FF0000",
            "#00FF00",
            "#0000FF",
            "#FF8C00",
            "#00FFFF",
            "#FF00FF",
            "#800000",
            "#808000",
            "#008000",
            "#800080",
            "#008080",
            "#000080",
        ]

    def _set_size(self, size):
        """
        set graph size - (width, height)
        """
        sizes = {
            "small": (600, 200),
            "medium": (900, 300),
            "large": (1200, 400),
        }
        if size in sizes:
            return sizes[size]
        else:
            return sizes["medium"]

    def plot_disk_graph(self):
        """
        plot disk RRD graphs
        """
        # set up graph attributes
        disk_metric_mappings = {
            "read_io": {
                "rrd_filename": self.rrd_db_dir + "/disk-read_io.rrd",
                "graph_title": "Number of Read I/Os (per second)",
                "graph_vertical_label": "count/second",
                "graph_filename": self.rrd_graph_dir + "/disk-read_io.png",
            },
            "read_merge": {
                "rrd_filename": self.rrd_db_dir + "/disk-read_merge.rrd",
                "graph_title": "Number of Read I/Os Merged (per second)",
                "graph_vertical_label": "count/second",
                "graph_filename": self.rrd_graph_dir + "/disk-read_merge.png",
            },
            "read_sector": {
                "rrd_filename": self.rrd_db_dir + "/disk-read_sector.rrd",
                "graph_title": "Number of Sectors Read (per second)",
                "graph_vertical_label": "sector/second",
                "graph_filename": self.rrd_graph_dir + "/disk-read_sector.png",
            },
            "write_io": {
                "rrd_filename": self.rrd_db_dir + "/disk-write_io.rrd",
                "graph_title": "Number of Write I/Os (per second)",
                "graph_vertical_label": "count/second",
                "graph_filename": self.rrd_graph_dir + "/disk-write_io.png",
            },
            "write_merge": {
                "rrd_filename": self.rrd_db_dir + "/disk-write_merge.rrd",
                "graph_title": "Number of Write I/Os Merged (per second)",
                "graph_vertical_label": "count/second",
                "graph_filename": self.rrd_graph_dir + "/disk-write_merge.png",
            },
            "write_sector": {
                "rrd_filename": self.rrd_db_dir + "/disk-write_sector.rrd",
                "graph_title": "Number of Sectors Written (per second)",
                "graph_vertical_label": "sector/second",
                "graph_filename": self.rrd_graph_dir + "/disk-write_sector.png",
            },
            "in_flight": {
                "rrd_filename": self.rrd_db_dir + "/disk-in_flight.rrd",
                "graph_title": "Number of I/Os In Flight (per second)",
                "graph_vertical_label": "count/second",
                "graph_filename": self.rrd_graph_dir + "/disk-in_flight.png",
            },
        }

        for metric, graph_meta in disk_metric_mappings.items():
            # metric mapping variables
            rrd_filename = graph_meta["rrd_filename"]
            graph_title = graph_meta["graph_title"]
            graph_vertical_label = graph_meta["graph_vertical_label"]
            graph_filename = graph_meta["graph_filename"]

            # get disk device names
            disk_devices = utils.get_rrd_ds(rrd_filename)

            # get color plate list
            disk_color_plate = utils.rotate_color_plate(disk_devices, self.color_plate)

            # plot disk graphs
            disk = collections.OrderedDict()
            for count in range(len(disk_devices)):
                disk_device = disk_devices[count]
                disk[disk_device] = {
                    "color": disk_color_plate[count],
                    "legend": disk_device,
                    "style": "LINE1",
                }

            # disk graph variables
            disk_graph_commands = []
            for disk_device, meta in disk.items():
                color = meta["color"]
                legend = meta["legend"]
                style = meta["style"]
                disk_graph_commands.append(
                    f"DEF:{disk_device}={rrd_filename}:{disk_device}:LAST"
                )
                disk_graph_commands.append(f"{style}:{disk_device}{color}:{legend}")
                disk_graph_commands.append(f"GPRINT:{disk_device}:MAX:max\: %8.1lf")
                disk_graph_commands.append(f"GPRINT:{disk_device}:MIN:min\: %8.1lf")
                disk_graph_commands.append(
                    f"GPRINT:{disk_device}:LAST:last\: %8.1lf \j"
                )

            # generate graph
            rrdtool.graph(
                graph_filename,
                "-a",
                self.rrd_graph_format,
                "--width",
                str(self.size[0]),
                "--height",
                str(self.size[1]),
                "--end",
                str(self.end),
                "--start",
                str(self.start),
                "--title",
                graph_title,
                "--vertical-label",
                graph_vertical_label,
                disk_graph_commands,
            )

    def plot_memory_graph(self):
        """
        plot memory RRD graphs
        """
        # set up RRD DB filename
        rrd_filename = self.rrd_db_dir + "/memory.rrd"

        # plot memory graphs
        memory = collections.OrderedDict()
        memory = {
            "memory_total": {
                "color": "#808080",
                "legend": "Total Memory",
                "style": "AREA",
            },
            "memory_free": {
                "color": "#800080",
                "legend": "Free Memory",
                "style": "LINE1",
            },
            "memory_avail": {
                "color": "#FF0000",
                "legend": "Available Memory",
                "style": "LINE1",
            },
            "buffer": {
                "color": "#FF00FF",
                "legend": "Buffer",
                "style": "LINE1",
            },
            "cache": {
                "color": "#0000FF",
                "legend": "Cache",
                "style": "LINE1",
            },
        }

        # set up graph attributes
        memory_graph_title = "Memory Usage (kB)"
        memory_graph_vertical_label = "kB"
        memory_graph_filename = self.rrd_graph_dir + "/memory-memory.png"
        memory_graph_commands = []
        for metric, meta in memory.items():
            color = meta["color"]
            legend = meta["legend"]
            style = meta["style"]
            memory_graph_commands.append(f"DEF:{metric}={rrd_filename}:{metric}:LAST")
            memory_graph_commands.append(f"{style}:{metric}{color}:{legend}")
            memory_graph_commands.append(f"GPRINT:{metric}:MAX:max\: %12.1lf")
            memory_graph_commands.append(f"GPRINT:{metric}:MIN:min\: %12.1lf")
            memory_graph_commands.append(f"GPRINT:{metric}:LAST:last\: %12.1lf \j")

        # generate graph
        rrdtool.graph(
            memory_graph_filename,
            "-a",
            self.rrd_graph_format,
            "--width",
            str(self.size[0]),
            "--height",
            str(self.size[1]),
            "--end",
            str(self.end),
            "--start",
            str(self.start),
            "--title",
            memory_graph_title,
            "--vertical-label",
            memory_graph_vertical_label,
            memory_graph_commands,
        )

        # plot swap graph
        swap = collections.OrderedDict()
        swap = {
            "swap_total": {
                "color": "#808080",
                "legend": "Total Swap",
                "style": "AREA",
            },
            "swap_free": {
                "color": "#800080",
                "legend": "Free Swap",
                "style": "LINE1",
            },
        }

        # set up graph attributes
        swap_graph_title = "Swap Usage (kB)"
        swap_graph_vertical_label = "kB"
        swap_graph_filename = self.rrd_graph_dir + "/memory-swap.png"
        swap_graph_commands = []
        for metric, meta in swap.items():
            color = meta["color"]
            legend = meta["legend"]
            style = meta["style"]
            swap_graph_commands.append(f"DEF:{metric}={rrd_filename}:{metric}:LAST")
            swap_graph_commands.append(f"{style}:{metric}{color}:{legend}")
            swap_graph_commands.append(f"GPRINT:{metric}:MAX:max\: %12.1lf")
            swap_graph_commands.append(f"GPRINT:{metric}:MIN:min\: %12.1lf")
            swap_graph_commands.append(f"GPRINT:{metric}:LAST:last\: %12.1lf \j")

        # generate graph
        rrdtool.graph(
            swap_graph_filename,
            "-a",
            self.rrd_graph_format,
            "--width",
            str(self.size[0]),
            "--height",
            str(self.size[1]),
            "--end",
            str(self.end),
            "--start",
            str(self.start),
            "--title",
            swap_graph_title,
            "--vertical-label",
            swap_graph_vertical_label,
            swap_graph_commands,
        )

    def plot_os_graph(self):
        """
        plot OS RRD graphs
        """
        # set up RRD DB filename
        rrd_filename = self.rrd_db_dir + "/os.rrd"

        # plot loadavg graph
        loadavg = collections.OrderedDict()
        loadavg = {
            "loadavg_1min": {
                "color": "#FF0000",
                "legend": "LoadAvg 1min",
                "style": "LINE1",
            },
            "loadavg_5min": {
                "color": "#00FF00",
                "legend": "LoadAvg 5min",
                "style": "LINE1",
            },
            "loadavg_15min": {
                "color": "#0000FF",
                "legend": "LoadAvg 15min",
                "style": "LINE1",
            },
        }

        # set up graph attributes
        loadavg_graph_title = "Load Average 1min/5min/15min"
        loadavg_graph_filename = self.rrd_graph_dir + "/os-loadavg.png"
        loadavg_graph_commands = []
        for metric, meta in loadavg.items():
            color = meta["color"]
            legend = meta["legend"]
            style = meta["style"]
            loadavg_graph_commands.append(f"DEF:{metric}={rrd_filename}:{metric}:LAST")
            loadavg_graph_commands.append(f"{style}:{metric}{color}:{legend}")
            loadavg_graph_commands.append(f"GPRINT:{metric}:MAX:max\: %6.2lf")
            loadavg_graph_commands.append(f"GPRINT:{metric}:MIN:min\: %6.2lf")
            loadavg_graph_commands.append(f"GPRINT:{metric}:LAST:last\: %6.2lf \j")

        # generate graph
        rrdtool.graph(
            loadavg_graph_filename,
            "-a",
            self.rrd_graph_format,
            "-X",
            str(0),
            "--width",
            str(self.size[0]),
            "--height",
            str(self.size[1]),
            "--end",
            str(self.end),
            "--start",
            str(self.start),
            "--title",
            loadavg_graph_title,
            loadavg_graph_commands,
        )

        # plot fd graph
        fd = collections.OrderedDict()
        fd = {
            "num_used_fd": {
                "color": "#FF0000",
                "legend": "Number of Used FDs",
                "style": "LINE1",
            },
        }

        # set up graph attributes
        fd_graph_title = "File Descriptors Usage"
        fd_graph_vertical_label = "count"
        fd_graph_filename = self.rrd_graph_dir + "/os-fd.png"
        fd_graph_commands = []
        for metric, meta in fd.items():
            color = meta["color"]
            legend = meta["legend"]
            style = meta["style"]
            fd_graph_commands.append(f"DEF:{metric}={rrd_filename}:{metric}:LAST")
            fd_graph_commands.append(f"{style}:{metric}{color}:{legend}")
            fd_graph_commands.append(f"GPRINT:{metric}:MAX:max\: %20.1lf")
            fd_graph_commands.append(f"GPRINT:{metric}:MIN:min\: %20.1lf")
            fd_graph_commands.append(f"GPRINT:{metric}:LAST:last\: %20.1lf \j")

        # generate graph
        rrdtool.graph(
            fd_graph_filename,
            "-a",
            self.rrd_graph_format,
            "--width",
            str(self.size[0]),
            "--height",
            str(self.size[1]),
            "--end",
            str(self.end),
            "--start",
            str(self.start),
            "--title",
            fd_graph_title,
            "--vertical-label",
            fd_graph_vertical_label,
            fd_graph_commands,
        )

        # plot procs graph
        procs = collections.OrderedDict()
        procs = {
            "num_total_procs": {
                "color": "#FF0000",
                "legend": "Number of Total Processes",
                "style": "LINE1",
            },
            "num_running_procs": {
                "color": "#00FF00",
                "legend": "Number of Running Processes",
                "style": "LINE1",
            },
            "num_blocked_procs": {
                "color": "#0000FF",
                "legend": "Number of Blocked Processes",
                "style": "LINE1",
            },
            "num_zombie_procs": {
                "color": "#FF00FF",
                "legend": "Number of Zombie Processes",
                "style": "LINE1",
            },
        }

        # set up graph attributes
        procs_graph_title = "Processes States"
        procs_graph_vertical_count = "count"
        procs_graph_filename = self.rrd_graph_dir + "/os-procs.png"
        procs_graph_commands = []
        for metric, meta in procs.items():
            color = meta["color"]
            legend = meta["legend"]
            style = meta["style"]
            procs_graph_commands.append(f"DEF:{metric}={rrd_filename}:{metric}:LAST")
            procs_graph_commands.append(f"{style}:{metric}{color}:{legend}")
            procs_graph_commands.append(f"GPRINT:{metric}:MAX:max\: %20.1lf")
            procs_graph_commands.append(f"GPRINT:{metric}:MIN:min\: %20.1lf")
            procs_graph_commands.append(f"GPRINT:{metric}:LAST:last\: %20.1lf \j")

        # generate graph
        rrdtool.graph(
            procs_graph_filename,
            "-a",
            self.rrd_graph_format,
            "--width",
            str(self.size[0]),
            "--height",
            str(self.size[1]),
            "--end",
            str(self.end),
            "--start",
            str(self.start),
            "--title",
            procs_graph_title,
            "--vertical-label",
            procs_graph_vertical_count,
            procs_graph_commands,
        )

        # plot context_switch graph
        context_switch = collections.OrderedDict()
        context_switch = {
            "num_context_switch": {
                "color": "#FF0000",
                "legend": "Number of Context Switches",
                "style": "LINE1",
            },
        }

        # set up graph attributes
        context_switch_graph_title = "Context Switches States (per second)"
        context_switch_graph_vertical_label = "count/second"
        context_switch_graph_filename = self.rrd_graph_dir + "/os-context_switch.png"
        context_switch_graph_commands = []
        for metric, meta in context_switch.items():
            color = meta["color"]
            legend = meta["legend"]
            style = meta["style"]
            context_switch_graph_commands.append(
                f"DEF:{metric}={rrd_filename}:{metric}:LAST"
            )
            context_switch_graph_commands.append(f"{style}:{metric}{color}:{legend}")
            context_switch_graph_commands.append(f"GPRINT:{metric}:MAX:max\: %20.1lf")
            context_switch_graph_commands.append(f"GPRINT:{metric}:MIN:min\: %20.1lf")
            context_switch_graph_commands.append(
                f"GPRINT:{metric}:LAST:last\: %20.1lf \j"
            )

        # generate graph
        rrdtool.graph(
            context_switch_graph_filename,
            "-a",
            self.rrd_graph_format,
            "--width",
            str(self.size[0]),
            "--height",
            str(self.size[1]),
            "--end",
            str(self.end),
            "--start",
            str(self.start),
            "--title",
            context_switch_graph_title,
            "--vertical-label",
            context_switch_graph_vertical_label,
            context_switch_graph_commands,
        )

    def plot_network_graph(self):
        """
        plot network RRD graphs
        """
        # set up graph attributes
        network_metric_mappings = {
            "rx_bytes": {
                "rrd_filename": self.rrd_db_dir + "/network-rx_bytes.rrd",
                "graph_title": "Number of Good Received Bytes (per second)",
                "graph_vertical_label": "byte/second",
                "graph_filename": self.rrd_graph_dir + "/network-rx_bytes.png",
            },
            "rx_errors": {
                "rrd_filename": self.rrd_db_dir + "/network-rx_errors.rrd",
                "graph_title": "Number of Bad Packets Received (per second)",
                "graph_vertical_label": "packet/second",
                "graph_filename": self.rrd_graph_dir + "/network-rx_errors.png",
            },
            "rx_dropped": {
                "rrd_filename": self.rrd_db_dir + "/network-rx_dropped.rrd",
                "graph_title": "Number of Packets Received But Dropped (per second)",
                "graph_vertical_label": "packet/second",
                "graph_filename": self.rrd_graph_dir + "/network-rx_dropped.png",
            },
            "tx_bytes": {
                "rrd_filename": self.rrd_db_dir + "/network-tx_bytes.rrd",
                "graph_title": "Number of Good Transmitted Bytes (per second)",
                "graph_vertical_label": "byte/second",
                "graph_filename": self.rrd_graph_dir + "/network-tx_bytes.png",
            },
            "tx_errors": {
                "rrd_filename": self.rrd_db_dir + "/network-tx_errors.rrd",
                "graph_title": "Number of Bad Packets Transmitted (per second)",
                "graph_vertical_label": "packet/second",
                "graph_filename": self.rrd_graph_dir + "/network-tx_errors.png",
            },
            "tx_dropped": {
                "rrd_filename": self.rrd_db_dir + "/network-tx_dropped.rrd",
                "graph_title": "Number of Packets Dropped In Transmission (per second)",
                "graph_vertical_label": "packet/second",
                "graph_filename": self.rrd_graph_dir + "/network-rx_dropped.png",
            },
            "collisions": {
                "rrd_filename": self.rrd_db_dir + "/network-collisions.rrd",
                "graph_title": "Number of Collisions (per second)",
                "graph_vertical_label": "count/second",
                "graph_filename": self.rrd_graph_dir + "/network-collisions.png",
            },
        }

        for metric, graph_meta in network_metric_mappings.items():
            # metric mapping variables
            rrd_filename = graph_meta["rrd_filename"]
            graph_title = graph_meta["graph_title"]
            graph_vertical_label = graph_meta["graph_vertical_label"]
            graph_filename = graph_meta["graph_filename"]

            # get network interface names
            interfaces = utils.get_rrd_ds(rrd_filename)

            # get color plate list
            interface_color_plate = utils.rotate_color_plate(
                interfaces, self.color_plate
            )

            # plot network graphs
            network = collections.OrderedDict()
            for count in range(len(interfaces)):
                interface = interfaces[count]
                network[interface] = {
                    "color": interface_color_plate[count],
                    "legend": interface,
                    "style": "LINE1",
                }

            # network graph variables
            network_graph_commands = []
            for interface, meta in network.items():
                color = meta["color"]
                legend = meta["legend"]
                style = meta["style"]
                network_graph_commands.append(
                    f"DEF:{interface}={rrd_filename}:{interface}:LAST"
                )
                network_graph_commands.append(f"{style}:{interface}{color}:{legend}")
                network_graph_commands.append(f"GPRINT:{interface}:MAX:max\: %8.1lf")
                network_graph_commands.append(f"GPRINT:{interface}:MIN:min\: %8.1lf")
                network_graph_commands.append(
                    f"GPRINT:{interface}:LAST:last\: %8.1lf \j"
                )

            # generate graph
            rrdtool.graph(
                graph_filename,
                "-a",
                self.rrd_graph_format,
                "--width",
                str(self.size[0]),
                "--height",
                str(self.size[1]),
                "--end",
                str(self.end),
                "--start",
                str(self.start),
                "--title",
                graph_title,
                "--vertical-label",
                graph_vertical_label,
                network_graph_commands,
            )