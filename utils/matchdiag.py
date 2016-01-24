import read_diag
from netCDF4 import Dataset
import numpy as np
obsfile = 'diag_conv_ges.2010102700'
ncfile = 'prepbufr_2010102700.nc'
diag_conv = read_diag.diag_conv(obsfile,endian='big')
print 'read netcdf'
nc_prepbufr = Dataset(ncfile)
# observation id (station id/type code/lon/lat/time/elevation/pressure)
obidstrs = nc_prepbufr['obid'][:]
obidstrs2 = np.array([obid[:-6] for obid in obidstrs])
#for id in obidstrs:
#    if id.startswith('NZSP'): print id[:-6]
print 'total number of diag obs = ',diag_conv.nobs
print 'total number of prepbufr obs = ',nc_prepbufr.dimensions['nobs'].size 
diag_conv.read_obs()
count_nomatch = 0; count_multmatch = 0
for nob in range(diag_conv.nobs):
    if diag_conv.obtype[nob] == 'gps': continue
    stid = diag_conv.station_ids[nob]
    lon = diag_conv.lon[nob]
    lat = diag_conv.lat[nob]
    time = diag_conv.time[nob]
    press = diag_conv.press[nob]
    elev = diag_conv.stnelev[nob]
    obcode = diag_conv.code[nob]
    obtype = diag_conv.obtype[nob]
    obidstr = "%s %3i %6.2f %6.2f %6.2f %4i %6.1f" % \
    (stid,obcode,lon,lat,time,elev,press)
    if str(obcode).startswith('18') or str(obcode).startswith('28'):
        nobs_nc = np.nonzero(obidstrs2 == obidstr[:-6])[0]
    else:
        nobs_nc = np.nonzero(obidstrs == obidstr)[0]
    print nob,obidstr,len(nobs_nc),'matches'
    if len(nobs_nc) == 0:
        count_nomatch += 1
        #raise ValueError('no match found')
    elif len(nobs_nc) > 1:
        count_multmatch += 1
        print nobs_nc,obidstrs[nobs_nc]
        print nc_prepbufr['obdata'][nobs_nc]
        #raise ValueError('multiple matches found')
print(count_nomatch,' no matches')
print(count_multmatch,' multiple matches')
nc_prepbufr.close()
