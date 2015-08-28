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

hdstr1 ='SAID SIID FOVN YEAR MNTH DAYS HOUR MINU SECO CLAT CLON CLATH CLONH HOLS'
hdstr2 ='SAZA SOZA BEARAZ SOLAZI'

# read radiance file.

bufr = ncepbufr.open('../test/1bamua')
bufr.print_table()
print_data = True
for subset in bufr:
    print bufr.subset_counter, bufr.subset_type, bufr.subset_date
    while (bufr.load_subset() == 0):
        hdr1 = bufr.read_subset(hdstr1)
        hdr2 = bufr.read_subset(hdstr2)
        yyyymmddhhss ='%04i%02i%02i%02i%02i%02i' % tuple(hdr1[3:9])
        # for satellite id, see common code table c-5
        # (http://www.emc.ncep.noaa.gov/mmb/data_processing/common_tbl_c1-c5.htm#c-5)
        # for sensor id, see common code table c-8
        # (http://www.emc.ncep.noaa.gov/mmb/data_processing/common_tbl_c8-c14.htm#c-8)
        print 'sat id,sensor id lat, lon, yyyymmddhhmmss =',int(hdr1[0].item()),\
        int(hdr1[1].item()),hdr1[9].item(),hdr1[10].item(),yyyymmddhhss
        if print_data: # print data from first subset with data
            obs = bufr.read_subset('TMBR',pivot=True)
            nchanl = obs.shape[-1]
            for k in xrange(nchanl):
                print 'channel, tb =',k+1,obs[0,k]
            print_data = False
bufr.close()
