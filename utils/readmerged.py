from netCDF4 import Dataset
import numpy as np
import sys

# ob type, code and level to check
obtype = 'T'
obcode = 120
level = 850.
# define column in obs and gsi diag arrays
print 'obtype, obcode, level = ',obtype,obcode,level
filename = sys.argv[1]

nc = Dataset(filename)

header = nc.variables['header'][:]

for icol,obstr in enumerate(nc.variables['obdata'].obinfo.split()):
    if obstr.startswith('P'): break
press = nc.variables['obdata'][:,icol]
for icol,obstr in enumerate(nc.variables['obdata'].obinfo.split()):
    if obstr.startswith(obtype): break
obs = nc.variables['obdata'][:,icol]
bufrerr = nc.variables['oberr'][:,icol]

for icol,obstr in enumerate(nc.variables['gsigesdata'].diaginfo.split()):
    if obstr.startswith(obtype): break

gsiges = nc.variables['gsigesdata'][:,icol]
gsianl = nc.variables['gsianldata'][:,icol]
enssprd = nc.variables['gsi_ensstd'][:,icol]
gsierr = nc.variables['gsierr'][:,icol]
used = (nc.variables['gsiqc'][:,icol]).astype('bool')

# find indices corresponding to specified obcode, pressure level
idx = np.argwhere( \
   np.logical_and( header[:,4] == obcode, \
   np.abs(level-press) <= 1.0) \
   ).squeeze()
idx = np.compress(used[idx],idx) # only select obs used by GSI
print 'count = ',len(idx)
print 'RMS ges departure',np.sqrt(np.mean( (obs-gsiges)[idx]**2 ))
print 'expected ges departure',np.sqrt(np.mean( (enssprd**2+bufrerr**2)[idx] ))
print 'RMS anl departure',np.sqrt(np.mean( (obs-gsianl)[idx]**2 ))
