import ncepbufr

hdstr='SID XOB YOB DHR TYP ELV SAID T29'
obstr='POB QOB TOB ZOB UOB VOB PWO MXGS HOVI CAT PRSS TDO PMO'
qcstr='PQM QQM TQM ZQM WQM NUL PWQ PMQ'
oestr='POE QOE TOE NUL WOE NUL PWE     '

# read prepbufr file.

bufr = ncepbufr.open('prepbufr')
bufr.print_table()
for subset in bufr:
    print bufr.subset_counter, bufr.subset_type, bufr.subset_date
    #bufr.read_subset(obstr) # should raise subset not loaded error
    while (bufr.load_subset() == 0):
        hdr = bufr.read_subset(hdstr)
        station_id = hdr[0].tostring()
        obs = bufr.read_subset(obstr)
        nlevs = obs.shape[-1]
        oer = bufr.read_subset(oestr)
        qcf = bufr.read_subset(qcstr)
        print 'station_id, lon, lat, time, station_type, levels =',\
        station_id,hdr[1].item(),hdr[2].item(),hdr[3].item(),int(hdr[4].item()),nlevs
        if bufr.subset_counter == 1: # print data from first subset
            for k in xrange(nlevs):
                print 'level',k+1
                print 'obs',obs[:,k]
                print 'oer',oer[:,k]
                print 'qcf',qcf[:,k]
bufr.close()
