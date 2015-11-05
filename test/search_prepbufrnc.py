from __future__ import print_function
from netCDF4 import Dataset
import numpy as np
import sys, time

# script to test searching and extracting data from
# netcdf prepbufr file (created with prepbufr2nc).

t0 = time.clock()
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
tqc = g.variables['qcdata'][indices,2].astype('i') # read in temp qc flags
good_indices = tqc < 7 # find boolean indices for temp qc mark < 7 (good data)
print(indices.sum(),' obs found matching %s %s' % (dump_type,report_type))
t2 = time.clock()

print(t2-t1,'seconds for search')
t1 = time.clock()
# read data for desired types using boolean indices.
tdata = g.variables['obdata'][indices,2] # temp ob
pdata = g.variables['obdata'][indices,0] # pressure values
londata = g.variables['obdata'][indices,11] # longitude (including drift)
latdata = g.variables['obdata'][indices,12] # latitude (including drift)
pselect = (pdata < 501) & (pdata > 499) # indices of press values near 500 hPa
#pselect = pdata == 500
tdata_500 = tdata[np.logical_and(good_indices,pselect)]
nonmissing_indices = tdata_500.mask == False
tdata_500 = tdata_500.compressed()
lons_500 = londata[np.logical_and(good_indices, pselect)] # lons of stations
lons_500 = lons_500[nonmissing_indices] # toss missing temp ob locations
lats_500 = latdata[np.logical_and(good_indices, pselect)] # lats of stations
lats_500 = lats_500[nonmissing_indices]
print(lats_500.mask.sum())
print(tdata_500.shape, tdata_500.min(), tdata_500.max())
print(lons_500.shape, lons_500.min(), lons_500.max())
print(lats_500.shape, lats_500.min(), lats_500.max())
t2 = time.clock()
print(t2-t1,'seconds to read data')
print(t2-t0,'total time')
nc.close()
