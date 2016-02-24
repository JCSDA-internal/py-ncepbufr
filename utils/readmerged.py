from netCDF4 import Dataset
import numpy as np
import sys
# ob type, code and level to check
obtype = '  q'
obcode = 120
level = 850.
# define column in obs and gsi diag arrays
if obtype == '  t':
    obcol1 = 2
    obcol2 = 1
elif obtype == '  q':
    obcol1 = 1
    obcol2 = 0
elif obtype == '  u':
    obcol1 = 4
    obcol2 = 2
elif obtype == '  v':
    obcol1 = 5
    obcol2 = 3
else:
    raise ValueError('unrecognized ob type')
print 'obtype, obcode, level = ',obtype,obcode,level
filename = sys.argv[1]
nc = Dataset(filename)
obdata = nc.variables['obdata'][:]
gsigesdata = nc.variables['gsigesdata'][:]
gsianldata = nc.variables['gsianldata'][:]
header = nc.variables['header'][:]
# set un-set values as not used
gsiqc = nc.variables['gsiqc'][:]
idx = np.argwhere(\
   np.logical_and( header[:,4] == obcode, np.abs(level-obdata[:,0]) <= 1.0)\
   ).squeeze()
used = gsiqc[idx,obcol2].astype('bool')
idx = np.compress(used,idx)
obs = obdata[idx,obcol1]
ges = gsigesdata[idx,obcol2]
anl = gsianldata[idx,obcol2]
print 'count = ',len(idx)
print 'min/max for obs, ges, anl'
print obs.min(), obs.max()
print ges.min(), ges.max()
print anl.min(), anl.max()
print 'RMS ges departure',np.sqrt(np.mean( (obs-ges)**2 ))
print 'RMS anl departure',np.sqrt(np.mean( (obs-anl)**2 ))
