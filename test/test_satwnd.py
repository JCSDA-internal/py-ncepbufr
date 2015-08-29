import ncepbufr

hdrstr = 'SAID CLAT CLON YEAR MNTH DAYS HOUR MINU SWCM SAZA GCLONG SCCF SWQM' 
obstr = 'HAMD PRLC WDIR WSPD' 
qcstr = 'OGCE GNAP PCCF'

# read satellite wind file.

bufr = ncepbufr.open('../test/satwndbufr')
bufr.print_table()
while bufr.advance() == 0:
    print bufr.msg_counter, bufr.msg_type, bufr.msg_date
    while bufr.load_subset() == 0:
        hdr = bufr.read_subset(hdrstr)
        yyyymmddhh ='%04i%02i%02i%02i%02i' % tuple(hdr[3:8])
        satid = int(hdr[0].item())
        windtype = int(hdr[8].item())
        lat = hdr[1].item(); lon = hdr[2].item()
        qm = hdr[12].item()
        obdata = bufr.read_subset(obstr)
        print 'satid, wind type, lat, lon, press, qcflg, time, speed, dir =',\
        satid,windtype,lat,lon,obdata[1].item(),qm,yyyymmddhh,obdata[3].item(),obdata[2].item()
    # only loop over first 4 subsets
    if bufr.msg_counter == 4: break
bufr.close()
