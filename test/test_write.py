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
bufr.open_message(subset, idate)

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
# create a message with upper-air (raob) data.
subset='ADPUPA'  # upper-air (raob, drops) reports
bufr.open_message(subset, idate)

# set header
hdr[:]=1.e11
hdr[0] = np.fromstring('72293   ',dtype=np.float)[0]
hdr[1]=242.9; hdr[2]=32.9; hdr[3]=0.0; hdr[5]=134.0

# set obs, qcf, oer for  wind
nlvl=3
hdr[4]=220          # report type: sounding 
obs = np.empty((len(obstr.split()),nlvl),np.float)
oer = np.empty((len(oestr.split()),nlvl),np.float)
qcf = np.empty((len(qcstr.split()),nlvl),np.float)
obs[:]=1.e11;qcf[:]=1.e11;oer[:]=1.e11
obs[0,0]=998.0; obs[4,0]=4.6 ;obs[5,0]=2.2 ;obs[7,0]=3.0
qcf[0,0]=2.0  ; qcf[4,0]=2.0
oer[4,0]=2.3
obs[0,1]=850.0; obs[4,1]=2.0 ;obs[5,1]=-1.7;obs[7,1]=1.0
qcf[0,1]=2.0  ; qcf[4,1]=2.0
oer[4,1]=2.6
obs[0,2]=700.0; obs[4,2]=12.1;obs[5,2]=-4.4;obs[7,2]=1.0
qcf[0,2]=2.0  ; qcf[4,2]=2.0
oer[4,2]=2.5
# encode  wind obs
bufr.write_subset(hdr,hdstr)
bufr.write_subset(obs,obstr)
bufr.write_subset(oer,oestr)
bufr.write_subset(qcf,qcstr,end=True) # end subset
# set obs, qcf, oer for  temperature and moisture
nlvl=4
obs = np.empty((len(obstr.split()),nlvl),np.float)
oer = np.empty((len(oestr.split()),nlvl),np.float)
qcf = np.empty((len(qcstr.split()),nlvl),np.float)
hdr[4]=120          # report type: sounding
obs[:]=1.0e11;qcf[:]=1.e11;oer[:]=1.e11
obs[0,0]=998.0;obs[1,0]=8112.0;obs[2,0]=22.3;obs[3,0]=134.0;obs[7,0]=0.0
qcf[0,0]=2.0  ;qcf[1,0]=2.0   ;qcf[2,0]=2.0 ;qcf[3,0]=2.0
oer[0,0]=0.7  ;oer[1,0]=0.7   ;oer[2,0]=1.4 
obs[0,1]=925.0;obs[1,1]=6312.0;obs[2,1]=14.1;obs[3,1]=779.0;obs[7,1]=1.0
qcf[0,1]=2.0  ;qcf[1,1]=2.0   ;qcf[2,1]=2.0 ;qcf[3,1]=2.0
oer[1,1]=0.9   ;oer[2,1]=1.5 
obs[0,2]=850.0;obs[1,2]=2161.0;obs[2,2]=14.8;obs[3,2]=1493.;obs[7,2]=1.0
qcf[0,2]=2.0  ;qcf[1,2]=2.0   ;qcf[2,2]=2.0 ;qcf[3,2]=2.0
oer[1,2]=1.1   ;oer[2,2]=1.4 
obs[0,3]=700.0;obs[1,3]=2131.0;obs[2,3]=9.2 ;obs[3,3]=3118.;obs[7,3]=1.0
qcf[0,3]=2.0  ;qcf[1,3]=2.0   ;qcf[2,3]=2.0 ;qcf[3,3]=2.0
oer[1,3]=1.4   ;oer[2,3]=1.0 
# encode temperature and moisture
bufr.write_subset(hdr,hdstr)
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
            if nlevs > 1:
                print('level =',k+1)
            print('obs',obs[:,k])
            print('oer',oer[:,k])
            print('qcf',qcf[:,k])
bufr.close()
