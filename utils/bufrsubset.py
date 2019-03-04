"""bufrsubset.py - read in a bufr file, copy a subset of bufr data 
with receipt time later than specified time to a new file.

version 0.1: Jeff Whitaker 20190305
"""
from __future__ import print_function
import ncepbufr, sys, argparse

# Parse command line args
ap = argparse.ArgumentParser()
ap.add_argument("input_bufr", help="path to input BUFR file")
ap.add_argument("receipt_time", help="threshold receipt time (YYYYMMDDHHMM)")
ap.add_argument("output_bufr", help="output BUFR file")
ap.add_argument('--verbose', '-v', action='store_true')

MyArgs = ap.parse_args()

filename_in = MyArgs.input_bufr
filename_out = MyArgs.output_bufr
receipt_time = int(MyArgs.receipt_time)
verbose=MyArgs.verbose
print("""input_bufr=%s 
receipt_time=%s
output_bufr=%s""" % (filename_in,receipt_time,filename_out))

if filename_out == filename_in:
    msg="output file must not have same name as input file"
    raise SystemExit(msg)

bufr = ncepbufr.open(filename_in)
print('creating %s' % filename_out)
bufrout = ncepbufr.open(filename_out,'w',bufr)

ncount = 0; nskip = 0
while bufr.advance() == 0: 
    if bufr.receipt_time > 0 and bufr.receipt_time > receipt_time:
        if verbose: print('writing message with receipt time %s (> %s)' % (bufr.receipt_time,receipt_time))
        bufrout.open_message(bufr.msg_type,bufr.msg_date,bufr.receipt_time) # open output message
        ncount += 1
        while bufr.load_subset() == 0: # loop over subsets in message.
            bufrout.copy_subset(bufr)
        bufrout.close_message() # close message
    else:
        nskip += 1

print('%s messages copied, %s messages skipped' % (ncount,nskip))
# close up shop.
bufr.close(); bufrout.close()
