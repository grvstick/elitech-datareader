import elitech
from .msg import (
    DataBodyRequest,
    DataBodyResponse,
)
import math
from datetime import timedelta

class TempSensor(elitech.Device):
    def get_latest(self):
        devinfo = self.get_devinfo()
        if devinfo.rec_count == 0:
            return (None, None, None)
        header = self.get_data_header(devinfo.station_no)

        page_size = 500
        data_size = 1

        page = int(math.ceil(header.rec_count * data_size / float(page_size)))
        dt = timedelta(hours=devinfo.rec_interval.hour,
                       minutes=devinfo.rec_interval.minute,
                       seconds=devinfo.rec_interval.second)


        base_time = devinfo.start_time + dt * (header.rec_count-1)

        no = header.rec_count
        try:
            self._ser.open()

            p = page - 1
            req = DataBodyRequest(devinfo.station_no, p)
            count = page_size if (p+1) * page_size <= devinfo.rec_count * data_size else (devinfo.rec_count * data_size % page_size)

            res = DataBodyResponse(count)
            self._talk(req, res)

            rec = res.records[-1]
            latest = (no, base_time, rec/10.0)

        finally:
            self._ser.close()

        return latest
