from decimal import Decimal, ROUND_DOWN
import numpy as np
import struct

def floatstr(f,n):
    return str(Decimal(f).quantize(Decimal((0,(1,),-n)),rounding=ROUND_DOWN))

def binary(num):
    return ''.join(bin(ord(c)).replace('0b', '').rjust(8, '0') for c in
            struct.pack('!f', num))

def quantize(data,least_significant_digit):
    """
quantize floating point data. data is quantized using
around(scale*data)/scale, where scale is 2**bits, and bits is determined
from the least_significant_digit. For example, if
least_significant_digit=1, bits will be 4.
    """
    precision = pow(10.,-least_significant_digit)
    exp = np.log10(precision)
    if exp < 0:
        exp = int(np.floor(exp))
    else:
        exp = int(np.ceil(exp))
    bits = np.ceil(np.log2(pow(10.,-exp)))
    scale = pow(2.,bits)
    return np.around(scale*data)/scale

def splitdate(yyyymmddhh):
    """
 yyyy,mm,dd,hh = splitdate(yyyymmddhh)

 give an date string (yyyymmddhh) return integers yyyy,mm,dd,hh.
    """
    yyyy = int(yyyymmddhh[0:4])
    mm = int(yyyymmddhh[4:6])
    dd = int(yyyymmddhh[6:8])
    hh = int(yyyymmddhh[8:10])
    return yyyy,mm,dd,hh

def get_dist(lon1,lons,lat1,lats):
    """compute distances (in radians) along great circles on a sphere"""
    arg = np.sin(lat1)*np.sin(lats)+np.cos(lat1)*np.cos(lats)*np.cos(lon1-lons)
    arg = np.clip(arg,-1.,1.)
    return np.arccos(arg)

# map satellite id string to code number
# see common code table c-5
# (http://www.emc.ncep.noaa.gov/mmb/data_processing/common_tbl_c1-c5.htm#c-5)
sat_id_dict = {}
sat_id_dict['n05']=705
sat_id_dict['n06']=706
sat_id_dict['n07']=707
sat_id_dict['tirosn']=708
sat_id_dict['n08']=200
sat_id_dict['n09']=201
sat_id_dict['n10']=202
sat_id_dict['n11']=203
sat_id_dict['n12']=204
sat_id_dict['n14']=205
sat_id_dict['n15']=206
sat_id_dict['n16']=207
sat_id_dict['n17']=208
sat_id_dict['n18']=209
sat_id_dict['n19']=223
sat_id_dict['metop-a']=4
sat_id_dict['metop-b']=3
sat_id_dict['metop-c']=5
sat_id_dict['npp']=224
sat_id_dict['aqua']=784
sat_id_dict['aura']=785

# map sensor id string to code number.
# see common code table c-8
# (http://www.emc.ncep.noaa.gov/mmb/data_processing/common_tbl_c8-c14.htm#c-8)
sat_sensor_dict={}
sat_sensor_dict['amsua']=570
sat_sensor_dict['amsub']=574
sat_sensor_dict['msu']  =623
sat_sensor_dict['hirs3']=606
sat_sensor_dict['hirs4']=607
