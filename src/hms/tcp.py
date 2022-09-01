#!/usr/bin/env python3


# ref.: https://github.com/torvalds/linux/blob/master/include/net/tcp_states.h
tcp_states = {
    "01": "ESTABLISHED",
    "02": "SYN_SENT",
    "03": "SYN_RECV",
    "04": "FIN_WAIT1",
    "05": "FIN_WAIT2",
    "06": "TIME_WAIT",
    "07": "CLOSE",
    "08": "CLOSE_WAIT",
    "09": "LAST_ACK",
    "0A": "LISTEN",
    "0B": "CLOSING",
    "0C": "NEW_SYN_RECV",
}


class TCP:
    def __init__(self):
        self.tcp_proc_file = "/proc/net/tcp"
        self.tcp6_proc_file = "/proc/net/tcp6"
        self.tcp = self._get_tcp()
        self.tcp6 = self._get_tcp6()

    def _get_socket_states(self, proc_filename):
        """
        get TCP socket state counts from proc file
        """
        socket_states = {}
        for _, state in tcp_states.items():
            socket_states[state] = 0

        with open(proc_filename, "rt") as f:
            for line in f.readlines():
                cols = line.split()
                if cols:
                    state = cols[3]
                    if state in tcp_states:
                        tcp_state = tcp_states[state]
                        socket_states[tcp_state] += 1

        return socket_states

    def _get_tcp(self):
        """
        get IPv4 TCP socket state information
        """
        return self._get_socket_states(self.tcp_proc_file)

    def _get_tcp6(self):
        """
        get IPv6 TCP socket state information
        """
        return self._get_socket_states(self.tcp6_proc_file)
