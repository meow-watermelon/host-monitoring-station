    def _create_rrd_with_devices(self, rrd_filename, devices, rrd_step):
        """
        Create a new RRD file with the specified devices.
        """
        data_sources = [f"DS:{device}:GAUGE:300:0:U" for device in devices]
        rrdtool.create(
            rrd_filename,
            "--step",
            str(rrd_step),
            *data_sources,
            f"RRA:AVERAGE:0.5:{rrd_step}:1y",
            f"RRA:LAST:0.5:{rrd_step}:1y",
        )
