import ncepbufr
lunit = 7
# open bufr file
ncepbufr.openbf('prepbufr',lunit,'IN',lunit)
# set date length
ncepbufr.datelen(10)
# dump bufr table
ncepbufr.dxdump('prepbufr.table',lunit,lunit+1)
subset, idate, iret = ncepbufr.readmg(lunit)
print subset
print idate
print iret
