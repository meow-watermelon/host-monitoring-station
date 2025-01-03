#!/usr/bin/env python3

import importlib.util
import os
import sys
import uuid
from flask import Flask, render_template, request, g
from markupsafe import escape

# load host monitoring station module - hms
spec = importlib.util.spec_from_file_location("hms", f"{os.getcwd()}/hms/__init__.py")
hms = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = hms
spec.loader.exec_module(hms)

app = Flask(__name__)


@app.route("/hms", methods=["GET"])
def hms_load_graphs():
    # process query parameters
    start = request.args.get("start")
    end = request.args.get("end")
    size = request.args.get("size")

    if not start:
        start = "end-8h"
    if not end:
        end = "now"
    if not size:
        size = "medium"

    # exam start and end time range, set up to default value if not valid
    if not hms.utils.test_rrd_time_range(start, end):
        start = "end-8h"
        end = "now"

    # construct graph object
    hms_graph = hms.graph.Graph(
        g.config["RRD_DB_PATH"],
        "static/rrd_graph",
        str(escape(size)),
        str(escape(start)),
        str(escape(end)),
        g.uuid,
    )

    # plot graphs and retrieve graph filename mappings
    g.cpu_graph_filename = hms_graph.plot_cpu_graph()
    g.disk_graph_filename = hms_graph.plot_disk_graph()
    g.memory_swap_graph_filename = hms_graph.plot_memory_graph()
    g.network_graph_filename = hms_graph.plot_network_graph()
    g.tcp_graph_filename = hms_graph.plot_tcp_graph()
    g.udp_graph_filename = hms_graph.plot_udp_graph()
    g.os_graph_filename = hms_graph.plot_os_graph()
    g.arp_graph_filename = hms_graph.plot_arp_graph()

    # render HMS web page

    return render_template(
        "hms.html",
        hostname=g.hostname,
        cpu_cpu_freq=g.cpu_graph_filename["cpu_freq"],
        disk_read_io=g.disk_graph_filename["read_io"],
        disk_write_io=g.disk_graph_filename["write_io"],
        disk_read_sector=g.disk_graph_filename["read_sector"],
        disk_write_sector=g.disk_graph_filename["write_sector"],
        disk_read_merge=g.disk_graph_filename["read_merge"],
        disk_write_merge=g.disk_graph_filename["write_merge"],
        disk_in_flight=g.disk_graph_filename["in_flight"],
        memory_memory=g.memory_swap_graph_filename["memory"],
        memory_swap=g.memory_swap_graph_filename["swap"],
        memory_virtual=g.memory_swap_graph_filename["virtual"],
        network_rx_bytes=g.network_graph_filename["rx_bytes"],
        network_tx_bytes=g.network_graph_filename["tx_bytes"],
        network_rx_dropped=g.network_graph_filename["rx_dropped"],
        network_tx_dropped=g.network_graph_filename["tx_dropped"],
        network_rx_errors=g.network_graph_filename["rx_errors"],
        network_tx_errors=g.network_graph_filename["tx_errors"],
        network_collisions=g.network_graph_filename["collisions"],
        tcp_tcp=g.tcp_graph_filename["tcp"],
        tcp_tcp6=g.tcp_graph_filename["tcp6"],
        udp_udp=g.udp_graph_filename["udp"],
        arp_arp=g.arp_graph_filename["arp"],
        os_loadavg=g.os_graph_filename["loadavg"],
        os_fd=g.os_graph_filename["fd"],
        os_procs=g.os_graph_filename["procs"],
        os_context_switch=g.os_graph_filename["context_switch"],
    )


@app.before_request
def before_request():
    g.uuid = str(uuid.uuid4())
    g.config = hms.utils.read_config("static/config/hms.yaml")
    g.hostname = hms.utils.get_hostname_fqdn()
