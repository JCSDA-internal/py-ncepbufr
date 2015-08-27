import ncepbufr
hdstr='SID XOB YOB DHR TYP ELV SAID T29'
#hdstr2='TYP SAID T29 SID'
obstr='POB QOB TOB ZOB UOB VOB PWO MXGS HOVI CAT PRSS TDO PMO'
qcstr='PQM QQM TQM ZQM WQM NUL PWQ PMQ'
oestr='POE QOE TOE NUL WOE NUL PWE     '
mxlv = 255
lunit = 7
missval = 1.e11
# open bufr file
ncepbufr.openbf('prepbufr',lunit,'IN',lunit)
# set date length
ncepbufr.datelen(10)
# dump bufr table
ncepbufr.dxdump('prepbufr.table',lunit,lunit+1)
# loop over messages
nmsg = 0
while 1:
    subset, idate, iret = ncepbufr.readmg(lunit)
    if iret != 0: break
    nmsg += 1
    print 'nmsg, subset, date =',nmsg, subset, idate
    # loop reports in message
    while (ncepbufr.ireadsb(lunit) == 0):
        hdr,ilevs = ncepbufr.ufbint(lunit,len(hdstr.split()),1,hdstr)
        station_id = hdr[0].tostring()
        obs, ilevs = ncepbufr.ufbint(lunit,len(obstr.split()),mxlv,obstr)
        oer, ilevs = ncepbufr.ufbint(lunit,len(oestr.split()),mxlv,oestr)
        qcf, ilevs = ncepbufr.ufbint(lunit,len(qcstr.split()),mxlv,qcstr)
        print 'station_id, lon, lat, time, station_type, levels =',\
        station_id,hdr[1].item(),hdr[2].item(),hdr[3].item(),int(hdr[4].item()),ilevs
        #for k in xrange(ilevs):
        #    print 'level',k+1
        #    print 'obs',obs[:,k]
        #    print 'oer',oer[:,k]
        #    print 'qcf',qcf[:,k]
