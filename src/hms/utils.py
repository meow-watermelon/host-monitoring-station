#!/usr/bin/env python3

import glob
import os
import re
import rrdtool
import yaml


def get_network_interfaces():
    return [os.path.basename(dir) for dir in glob.glob("/sys/class/net/*")]


def get_disk_devices():
    return [
        os.path.basename(dir)
        for dir in glob.glob("/sys/class/block/*")
        if not re.match(r"^loop|^zram|^sr", os.path.basename(dir))
    ]


def get_rrd_ds(rrd_filename):
    ds = []

    rrd_info = rrdtool.info(rrd_filename)

    for key in rrd_info:
        if key.startswith("ds"):
            device_name = re.search(r"^ds\[(.*)\].*", key).group(1)
            if device_name not in ds:
                ds.append(device_name)

    return sorted(ds)


def rotate_color_plate(items, color_plate):
    final_color_plate = []

    rotate_count, extra_color_count = divmod(len(items), len(color_plate))
    final_color_plate = rotate_count * color_plate + color_plate[0:extra_color_count]

    return final_color_plate


def read_config(config_file):
    config = {}

    try:
        with open(config_file, "rt") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
    except:
        pass

    return config
