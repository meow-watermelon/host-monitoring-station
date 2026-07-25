Host-monitoring-station - systemd deployment files

This directory contains example systemd unit and timer files to run the Host Monitoring Station (HMS) services:

Files:
- hms_metrics_poller.service   - oneshot service that runs the metrics poller script
- hms_metrics_poller.timer     - timer that schedules the poller every minute and on boot
- hms_web.service              - uWSGI-based service to run the Flask web app (writes uWSGI log to /home/ericlee/Projects/hms/hms_uwsgi.log)
- hms_web-gunicorn.service     - optional Gunicorn-based service example

Pre-requisites (on the host):
- Python3 and required Python packages installed system-wide or available to the service user (flask, rrdtool Python bindings, PyYAML, markupsafe)
- uWSGI installed if using hms_web.service: sudo apt install uwsgi uwsgi-plugin-python3 or install in a virtualenv and adjust ExecStart accordingly
- rrdtool installed (system package) and RRD DB path exists

Required directories and permissions (run as root or via sudo):
sudo mkdir -p /home/ericlee/Projects/hms/rrd
sudo mkdir -p /home/ericlee/Projects/hms
sudo chown -R ericlee:ericlee /home/ericlee/Projects/hms
sudo chown -R ericlee:ericlee /home/ericlee/host-monitoring-station

Install and enable the units:
sudo cp deploy/systemd/hms_metrics_poller.service /etc/systemd/system/
sudo cp deploy/systemd/hms_metrics_poller.timer /etc/systemd/system/
sudo cp deploy/systemd/hms_web.service /etc/systemd/system/
# optionally copy the gunicorn unit if you prefer it
# sudo cp deploy/systemd/hms_web-gunicorn.service /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable --now hms_metrics_poller.timer
sudo systemctl enable --now hms_web.service

Check status and logs:
# Timer status
systemctl list-timers --all | grep hms_metrics_poller
# View poller run logs
journalctl -u hms_metrics_poller.timer -f
# View web service logs
journalctl -u hms_web.service -f
# Also uWSGI logs will be written to /home/ericlee/Projects/hms/hms_uwsgi.log

Notes:
- The poller runs every minute to match the RRD DB step.
- The units are configured to run as user 'ericlee' per your request.
- If you use a Python virtualenv for dependencies, adjust ExecStart in the .service files to point to the virtualenv's uwsgi/gunicorn/python binary.
