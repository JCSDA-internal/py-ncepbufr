from __future__ import print_function
import ncepbufr
import sys

# print inventory of specified bufr file

bufr = ncepbufr.open(sys.argv[1])
for n,msg in enumerate(bufr.inventory()):
    out = (n+1,)+msg
    print('message %s: %s %s %s %s subsets' % out)
bufr.close()
