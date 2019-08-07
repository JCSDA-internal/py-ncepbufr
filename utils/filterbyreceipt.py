import ncepbufr, sys, os
import numpy as np
filename = sys.argv[1]
filenameref = sys.argv[2]
filenameo = sys.argv[3]
try:
    # if filenameref is a file, determine receipt_time_cutoff
    # by looking for newest receipt time in the file.
    bufr = ncepbufr.open(filenameref)
    receipt_time_cutoff = -1
    while bufr.advance() == 0: # loop over messages.
        if bufr.receipt_time > receipt_time_cutoff:
            receipt_time_cutoff=bufr.receipt_time
    bufr.close()
except IOError:
    # if filenameref is not a file, assume it's a specified
    # receipt time cutoff.
    receipt_time_cutoff = int(filenameref)
print('receipt time cutoff = %s' % receipt_time_cutoff)
if filenameo == filename or filenameo == filenameref:
    msg="output file must not have same name as input file"
    raise SystemExit(msg)
bufr = ncepbufr.open(filename)
bufrout = ncepbufr.open(filenameo,'w',bufr)
nmsg=0; nmsgo=0
receipt_times=[]
while bufr.advance() == 0: # loop over messages.
    if bufr.receipt_time != -1 and  bufr.receipt_time > receipt_time_cutoff:    
        # keep this bufr message, write out to file.
        bufrout.copy_message(bufr)
        receipt_times.append(bufr.receipt_time)
        nmsgo+=1
    nmsg+=1
print('%s messages (out of %s) written to %s' % (nmsgo,nmsg,filenameo))
receipt_times=np.array(receipt_times)
if nmsgo: print('min/max receipt time: %s %s' % (receipt_times.min(), receipt_times.max()))
bufr.close()
bufrout.close()
