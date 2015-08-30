from __future__ import print_function
import ncepbufr

hdstr='SID XOB YOB DHR TYP ELV SAID T29'
obstr='POB QOB TOB ZOB UOB VOB PWO MXGS HOVI CAT PRSS TDO PMO'
qcstr='PQM QQM TQM ZQM WQM NUL PWQ PMQ'
oestr='POE QOE TOE NUL WOE NUL PWE     '

# open prepbufr file.

bufr = ncepbufr.open('prepbufr2','w',table='prepbufr.table')
idate=2010050700 # cycle time: YYYYMMDDHH
subset='ADPSFC'  # surface land (SYNOPTIC, METAR) reports
bufr.create_message(subset, idate)

hdr = np.empty(len(hdstring.split()),np.float)
hdr=1.e11 # set all values to missing
hdr[1]=263.4; hdr[2]=33.2; hdr[3] = -0.1; hdr[5]=179.0
levs = bufr.write_subset(hdr,hdrstr)
#! set headers
#      hdr=10.0e10
#      c_sid='KTKI'; hdr(1)=rstation_id
#      hdr(2)=263.4; hdr(3)=33.2; hdr(4)=-0.1; hdr(6)=179.0
#
#! set obs, qcf, oer for  wind
#      hdr(5)=287          ! report type
#      obs=10.0e10;qcf=10.0e10;oer=10.0e10
#      obs(1,1)=985.2; obs(5,1)=-2.8; obs(6,1)=-7.7; obs(8,1)=6.0
#      qcf(1,1)=2.0  ; qcf(5,1)=2.0
#      oer(5,1)=1.6
#! encode  wind obs
#      call ufbint(unit_out,hdr,mxmn,1   ,iret,hdstr)
#      call ufbint(unit_out,obs,mxmn,mxlv,iret,obstr)
#      call ufbint(unit_out,oer,mxmn,mxlv,iret,oestr)
#      call ufbint(unit_out,qcf,mxmn,mxlv,iret,qcstr)
#      call writsb(unit_out)
#
#! set obs, qcf, oer for  temperature and moisture
#      hdr(5)=187          ! report type
#      obs=10.0e10;qcf=10.0e10;oer=10.0e10
#      obs(1,1)=985.2;obs(2,1)=12968.0;obs(3,1)=31.3;obs(4,1)=179.0;obs(8,1)=0.0
#      qcf(1,1)=2.0  ;qcf(2,1)=2.0    ;qcf(3,1)=2.0 ;qcf(4,1)=2.0
#      oer(1,1)=0.5  ;oer(2,1)=0.6    ;oer(3,1)=2.3
#! encode temperature and moisture
#      call ufbint(unit_out,hdr,mxmn,1   ,iret,hdstr)
#      call ufbint(unit_out,obs,mxmn,mxlv,iret,obstr)
#      call ufbint(unit_out,oer,mxmn,mxlv,iret,oestr)
#      call ufbint(unit_out,qcf,mxmn,mxlv,iret,qcstr)
#      call writsb(unit_out)
#
#   call closmg(unit_out)
# call closbf(unit_out)
