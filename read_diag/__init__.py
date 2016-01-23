import numpy as np
import _read_convobs
__version__ = '0.0.1'
class diag_conv(object):
    # read diag_conv file.
    def __init__(self,filename,endian='native'):
        nobs = _read_convobs.get_num_convobs(filename,endian=endian)
        self.endian = endian
        self.nobs = nobs; self.filename = filename
    def read_obs(self):
        h_x,x_obs,x_err,x_lon,x_lat,x_press,x_time,\
        x_code,x_errorig,x_type,x_use,x_station_id,x_stnelev =\
        _read_convobs.get_convobs_data(self.filename, self.nobs,\
        endian=self.endian)
        self.hx = h_x
        self.obs = x_obs
        self.oberr = x_err
        self.lon = x_lon
        self.lat = x_lat
        self.press = x_press
        self.time = x_time
        self.stnelev = x_stnelev
        self.code = x_code
        self.oberr_orig = x_errorig
        self.used = x_use
        self.obtype = \
        np.array((x_type.tostring()).replace('\x00','')[:-1].split('|'))
        self.station_ids =\
        np.array((x_station_id.tostring()).replace('\x00','')[:-1].split('|'))
