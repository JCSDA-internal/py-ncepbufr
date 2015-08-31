from __future__ import print_function
import ncepbufr
import sys

# dump contents of bufr file to stdout or to a text file.
# Warning: resulting output may be HUGE.

bufr = ncepbufr.open(sys.argv[1])
first_dump = True
while bufr.advance() == 0: # loop over messages.
    while bufr.load_subset() == 0: # loop over subsets in message.
        if len(sys.argv) > 2:
            # dump decoded data to a file.
            if first_dump:
                bufr.dump_subset(sys.argv[2]) # print decoded subset to stdout
                first_dump = False
            else:
                bufr.dump_subset(sys.argv[2],append=True) # print decoded subset to stdout
        else:
            bufr.print_subset() # print decoded subset to stdout
bufr.close()
