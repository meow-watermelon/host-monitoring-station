#!/usr/bin/env python3

import collections
import rrdtool

class Graph():
    def __init__(self, rrd_db_dir, rrd_graph_dir, size, start, end):
        self.rrd_db_dir = rrd_db_dir
        self.rrd_graph_dir = rrd_graph_dir
        self.rrd_graph_format = 'PNG'
        self.size = self._set_size(size)
        self.start = start
        self.end = end

    def _set_size(self, size):
        """
        set graph size - (width, height)
        """
        sizes = {
            'small': (600, 200),
            'medium': (900, 300),
            'large': (1200, 400),
        }
        if size in sizes:
            return sizes[size]
        else:
            return sizes['medium']

    def plot_memory_graph(self):
        """
        plot memory RRD graphs
        """
        # set up RRD DB filename
        rrd_filename = self.rrd_db_dir + '/memory.rrd'

        # plot memory graph
        memory = collections.OrderedDict()
        memory = {
            'memory_total': {
                'color': '#808080',
                'legend': 'Total Memory',
                'style': 'AREA',
            },
            'memory_free': {
                'color': '#800080',
                'legend': 'Free Memory',
                'style': 'LINE1',
            },
            'memory_avail': {
                'color': '#FF0000',
                'legend': 'Available Memory',
                'style': 'LINE1',
            },
            'buffer': {
                'color': '#FF00FF',
                'legend': 'Buffer',
                'style': 'LINE1',
            },
            'cache': {
                'color': '#0000FF',
                'legend': 'Cache',
                'style': 'LINE1',
            },
        }

        # set up graph attributes
        memory_graph_title = 'Memory Usage (kB)'
        memory_graph_vertical_label = 'kB'
        memory_graph_filename = self.rrd_graph_dir + '/memory-memory.png'
        memory_graph_commands = []
        for metric, meta in memory.items():
            color = meta['color']
            legend = meta['legend']
            style = meta['style']
            memory_graph_commands.append(f'DEF:{metric}={rrd_filename}:{metric}:LAST')
            memory_graph_commands.append(f'{style}:{metric}{color}:{legend}')
            memory_graph_commands.append(f'GPRINT:{metric}:MAX:max\: %12.1lf')
            memory_graph_commands.append(f'GPRINT:{metric}:MIN:min\: %12.1lf')
            memory_graph_commands.append(f'GPRINT:{metric}:LAST:last\: %12.1lf \j')

        # generate graph
        rrdtool.graph(
            memory_graph_filename,
            '-a', self.rrd_graph_format,
            '--width', str(self.size[0]),
            '--height', str(self.size[1]),
            '--end', str(self.end),
            '--start', str(self.start),
            '--title', memory_graph_title,
            '--vertical-label', memory_graph_vertical_label, 
            memory_graph_commands,
        )

        # plot swap graph
        swap = collections.OrderedDict()
        swap = {
            'swap_total': {
                'color': '#808080',
                'legend': 'Total Swap',
                'style': 'AREA',
            },
            'swap_free': {
                'color': '#800080',
                'legend': 'Free Swap',
                'style': 'LINE1',
            },
        }

        # set up graph attributes
        swap_graph_title = 'Swap Usage (kB)'
        swap_graph_vertical_label = 'kB'
        swap_graph_filename = self.rrd_graph_dir + '/memory-swap.png'
        swap_graph_commands = []
        for metric, meta in swap.items():
            color = meta['color']
            legend = meta['legend']
            style = meta['style']
            swap_graph_commands.append(f'DEF:{metric}={rrd_filename}:{metric}:LAST')
            swap_graph_commands.append(f'{style}:{metric}{color}:{legend}')
            swap_graph_commands.append(f'GPRINT:{metric}:MAX:max\: %12.1lf')
            swap_graph_commands.append(f'GPRINT:{metric}:MIN:min\: %12.1lf')
            swap_graph_commands.append(f'GPRINT:{metric}:LAST:last\: %12.1lf \j')

        # generate graph
        rrdtool.graph(
            swap_graph_filename,
            '-a', self.rrd_graph_format,
            '--width', str(self.size[0]),
            '--height', str(self.size[1]),
            '--end', str(self.end),
            '--start', str(self.start),
            '--title', swap_graph_title,
            '--vertical-label', swap_graph_vertical_label, 
            swap_graph_commands,
        )

    def plot_os_graph(self):
        """
        plot OS RRD graphs
        """
        # set up RRD DB filename
        rrd_filename = self.rrd_db_dir + '/os.rrd'

        # plot loadavg graph
        loadavg = collections.OrderedDict()
        loadavg = {
            'loadavg_1min': {
                'color': '#FF0000',
                'legend': 'LoadAvg 1min',
                'style': 'LINE1',
            },
            'loadavg_5min': {
                'color': '#00FF00',
                'legend': 'LoadAvg 5min',
                'style': 'LINE1',
            },
            'loadavg_15min': {
                'color': '#0000FF',
                'legend': 'LoadAvg 15min',
                'style': 'LINE1',
            },
        }

        # set up graph attributes
        loadavg_graph_title = 'Load Average 1min/5min/15min'
        loadavg_graph_filename = self.rrd_graph_dir + '/os-loadavg.png'
        loadavg_graph_commands = []
        for metric, meta in loadavg.items():
            color = meta['color']
            legend = meta['legend']
            style = meta['style']
            loadavg_graph_commands.append(f'DEF:{metric}={rrd_filename}:{metric}:LAST')
            loadavg_graph_commands.append(f'{style}:{metric}{color}:{legend}')
            loadavg_graph_commands.append(f'GPRINT:{metric}:MAX:max\: %6.2lf')
            loadavg_graph_commands.append(f'GPRINT:{metric}:MIN:min\: %6.2lf')
            loadavg_graph_commands.append(f'GPRINT:{metric}:LAST:last\: %6.2lf \j')

        # generate graph
        rrdtool.graph(
            loadavg_graph_filename,
            '-a', self.rrd_graph_format,
            '-X', str(0),
            '--width', str(self.size[0]),
            '--height', str(self.size[1]),
            '--end', str(self.end),
            '--start', str(self.start),
            '--title', loadavg_graph_title,
            loadavg_graph_commands,
        )

        # plot fd graph
        fd = collections.OrderedDict()
        fd = {
            'num_used_fd': {
                'color': '#FF0000',
                'legend': 'Number of Used FDs',
                'style': 'LINE1',
            },
        }

        # set up graph attributes
        fd_graph_title = 'File Descriptors Usage'
        fd_graph_vertical_label = 'count'
        fd_graph_filename = self.rrd_graph_dir + '/os-fd.png'
        fd_graph_commands = []
        for metric, meta in fd.items():
            color = meta['color']
            legend = meta['legend']
            style = meta['style']
            fd_graph_commands.append(f'DEF:{metric}={rrd_filename}:{metric}:LAST')
            fd_graph_commands.append(f'{style}:{metric}{color}:{legend}')
            fd_graph_commands.append(f'GPRINT:{metric}:MAX:max\: %20.1lf')
            fd_graph_commands.append(f'GPRINT:{metric}:MIN:min\: %20.1lf')
            fd_graph_commands.append(f'GPRINT:{metric}:LAST:last\: %20.1lf \j')

        # generate graph
        rrdtool.graph(
            fd_graph_filename,
            '-a', self.rrd_graph_format,
            '--width', str(self.size[0]),
            '--height', str(self.size[1]),
            '--end', str(self.end),
            '--start', str(self.start),
            '--title', fd_graph_title,
            '--vertical-label', fd_graph_vertical_label,
            fd_graph_commands,
        )

        # plot procs graph
        procs = collections.OrderedDict()
        procs = {
            'num_total_procs': {
                'color': '#FF0000',
                'legend': 'Number of Total Processes',
                'style': 'LINE1',
            },
            'num_running_procs': {
                'color': '#00FF00',
                'legend': 'Number of Running Processes',
                'style': 'LINE1',
            },
            'num_blocked_procs': {
                'color': '#0000FF',
                'legend': 'Number of Blocked Processes',
                'style': 'LINE1',
            },
            'num_zombie_procs': {
                'color': '#FF00FF',
                'legend': 'Number of Zombie Processes',
                'style': 'LINE1',
            }
        }

        # set up graph attributes
        procs_graph_title = 'Processes States'
        procs_graph_vertical_count = 'count'
        procs_graph_filename = self.rrd_graph_dir + '/os-procs.png'
        procs_graph_commands = []
        for metric, meta in procs.items():
            color = meta['color']
            legend = meta['legend']
            style = meta['style']
            procs_graph_commands.append(f'DEF:{metric}={rrd_filename}:{metric}:LAST')
            procs_graph_commands.append(f'{style}:{metric}{color}:{legend}')
            procs_graph_commands.append(f'GPRINT:{metric}:MAX:max\: %20.1lf')
            procs_graph_commands.append(f'GPRINT:{metric}:MIN:min\: %20.1lf')
            procs_graph_commands.append(f'GPRINT:{metric}:LAST:last\: %20.1lf \j')

        # generate graph
        rrdtool.graph(
            procs_graph_filename,
            '-a', self.rrd_graph_format,
            '--width', str(self.size[0]),
            '--height', str(self.size[1]),
            '--end', str(self.end),
            '--start', str(self.start),
            '--title', procs_graph_title,
            '--vertical-label', procs_graph_vertical_count,
            procs_graph_commands,
        )

        # plot context_switch graph
        context_switch = collections.OrderedDict()
        context_switch = {
            'num_context_switch': {
                'color': '#FF0000',
                'legend': 'Number of Context Switches',
                'style': 'LINE1',
            },
        }

        # set up graph attributes
        context_switch_graph_title = 'Context Switches States (per second)'
        context_switch_graph_vertical_label = 'count/second'
        context_switch_graph_filename = self.rrd_graph_dir + '/os-context_switch.png'
        context_switch_graph_commands = []
        for metric, meta in context_switch.items():
            color = meta['color']
            legend = meta['legend']
            style = meta['style']
            context_switch_graph_commands.append(f'DEF:{metric}={rrd_filename}:{metric}:LAST')
            context_switch_graph_commands.append(f'{style}:{metric}{color}:{legend}')
            context_switch_graph_commands.append(f'GPRINT:{metric}:MAX:max\: %20.1lf')
            context_switch_graph_commands.append(f'GPRINT:{metric}:MIN:min\: %20.1lf')
            context_switch_graph_commands.append(f'GPRINT:{metric}:LAST:last\: %20.1lf \j')

        # generate graph
        rrdtool.graph(
            context_switch_graph_filename,
            '-a', self.rrd_graph_format,
            '--width', str(self.size[0]),
            '--height', str(self.size[1]),
            '--end', str(self.end),
            '--start', str(self.start),
            '--title', context_switch_graph_title,
            '--vertical-label', context_switch_graph_vertical_label,
            context_switch_graph_commands,
        )

g = Graph('/home/ericlee/Projects/hms/rrd', '/home/ericlee/Projects/hms/graphs', 'large', 'end-8h', 'now')
g.plot_os_graph()
g.plot_memory_graph()
