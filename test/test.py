from __future__ import print_function
import ncepbufr
import numpy as np

hdstr='SID XOB YOB DHR TYP ELV SAID T29'
obstr='POB QOB TOB ZOB UOB VOB PWO MXGS HOVI CAT PRSS TDO PMO'
qcstr='PQM QQM TQM ZQM WQM NUL PWQ PMQ'
oestr='POE QOE TOE NUL WOE NUL PWE'

# read prepbufr file.
bufr = ncepbufr.open('data/prepbufr')
while bufr.advance() == 0: # loop over messages.
    while bufr.load_subset() == 0: # loop over subsets in message.
        hdr = bufr.read_subset(hdstr).squeeze()
        station_id = hdr[0].tostring()
        lon = hdr[1]; lat = hdr[2]
        station_type = int(hdr[4])
        obs = bufr.read_subset(obstr)
        nlevs = obs.shape[-1]
        oer = bufr.read_subset(oestr)
        qcf = bufr.read_subset(qcstr)
    # stop after first 2 messages.
    if bufr.msg_counter == 2: break
# check data
# station_id,lon,lat,time,station_type,nlevs
assert station_id.rstrip() == b'91925'
np.testing.assert_almost_equal(lon,220.97)
np.testing.assert_almost_equal(lat,-9.8)
assert station_type == 220
assert nlevs == 41
obs_str = '%s' % obs[:,-1]
oer_str = '%s' % oer[:,-1]
qc_str = '%s' % qcf[:,-1]
assert obs_str ==\
       '[19.0 -- -- -- -11.200000000000001 5.2 -- -- -- 3.0 -- -- --]'
assert oer_str == \
       '[-- -- -- -- 2.1 -- --]'
assert qc_str == \
       '[2.0 -- -- -- 2.0 -- -- --]'
#  91925    220.97 -9.8 0.0 220 41
# obs [19.0 -- -- -- -11.200000000000001 5.2 -- -- -- 3.0 -- -- --]
# oer [-- -- -- -- 2.1 -- --]
# qcf [2.0 -- -- -- 2.0 -- -- --]
bufr.close()
