"""filterbyreceipt.py - read in a bufr file, copy a subset of bufr data
with receipt time later than specified time to a new file.

version 1.0: Jeff Whitaker 20190811
"""
from __future__ import print_function
import ncepbufr, sys, os, argparse
import numpy as np

# Parse command line args
ap = argparse.ArgumentParser()
ap.add_argument("input_bufr", help="path to input BUFR file")
ap.add_argument("output_bufr", help="output BUFR file")
msg="""
threshold receipt time (YYYYMMDDHHMM). If not specifed,
use maximum value in input_bufr."""
ap.add_argument("--receipt_time", '-rt', help=msg)

MyArgs = ap.parse_args()

filename_in = MyArgs.input_bufr
filename_out = MyArgs.output_bufr
receipt_time_cutoff = int(MyArgs.receipt_time)

if filename_out == filename_in:
    msg="output file must not have same name as input file"
    raise SystemExit(msg)

if receipt_time_cutoff is None:  # no receipt time specified
    # if filenameref is a file, determine receipt_time_cutoff
    # by looking for newest receipt time in the file.
    bufr = ncepbufr.open(filename_in)
    receipt_time_cutoff = -1
    while bufr.advance() == 0: # loop over messages.
        if bufr.receipt_time > receipt_time_cutoff:
            receipt_time_cutoff=bufr.receipt_time
    bufr.close()
print('receipt time cutoff = %s' % receipt_time_cutoff)

bufr = ncepbufr.open(filename_in)
bufrout = ncepbufr.open(filename_out,'w',bufr)
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
