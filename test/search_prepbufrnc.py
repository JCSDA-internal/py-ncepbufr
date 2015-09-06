from __future__ import print_function
from netCDF4 import Dataset
import sys, time

# script to test searching and extracting data from
# netcdf prepbufr file (created with prepbufr2nc).

# input filename
filename = sys.argv[1]
# message type (ADPUPA, SFCSHP, etc)
dump_type = sys.argv[2]
# integer report time (e.g. 120 for radiosone temp)
report_type = int(sys.argv[3])
nc = Dataset(filename) # open netcdf file
g = nc.groups[dump_type] # get group corresponding to msg type

t1 = time.clock()
types = g.variables['header'][:,3].astype('i') # read in report types
indices = types == report_type # find boolean indices for desired type
print(indices.sum(),' obs found matching %s %s' % (dump_type,report_type))
t2 = time.clock()
 
print(t2-t1,'seconds for search')
t1 = time.clock()
# read data for desired types using boolean indices.
data = g.variables['obdata'][indices]
print(data.shape)
t2 = time.clock()
print(t2-t1,'seconds to read data')
nc.close()
