import ncepbufr
import struct
hdstr='SID XOB YOB DHR TYP ELV SAID T29'
obstr='POB QOB TOB ZOB UOB VOB PWO CAT PRSS'
qcstr='PQM QQM TQM ZQM WQM NUL PWQ     '
oestr='POE QOE TOE NUL WOE NUL PWE     '
mxmn = 35; mxlv = 250
lunit = 7
# open bufr file
ncepbufr.openbf('prepbufr',lunit,'IN',lunit)
# set date length
ncepbufr.datelen(10)
# dump bufr table
ncepbufr.dxdump('prepbufr.table',lunit,lunit+1)
subset, idate, iret = ncepbufr.readmg(lunit)
if iret == 0:
    print 'subset, date =',subset, idate
else:
    raise ValueError('nonzero return code = %s from readmg' % iret)
iret = ncepbufr.ireadsb(lunit)
if iret == 0:
    hdr,iret = ncepbufr.ufbint(lunit,mxmn,1,hdstr)
    station_id = hdr[0].tostring()
    print 'station_id, lon, lat, time, station_type =',\
    station_id,hdr[1].item(),hdr[2].item(),hdr[3].item(),int(hdr[4].item())
