from __future__ import print_function
import ncepbufr, sys
import numpy as np

hdstr='RCYR RCMO RCDY RCHR RCMI'
hdstr2='RSRD EXPRSRD'

def get_receipt_times(bufr,check_subsets=False):
    receipt_times_bysubset = []
    receipt_times_bymsg = []
    while bufr.advance() == 0: # loop over messages.
        #print(bufr.msg_counter, bufr.msg_type, bufr.msg_date, bufr.receipt_time)
        receipt_time_msg = int(bufr.receipt_time)
        rtimes=[]; no_restricted_data = True
        if check_subsets or receipt_time_msg <= 0:
            # loop over all subsets, check for receipt time and restricted data flags.
            while bufr.load_subset() == 0: # loop over subsets in message.
                hdr1 = bufr.read_subset(hdstr)
                hdr2 = (bufr.read_subset(hdstr2).squeeze()).filled(0)
                try:
                    rsrd = int(hdr2[0]); exprsrd = int(hdr2[1])
                except:
                    rsrd = 0; exprsrd = 0
                if rsrd > 0 and exprsrd == 0 : 
                   no_restricted_data = False
                receipt_time_subset = 0
                for nlev in range(hdr1.shape[1]):
                   nlevp1=nlev+1
                   rtime = int('%04i%02i%02i%02i%02i' % (hdr1[0,nlev],hdr1[1,nlev],hdr1[2,nlev],hdr1[3,nlev],hdr1[4,nlev]))
                   if rtime > receipt_time_subset: receipt_time_subset=rtime
                if receipt_time_subset > 0:
                    receipt_times_bysubset.append(receipt_time_subset)
                    rtimes.append(receipt_time_subset)
                else:
                    receipt_times_bysubset.append(receipt_time_msg)
                    rtimes.append(receipt_time_msg)
            rtimes = np.array(rtimes)
            if rtimes.size:
                rtime_min=rtimes.min(); rtime_max=rtimes.max()
            else:
                rtime_min=-1; rtime_max=-1
            if rtime_min == rtime_max and rtime_max > 0:
                receipt_times_bymsg.append((rtime_max,no_restricted_data))
            else:
                receipt_times_bymsg.append((-1,no_restricted_data))
        else:
            receipt_times_bymsg.append((receipt_time_msg,no_restricted_data))
            while bufr.load_subset() == 0: # loop over subsets in message.
                receipt_times_bysubset.append(receipt_time_msg)
    receipt_times_bysubset=np.array(receipt_times_bysubset)
    indx = receipt_times_bysubset > 0
    if indx.any():
        print('%s out of %s subsets have receipt times, min %s max %s' % (indx.sum(), len(receipt_times_bysubset), receipt_times_bysubset[indx].min(), receipt_times_bysubset[indx].max()))
    else:
        print('ERROR:  No receipt times in this bufr file!')
        raise SystemExit
    return receipt_times_bymsg, receipt_times_bysubset

filename = sys.argv[1]
filenameref = sys.argv[2]
filenameo = sys.argv[3]

try:
    receipt_time_cutoff = int(filenameref)
except ValueError:
    # if filenameref is a file, determine receipt_time_cutoff
    # by looking for newest receipt time in the file.
    bufr = ncepbufr.open(filenameref)
    if 'adpupa' in filenameref or 'sfcshp' in filenameref or \
       'adpsfc' in filenameref or 'aircar' in filenameref or \
       'saphir' in filenameref or 'gpsipw' in filenameref or \
       'aircft' in filenameref or 'gpsro' in filename:
        receipt_times_bymsg, receipt_times = get_receipt_times(bufr,check_subsets=True)
    else:
        receipt_times_bymsg, receipt_times = get_receipt_times(bufr,check_subsets=False)
    bufr.close()
    receipt_time_cutoff = receipt_times.max()
 
print('receipt time cutoff = %s' % receipt_time_cutoff)
if filenameo == filename or filenameo == filenameref:
    msg="output file must not have same name as input file"
    raise SystemExit(msg)

bufr = ncepbufr.open(filename)
bufrout = ncepbufr.open(filenameo,'w',bufr)

nsubs=0; nsubso=0; nskip=0; nskip2=0; nmsg=0; nmsgo = 0; nskip1=0
print(filename)
if 'adpupa' in filename or 'sfcshp' in filename or \
   'adpsfc' in filename or 'aircar' in filename or \
   'saphir' in filename or 'gpsipw' in filename or \
   'aircft' in filename or 'gpsro'  in filename:
    receipt_times_bymsg, receipt_times = get_receipt_times(bufr,check_subsets=True)
else:
    receipt_times_bymsg, receipt_times = get_receipt_times(bufr,check_subsets=False)
bufr.rewind()
while bufr.advance() == 0: # loop over messages.
    msg_receipt_time,no_restricted_data = receipt_times_bymsg[nmsg]
    if msg_receipt_time > 0 and no_restricted_data:
       # write entire message at once, since subsets all have same receipt time.
       if msg_receipt_time > receipt_time_cutoff:    
           bufrout.copy_message(bufr)
           nmsgo += 1
       else:
           nskip1 += 1
    else:
       # check individual subsets
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
       bufrout.close_message()
    nmsg+=1

if nsubso: print('%s subsets (out of %s) written to %s' % (nsubso,nsubs,filenameo))
if nmsgo: print('%s messages (out of %s) written to %s' % (nmsgo,nmsg,filenameo))
if nskip: print('%s obs skipped due to use restrictions' % nskip)
if nskip2: print('%s subsets skipped due to receipt time missing or < cutoff' % nskip2)
if nskip1: print('%s messages skipped due to receipt time missing or < cutoff' % nskip1)
bufr.close()
bufrout.close()
