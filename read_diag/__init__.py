import numpy as np
import _read_convobs
class diag_conv(object):
    # read diag_conv file.
    def __init__(self,filename):
        nobs = _read_convobs.get_num_convobs(filename)
        self.nobs = nobs; self.filename = filename
    def read_obs(self):
        h_x,x_obs,x_err,x_lon,x_lat,x_press,x_time,\
        x_code,x_errorig,x_type,x_use,x_station_id =\
        _read_convobs.get_convobs_data(self.filename, self.nobs)
        obs_desc = []
        for n in range(self.nobs):
            s = x_type[n].tostring()
            s = s.encode('ascii').replace('\x00','').strip()
            obs_desc.append(s)
        station_ids = []
        for n in range(self.nobs):
            s = x_station_id[n].tostring()
            s = s.encode('ascii').replace('\x00','').strip()
            station_ids.append(s)
        self.hx = h_x
        self.obs = x_obs
        self.oberr = x_err
        self.lon = x_lon
        self.lat = x_lat
        self.press = x_press
        self.time = x_time
        self.code = x_code
        self.oberr_orig = x_errorig
        self.obtype = np.array(obs_desc,'S3')
        self.used = x_use
        self.station_ids = np.array(station_ids,'S8')

