from __future__ import print_function
import ncepbufr, sys
import numpy as np

hdstr='RCYR RCMO RCDY RCHR RCMI'
hdstr2='RSRD EXPRSRD'

def get_receipt_times(bufr):
    receipt_times = []
    while bufr.advance() == 0: # loop over messages.
        receipt_time_msg = int(bufr.receipt_time)
        while bufr.load_subset() == 0: # loop over subsets in message.
            hdr1 = bufr.read_subset(hdstr)
            receipt_time_subset = 0
            for nlev in range(hdr1.shape[1]):
               nlevp1=nlev+1
               rtime = int('%04i%02i%02i%02i%02i' % (hdr1[0,nlev],hdr1[1,nlev],hdr1[2,nlev],hdr1[3,nlev],hdr1[4,nlev]))
               if rtime > receipt_time_subset: receipt_time_subset=rtime
            if receipt_time_subset > 0:
                receipt_times.append(receipt_time_subset)
            else:
                receipt_times.append(receipt_time_msg)
    receipt_times=np.array(receipt_times)
    indx = receipt_times > 0
    if indx.any():
        print('%s out of %s subsets have receipt times, min %s max %s' % (indx.sum(), len(receipt_times), receipt_times[indx].min(), receipt_times[indx].max()))
    else:
        print('ERROR:  No receipt times in this bufr file!')
        raise SystemExit
    return receipt_times

filename = sys.argv[1]
filenameref = sys.argv[2]
filenameo = sys.argv[3]

try:
    # if filenameref is a file, determine receipt_time_cutoff
    # by looking for newest receipt time in the file.
    bufr = ncepbufr.open(filenameref)
    print(filenameref)
    receipt_times = get_receipt_times(bufr)
    bufr.close()
    receipt_time_cutoff = receipt_times.max()
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

nsubs=0; nsubso=0; nskip=0; nskip2=0
print(filename)
receipt_times=get_receipt_times(bufr)
bufr.rewind()
while bufr.advance() == 0: # loop over messages.
    bufrout.open_message(bufr.msg_type,bufr.msg_date) # open message
    while bufr.load_subset() == 0: # loop over subsets in message.
        hdr = (bufr.read_subset(hdstr2).squeeze()).filled(0)
        try:
            rsrd = int(hdr[0]); exprsrd = int(hdr[1])
        except:
            rsrd = 0; exprsrd = 0
        if receipt_times[nsubs] > receipt_time_cutoff:    
            rs_bitstring =  "{0:b}".format(rsrd)
            # skip restricted data with no expiration time
            if rsrd == 0 or exprsrd > 0 : 
                # keep this bufr subset, write out to file.
                bufrout.copy_subset(bufr)
                nsubso+=1
            else:
                nskip += 1
                #print('skipping ob with restricted data flags %s' % rs_bitstring[0:5])
        else:
            nskip2+=1
        nsubs+=1

print('%s subsets (out of %s) written to %s' % (nsubso,nsubs,filenameo))
if nskip: print('%s obs skipped due to use restrictions' % nskip)
if nskip2: print('%s obs skipped due to receipt time missing or < cutoff' % nskip2)
bufr.close()
bufrout.close()
