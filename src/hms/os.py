#!/usr/bin/env python3

import subprocess

class OS():
    def __init__(self):
        self.loadavg = self._get_loadavg()
        self.fd = self._get_fd()
        self.procs = self._get_procs()
        self.context_switch = self._get_context_switch()

    def _get_loadavg(self):
        """
        get 1min, 5min and 15min load average values
        """
        loadavg = {
            'loadavg_1min': None,
            'loadavg_5min': None,
            'loadavg_15min': None,
        }

        try:
            with open('/proc/loadavg', 'rt') as f:
                loadavg_lines = f.readlines()
        except:
            pass
        else:
            loadavg_values = loadavg_lines[0].strip().split()
            loadavg['loadavg_1min'] = loadavg_values[0]
            loadavg['loadavg_5min'] = loadavg_values[1]
            loadavg['loadavg_15min'] = loadavg_values[2]

        return loadavg

    def _get_fd(self):
        """
        get allocated number of fds
        """
        fd = {
            'num_used_fd': None,
        }

        try:
            with open('/proc/sys/fs/file-nr', 'rt') as f:
                fd_lines = f.readlines()
        except:
            pass
        else:
            fd_values = fd_lines[0].strip().split()
            fd['num_used_fd'] = fd_values[0]

        return fd

    def _get_procs(self):
        """
        get processes running state
        """
        procs = {
            'num_total_procs': None,
            'num_running_procs': None,
            'num_blocked_procs': None,
            'num_zombie_procs': None,
        }

        try:
            with open('/proc/stat', 'rt') as f:
                procs_lines = f.readlines()
        except:
            pass
        else:
            for line in procs_lines:
                if line.startswith('processes'):
                    procs['num_total_procs'] = line.strip().split()[1]
                if line.startswith('procs_running'):
                    procs['num_running_procs'] = line.strip().split()[1]
                if line.startswith('procs_blocked'):
                    procs['num_blocked_procs'] = line.strip().split()[1]

        # use ps command to get number of zombie processes
        try:
            ps_run = subprocess.run(['ps', '-eo', 'state', '--no-headers'], capture_output=True)
        except:
            pass
        else:
            if ps_run.returncode == 0:
                zombie_count = 0

                ps_run_lines = ps_run.stdout.decode().split('\n')
                for line in ps_run_lines:
                    if line.startswith('Z'):
                        zombie_count += 1

                procs['num_zombie_procs'] = str(zombie_count)
            else:
                pass

        return procs

    def _get_context_switch(self):
        """
        get total number of context switches
        """
        context_switch = {
            'num_context_switch': None,
        }

        try:
            with open('/proc/stat', 'rt') as f:
                context_switch_lines = f.readlines()
        except:
            pass
        else:
            for line in context_switch_lines:
                if line.startswith('ctxt'):
                    context_switch['num_context_switch'] = line.strip().split()[1]
                    break

        return context_switch
