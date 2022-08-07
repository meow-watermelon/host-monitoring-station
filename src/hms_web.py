#!/usr/bin/env python3

import importlib.util
import os
import rrdtool
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

    # retrieve the default start / end time and graph size
    default_start = g.config["RRD_GRAPH_DEFAULT_START"]
    default_end = g.config["RRD_GRAPH_DEFAULT_END"]
    default_size = g.config["RRD_GRAPH_DEFAULT_SIZE"]

    if not start:
        start = default_start
    if not end:
        end = default_end
    if not size:
        size = default_size

    # issue#1
    # apply default start / end time if the range is not valid
    try:
        rrdtool.graph(
            "--start", start,
            "--end", end,
        )
    except rrdtool.OperationalError:
        start = default_start
        end = default_end

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
    g.disk_graph_filename = hms_graph.plot_disk_graph()
    g.memory_swap_graph_filename = hms_graph.plot_memory_graph()
    g.network_graph_filename = hms_graph.plot_network_graph()
    g.os_graph_filename = hms_graph.plot_os_graph()

    # render HMS web page

    return render_template(
        "hms.html",
        hostname=g.hostname,
        disk_read_io=g.disk_graph_filename["read_io"],
        disk_write_io=g.disk_graph_filename["write_io"],
        disk_read_sector=g.disk_graph_filename["read_sector"],
        disk_write_sector=g.disk_graph_filename["write_sector"],
        disk_read_merge=g.disk_graph_filename["read_merge"],
        disk_write_merge=g.disk_graph_filename["write_merge"],
        disk_in_flight=g.disk_graph_filename["in_flight"],
        memory_memory=g.memory_swap_graph_filename["memory"],
        memory_swap=g.memory_swap_graph_filename["swap"],
        network_rx_bytes=g.network_graph_filename["rx_bytes"],
        network_tx_bytes=g.network_graph_filename["tx_bytes"],
        network_rx_dropped=g.network_graph_filename["rx_dropped"],
        network_tx_dropped=g.network_graph_filename["tx_dropped"],
        network_rx_errors=g.network_graph_filename["rx_errors"],
        network_tx_errors=g.network_graph_filename["tx_errors"],
        network_collisions=g.network_graph_filename["collisions"],
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
