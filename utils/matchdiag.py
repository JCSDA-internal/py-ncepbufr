import read_diag
from netCDF4 import Dataset
import numpy as np
# match records in diag_conv file to records in prepbufr netcdf file.
obsfile = 'diag_conv_ges.2010102700'
ncfile = 'prepbufr_2010102700.nc'
diag_conv = read_diag.diag_conv(obsfile,endian='big')
print 'read netcdf'
nc_prepbufr = Dataset(ncfile)
# observation id (station id/type code/lon/lat/time/elevation/pressure)
obidstrs = nc_prepbufr['obid'][:]
obidl = obidstrs.tolist()
#for obid in obidl:
#    if obid.startswith('89009'): print obid
#raise SystemExit
print('%s non-unique ob ids' % str(len(obidl)-len(set(obidl))))
# observation id not including pressure.
obidstrs_nop = np.array([obid[:-6] for obid in obidstrs])
print 'total number of diag obs = ',diag_conv.nobs
print 'total number of prepbufr obs = ',nc_prepbufr.dimensions['nobs'].size
diag_conv.read_obs()
count_nomatch = 0
for nob in range(diag_conv.nobs):
    if diag_conv.obtype[nob] in ['tcp','gps']: continue
    stid = diag_conv.station_ids[nob]
    lon = diag_conv.lon[nob]
    lat = diag_conv.lat[nob]
    time = diag_conv.time[nob]
    press = diag_conv.press[nob]
    # skip if missing or invalid pressure
    if press < 0 or press > 2.e3: continue
    elev = diag_conv.stnelev[nob]
    obcode = diag_conv.code[nob]
    obtype = diag_conv.obtype[nob]
    obidstr = "%s %3i %6.2f %6.2f %9.5f %5i %6.1f" % \
    (stid,obcode,lon,lat,time,elev,press)
    nobs_nc = np.nonzero(obidstrs_nop == obidstr[:-6])[0]
    if len(nobs_nc) > 1: # if more than one match, include pressure
        nobs_nc = np.nonzero(obidstrs == obidstr)[0]
    print nob,obidstr,len(nobs_nc),'matches'
    if len(nobs_nc) == 0:
        count_nomatch += 1
        #raise ValueError('no match found')
    elif len(nobs_nc) > 1:
        raise ValueError('multiple matches found')
print('%s no matches' % count_nomatch)
nc_prepbufr.close()
