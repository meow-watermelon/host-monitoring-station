# Host Monitoring Station

## Intro

Host Monitoring Station(HMS) is my home-brew standalone monitoring system. This application can collect system metrics and then display graphs in a web page. HMS can ONLY monitor local host system metrics, it is NOT a distributed monitoring system. The reason why I built it is to give myself a simple and easy way to grasp system performance across several servers in my home.

HMS is a very lightweight monitoring system and can be running with minimum configuration efforts.

HMS uses [RRDtool](https://oss.oetiker.ch/rrdtool/) for local TSDB storage with [Flask](https://palletsprojects.com/p/flask/) WSGI framework for the front-end web application.

## Components

HMS is constructed by the following components:

* RRD Databases Bootstrap Utility
* System Metrics Poller
* HMS Web Application

**RRD Databases Bootstrap Utility** is a utility to help users bootstrap RRD databases schema.

**System Metrics Poller** is an application to collect system metrics and write the values to local RRDtool TSDB.

**HMS Web Application** is the front-end web application to display RRD graphs. Users can use any WSGI server to run this web application. I shipped a [uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/) configuration file that can be running directly if users would like to use uWSGI as the WSGI server.

## Package Structure

All source codes are located under the `src` directory. Please **DO NOT** change any filename or subdirectory name.

```
├── hms
│   ├── cpu.py
│   ├── disk.py
│   ├── graph.py
│   ├── __init__.py
│   ├── memory.py
│   ├── network.py
│   ├── os.py
│   └── utils.py
├── hms_bootstrap_rrd.py
├── hms_metrics_poller.py
├── hms_web.py
├── hms_web_uwsgi.ini
├── static
│   ├── config
│   │   └── hms.yaml
│   └── rrd_graph
│       └── placeholder
└── templates
    └── hms.html
```

`hms` directory is the core module package of HMS. This module includes all necessary functions and classes to collect metrics and generate RRD graphs.

`hms_bootstrap_rrd.py` is the **RRD Databases Bootstrap Utility**.

`hms_metrics_poller.py` is the **System Metrics Poller**.

`hms_web.py` is the **HMS Web Application**.

`hms_web_uwsgi.ini` is a uWSGI configuration file that can be used for running HMS web application directly.

`static` directory is a place to save HMS configuration files and RRD graphs.

`templates` directory is a place for rendering HMS web page.

## Dependencies

HMS is written in Python3.

Following Python packages are needed:

```
flask
importlib.util
markupsafe
rrdtool
uWSGI + python3 plugin[optional]
yaml
```

## Installation and Configuration

In order to make the installation and configuration easier, I did not create any 3rd-party package. Users can clone the whole repository and configure some parameters to start running HMS. All commands should be running under `src` directory.

Please follow the instructions below to set up and run HMS:

1. Clone the whole repository in a directory.
```
$ git clone https://github.com/meow-watermelon/host-monitoring-station.git
```
2. Configure the HMS configuration file `src/static/config/hms.yaml`. In this file, please define **RRD_DB_PATH** variable to a proper directory to save RRD databases. Please ignore other variables now as those might be used for future version.
3. Bootstrap RRD databases. Please use `hms_bootstrap_rrd.py` utility to bootstrap the RRD databases. Usage:
```
$ ./hms_bootstrap_rrd.py -h
usage: hms_bootstrap_rrd.py [-h] --dir DIR [--step STEP]

Host Monitoring Station RRD Database Bootstrap Tool

options:
  -h, --help   show this help message and exit
  --dir DIR    RRD database directory
  --step STEP  RRD database step (default: 1m)
```
The default RRD database step is 1 minute. It s a recommended value in HMS. Please do not change this unless you know what you are doing. Collecting and writing metrics every minute is reasonable for a local monitoring system.

4. Set up the system metrics poller. The poller completes collecting metrics and writing values to RRD databases in a running cycle. Usage:
```
$ ./hms_metrics_poller.py -h
usage: hms_metrics_poller.py [-h] --config CONFIG

Host Monitoring Station Metrics Poller

options:
  -h, --help       show this help message and exit
  --config CONFIG  Host Monitoring Station config file
```
The time period between each polling **MUST** match the step defined in the bootstrap step. For example, if the step of RRD databases is 1 minute then the metrics poller must be triggered every minute. Here is an example of how I run the poller in a bash terminal:
```
while true; do ./hms_metrics_poller.py --config static/config/hms.yaml; sleep 60; done
```
5. Set up RRD graphs retention policy. RRD graphs are generated in real-time and will be only used once. So it does not make sense to save all RRD graphs because the graphs are useless once the graphs are displayed in HMS web application. Users can simply use cron to trigger the deletion based on the graph files modification time. Here is an example of crontab I use on my laptop:
```
* * * * * find /home/ericlee/Projects/git/host-monitoring-station/src/static/rrd_graph -type f -name '*.png' -mmin +1 -exec rm -rf '{}' \;
```
6. Once the metrics poller is running, the RRD databases will have system metrics stored in the RRD TSDB and can be displayed in the HMS web application. All RRD graphs are in PNG format. The default HTTP service port of HMS web application is **4080** and web server stats port is **4081**. Users can adjust those parameters in `hms_web_uwsgi.ini` file. To start the HMS web application please run the following command under `src` directory:
```
$ uwsgi hms_web_uwsgi.ini
```
Once the HMS web application started, users can access the metrics graph via <http://127.0.0.1:4080/hms>. The default graph size is 900 x 300 pixels and display last 8 hours metrics. Users can query the historical data and display different graph size by using different URL query parameters. This will be covered by following section. 

## HMS Web Application Query Parameters

HMS web application supports 3 query parameters:

**size**: RRD graph size. The default one is **medium** size which is 900 x 300 pixels. There are also **small** and **large** which are 600 x 200 pixels and 1200 x 400 pixels. 

**start**: RRD query start timestamp. The default is **end-8h** which is past 8 hours from the current time.

**end**: RRD query end timestamp. The default is **now** which is the current time.

For more information about start and end keywords please read the [rrdgraph manual](https://oss.oetiker.ch/rrdtool/doc/rrdgraph.en.html#OPTIONS).

## Metrics List

| Category | Metric Name | Unit | Description |
| --- | --- | --- | --- |
| OS | loadavg_1min | n/a | 1 min load average |
| OS | loadavg_5min | n/a | 5 min load average |
| OS | loadavg_15min | n/a | 15 min load average |
| OS | num_used_fd | count | number of occupied file descriptors |
| OS | num_total_procs | count | number of total processes |
| OS | num_running_procs | count | number of running processes |
| OS | num_blocked_procs | count | number of blocked processes (e.g. I/O blocked) |
| OS | num_zombie_procs | count | number of zombie processes |
| OS | context_switch | count/second | number of context switches per second |
| CPU | cpu_freq | kHz | cpu current running frequency |
| Memory | memory_total | kB | total memory |
| Memory | memory_free | kB | free memory |
| Memory | memory_avail | kB | available memory |
| Memory | buffer | kB | buffer |
| Memory | cache | kB | cache |
| Memory | swap_total | kB | total swap space |
| Memory | swap_free | kB | free swap space |
| Disk | read_io | count/second | number of read I/Os per second |
| Disk | write_io | count/second | number of write I/Os per second |
| Disk | read_merge | count/second | number of read I/Os merged per second |
| Disk | write_merge | count/second | number of write I/Os merged per second |
| Disk | read_sector | sector/second | number of sectors read per second |
| Disk | write_sector | sector/second | number of sectors written per second |
| Disk | in_flight | count/second | number of I/Os in flight per second |
| Network | rx_bytes | byte/second | number of good received bytes per second |
| Network | tx_bytes | byte/second | number of good transmitted bytes per second |
| Network | rx_dropped | packet/second | number of packets received but dropped per second |
| Network | tx_dropped | packet/second | number of packets dropped in transmission per second |
| Network | rx_errors | packet/second | number of bad packets received per second |
| Network | tx_errors | packet/second | number of bad packets transmitted per second |
| Network | collisions | count/second | number of I/Os in flight per second |

## Screenshots

I saved some example screenshots in the `screenshots` directory for reference.

## Known Issues and Thoughts

* UI is ugly! I know that and I'm really not a UI/UX expert.
* No logs so far for all applications. I will add a logging facility in the next version.
* I would add more metrics in the future version but the current metrics are pretty sufficient for my own use. If you have any suggestions on metrics please open a bug to me.
* Better exception handling. The current version swallowed some exceptions to make the application run smoothly. I may write some customized exception classes in the future version for better debugging purposes.
* If a new disk device or network interface is added into the host the graph won't display metrics of the newly added devices. Because the current version does not support dynamic data sources adjustment. This feature will be added soon.
