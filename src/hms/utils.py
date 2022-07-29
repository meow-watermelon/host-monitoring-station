#!/usr/bin/env python3

import glob
import os
import re
import yaml

def get_network_interfaces():
    return [os.path.basename(dir) for dir in glob.glob('/sys/class/net/*')]

def get_disk_devices():
    return [os.path.basename(dir) for dir in glob.glob('/sys/class/block/*') if not re.match(r'^loop|^zram|^sr', os.path.basename(dir))]

def read_config(config_file):
    config = {}

    try:
        with open(config_file, 'rt') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
    except:
        pass

    return config

