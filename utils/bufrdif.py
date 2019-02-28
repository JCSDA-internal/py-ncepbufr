"""bufrdif.py - read in two bufr files, write out a third containing data
that is unique in the 2nd file

version 0.1: Jeff Whitaker 20190227
"""
from __future__ import print_function
import ncepbufr, sys, os, tempfile, hashlib
from datetime import datetime, timedelta

if len(sys.argv) < 5:
    msg = """python prepbufrdif.py <bufr 1> <bufr 2> <bufr2-bufr1> <bufr_type>
where <bufr 1> is input bufr file (early cutoff)
      <bufr 2> is input bufr file (late cutoff)
      <bufr2-bufr1> is output bufr file containing obs in 2 not in 1
      <bufr_type> is type of bufr file ('prep','satwnd')\n"""
    raise SystemExit(msg)
filename_in1 = sys.argv[1]
filename_in2 = sys.argv[2]
filename_out = sys.argv[3]
bufr_type = sys.argv[4]
if filename_out == filename_in1 or filename_out == filename_in2:
    msg="output file must not have same name as input files"
    raise SystemExit(msg)

verbose = False # controls level of output

if bufr_type == 'prep':
    hdstr='SID XOB YOB DHR TYP ELV T29'
    obstr='POB QOB TOB UOB VOB PMO PRSS PWO'
    qcstr='PQM QQM TQM WQM PMQ PWQ'
elif bufr_type == 'satwnd':
    hdstr = 'SAID CLAT CLON CLATH CLONH YEAR MNTH DAYS HOUR MINU SWCM SAZA SCCF SWQM'
    obstr = 'EHAM HAMD PRLC WDIR WSPD'
    qcstr = 'OGCE GNAP PCCF'
else:
    msg="unrecognized bufr_type, must be one of 'prep','satwnd'"
    raise SystemExit(msg)

def splitdate(yyyymmddhh):
    """
 yyyy,mm,dd,hh = splitdate(yyyymmddhh)

 give an date string (yyyymmddhh) return integers yyyy,mm,dd,hh.
    """
    yyyymmddhh = str(yyyymmddhh)
    yyyy = int(yyyymmddhh[0:4])
    mm = int(yyyymmddhh[4:6])
    dd = int(yyyymmddhh[6:8])
    hh = int(yyyymmddhh[8:10])
    return yyyy,mm,dd,hh

def get_bufr_dict(bufr,verbose=False,bufr_type='prep'):
    bufr_dict = {}
    ndup = 0
    delta = timedelta(seconds=1)
    while bufr.advance() == 0: 
        nsubset = 0
        if bufr_type == 'prep':
            yyyy,mm,dd,hh = splitdate(bufr.msg_date)
            refdate = datetime(yyyy,mm,dd,hh)
        while bufr.load_subset() == 0: # loop over subsets in message.
            hdr = bufr.read_subset(hdstr).squeeze()
            if bufr_type == 'prep':
                secs = int(hdr[3]*3600.)
                obdate = refdate + secs*delta
                hdr[3]=float(obdate.strftime('%Y%m%d%H%M%S')) # YYYYMMDDHHMMSS
            hdrhash = hash(hdr.tostring())
            obshash = hash(bufr.read_subset(obstr).tostring())
            qchash = hash(bufr.read_subset(qcstr).tostring())
            key = '%s %s %s %s' % (bufr.msg_type,hdrhash,obshash,qchash)
            key = hashlib.md5(key).hexdigest()
            nsubset += 1
            if key in bufr_dict:
                ndup += 1
                if verbose: print('warning: duplicate key for msg type %s' % bufr.msg_type)
            else:
                bufr_dict[key] = bufr.msg_counter,nsubset
    return bufr_dict,ndup

# create dictionaries with md5 hashes for each message as keys, 
# (msg number,subset number) tuple as values.
bufr = ncepbufr.open(filename_in1)
bufr_dict1,ndup = get_bufr_dict(bufr,verbose=verbose,bufr_type=bufr_type)
print('%s duplicate keys found in %s' % (ndup,filename_in1))
bufr.close()

bufr = ncepbufr.open(filename_in2)
bufr_dict2,ndup = get_bufr_dict(bufr,verbose=verbose,bufr_type=bufr_type)
print('%s duplicate keys found in %s' % (ndup,filename_in2))

# find message subsets in bufr 2 that aren't in bufr 1
# uniq_messages is a dict whose keys are message numbers.
# dict entry is a list with unique subset numbers.
ncount = 0; uniq_messages = {}
for bkey in bufr_dict2:
    if bkey not in bufr_dict1:
        ncount += 1
        nmsg, nsubset = bufr_dict2[bkey]
        if nmsg in uniq_messages:
           uniq_messages[nmsg].append(nsubset)
        else:
           uniq_messages[nmsg] = [nsubset]
        if verbose: print('msg/subset %s/%s in %s not in %s' % (nmsg,nsubset,filename_in2,filename_in1))
print('%s unique message subsets (out of %s) in %s' % (ncount,len(bufr_dict2),filename_in2))

# write unique messages in bufr 2 to new file
# open output bufr file using same prepbufr table.
print('creating %s' % filename_out)
bufr.rewind()
bufrout = ncepbufr.open(filename_out,'w',bufr)
while bufr.advance() == 0: 
    if bufr.msg_counter in uniq_messages: # this message has a unique subset
        bufrout.open_message(bufr.msg_type,bufr.msg_date) # open output message
        nsubset = 0
        while bufr.load_subset() == 0: # loop over subsets in message.
            nsubset += 1 
            if nsubset in uniq_messages[bufr.msg_counter]: # write unique subsets
                bufrout.copy_subset(bufr)
        bufrout.close_message() # close message

# close up shop.
bufr.close(); bufrout.close()
