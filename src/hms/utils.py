#!/usr/bin/env python3

import glob
import os
import re
import rrdtool
import socket
import yaml


def get_hostname_fqdn():
    """
    get local hostname FQDN
    """
    return socket.getfqdn()

def get_network_interfaces():
    """
    get network interface list
    """
    return [os.path.basename(dir) for dir in glob.glob("/sys/class/net/*")]


def get_disk_devices():
    """
    get disk device list
    """
    return [
        os.path.basename(dir)
        for dir in glob.glob("/sys/class/block/*")
        if not re.match(r"^loop|^zram|^sr", os.path.basename(dir))
    ]


def get_rrd_ds(rrd_filename):
    """
    get data source list from RRD database. used for populating dynamic generating data sources
    """
    ds = []

    rrd_info = rrdtool.info(rrd_filename)

    for key in rrd_info:
        if key.startswith("ds"):
            device_name = re.search(r"^ds\[(.*)\].*", key).group(1)
            if device_name not in ds:
                ds.append(device_name)

    return sorted(ds)


def rotate_color_plate(items, color_plate):
    """
    build color plate list for dynamic generating legends
    """
    final_color_plate = []

    rotate_count, extra_color_count = divmod(len(items), len(color_plate))
    final_color_plate = rotate_count * color_plate + color_plate[0:extra_color_count]

    return final_color_plate


def read_config(config_file):
    """
    read YAML format configuration file
    """
    config = {}

    try:
        with open(config_file, "rt") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
    except:
        pass

    return config
