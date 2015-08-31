from __future__ import print_function
import ncepbufr
import sys

# dump contents of bufr file to a text file
# Warning: resulting file may be HUGE.

bufr = ncepbufr.open(sys.argv[1])
while bufr.advance() == 0: # loop over messages.
    while bufr.load_subset() == 0: # loop over subsets in message.
        subset_dump = bufr.print_subset() # print decoded subset to stdout
bufr.close()
