from __future__ import print_function
import ncepbufr
import numpy as np

hdstr='SID XOB YOB DHR TYP ELV SAID T29'
obstr='POB QOB TOB ZOB UOB VOB PWO MXGS HOVI CAT PRSS TDO PMO'
qcstr='PQM QQM TQM ZQM WQM NUL PWQ PMQ'
oestr='POE QOE TOE NUL WOE NUL PWE     '

# open prepbufr file.

bufr = ncepbufr.open('prepbufr2','w',table='prepbufr.table')
idate=2010050700 # cycle time: YYYYMMDDHH
subset='ADPSFC'  # surface land (SYNOPTIC, METAR) reports
bufr.create_message(subset, idate)

hdr = np.empty(len(hdstr.split()),np.float)
hdr[:]=1.e11 # set all values to missing
hdr[0] = np.fromstring('KTKI    ',dtype=np.float)[0]
hdr[1]=263.4; hdr[2]=33.2; hdr[3] = -0.1; hdr[4]=287; hdr[5]=179
# encode header for wind obs
bufr.write_subset(hdr,hdstr)
# set obs, qcf, oer for  wind
obs = np.empty(len(obstr.split()),np.float)
oer = np.empty(len(oestr.split()),np.float)
qcf = np.empty(len(qcstr.split()),np.float)
obs[:]=1.e11; qcf[:]=1.e11; oer[:]=1.0e11
obs[0]=985.2; obs[4]=-2.8; obs[5]=-7.7; obs[7]=6.0
qcf[0]=2.0  ; qcf[4]=2.0; oer[4] = 1.6
# encode wind obs
bufr.write_subset(obs,obstr)
# encode wind ob err
bufr.write_subset(oer,oestr)
# encode quality flags, end subset.
bufr.write_subset(qcf,qcstr,end=True)
# set obs, qcf, oer for  temperature and moisture
hdr[4]=187          # report type
# encode header
bufr.write_subset(hdr,hdstr)
obs[:]=1.e11; qcf[:]=1.e11; oer[:]=1.0e11
obs[0]=985.2;obs[1]=12968.0;obs[2]=31.3;obs[3]=179.0;obs[7]=0.0
qcf[0]=2.0  ;qcf[1]=2.0    ;qcf[2]=2.0 ;qcf[3]=2.0
oer[0]=0.5  ;oer[1]=0.6    ;oer[2]=2.3
# encode temperature and moisture obs, obs err and qc flags.
bufr.write_subset(obs,obstr)
bufr.write_subset(oer,oestr)
bufr.write_subset(qcf,qcstr,end=True) # end subset
# close bufr message
bufr.close_message()
# close bufr file
bufr.close()

# read prepbufr file back in.

bufr = ncepbufr.open('prepbufr2')
bufr.print_table() # print embedded table
while bufr.advance() == 0: # loop over messages.
    print(bufr.msg_counter, bufr.msg_type, bufr.msg_date)
    while bufr.load_subset() == 0: # loop over subsets in message.
        hdr = bufr.read_subset(hdstr)
        station_id = hdr[0].tostring()
        obs = bufr.read_subset(obstr)
        nlevs = obs.shape[-1]
        oer = bufr.read_subset(oestr)
        qcf = bufr.read_subset(qcstr)
        print('station_id, lon, lat, time, station_type, levels =',\
        station_id,hdr[1].item(),hdr[2].item(),hdr[3].item(),int(hdr[4].item()),nlevs)
        for k in range(nlevs):
            print('obs',obs[:,k])
            print('oer',oer[:,k])
            print('qcf',qcf[:,k])
bufr.close()
