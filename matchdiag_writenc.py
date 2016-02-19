import ncepbufr
import numpy as np
from netCDF4 import Dataset
from ncepbufr import prepbufr_mnemonics_dict as mnemonics_dict
import sys, os
import read_diag
import math

# match records in diag_conv_F file to records in prepbufr netcdf file.


out_ncfilename='testing_write2.nc'
nc_out = Dataset(out_ncfilename,'w',format='NETCDF4')



bufr = ncepbufr.open('prepbufr.2015102700')



## PREBUFR NC FILE made with prepbufr2nc ############################################
ncfile = 'prepbufr_2015102700.nc' # made with prepbufr2nc
print 'read netcdf'
nc_prepbufr = Dataset(ncfile)
# observation id (station id/type code/lon/lat/time/elevation/pressure)
obidstrs = nc_prepbufr['obid'][:]
obidl = obidstrs.tolist()
print('%s non-unique ob ids' % str(len(obidl)-len(set(obidl))))
# observation id not including pressure.
obidstrs_nop = np.array([obid[:-6] for obid in obidstrs]) ##dropping pressure from ma
print 'total number of prepbufr obs = ',nc_prepbufr.dimensions['nobs'].size
########## obidstrs (with an 's' at the end, comes from prepbufr
######################################################################################
prep_header = nc_prepbufr['header'][:]
print 'prep header shape=',prep_header.shape
prep_obdata = nc_prepbufr['obdata'][:]
print 'prepobdata whole shape = ',prep_obdata.shape
obdata_shape = prep_obdata.shape
obdata_nrows = prep_obdata.shape[0]
obdata_ncols = prep_obdata.shape[1]
print 'prepobdata rows = ',obdata_nrows
print 'prepobdata columns = ',obdata_ncols
prep_nobs = obdata_nrows
prep_nvarb = obdata_ncols

#print 'new message ',nc_prepbufr.msg_type
print 'prepnobs ',prep_nobs

######################################################################################
hdstr='SID XOB YOB DHR TYP ELV SAID T29'
hd = nc_out.createDimension('hdrinfo',len(hdstr.split()))
nhdd = len(hd)
obstr='POB QOB TOB ZOB UOB VOB PWO CAT PRSS TDO PMO XDR YDR HRDR'
ob = nc_out.createDimension('obinfo',len(obstr.split()))
nobd = len(ob)
qcstr='PQM QQM TQM ZQM WQM PWQ PMQ'
qc = nc_out.createDimension('qcinfo',len(qcstr.split()))
nqcd = len(qc)
oestr='POE QOE TOE ZOE WOE PWE'
oe = nc_out.createDimension('oeinfo',len(oestr.split()))
noed = len(oe)
diag_varbstr='Qdiag Tdiag Udiag Vdiag PSdiag PWdiag GPSdiag SSTdiag TCPdiag'
diag_obs = nc_out.createDimension('diaginfo',len(diag_varbstr.split()))
ndiag_obd = len(diag_obs)

nmsgs = nc_out.createDimension('nmsgs',obdata_nrows)
nobsd = nc_out.createDimension('nobs',None)
######################################################################################
nobs_chunk = 200

print 'nhdd=',nhdd

hdrdata =\
nc_out.createVariable('header',np.float32,('nobs','hdrinfo'),\
fill_value=bufr.missing_value,zlib=True,chunksizes=(nobs_chunk,nhdd))
hdrdata.desc = 'observation header data'
for key in hdstr.split():
    hdrdata.setncattr(key,mnemonics_dict[key])
hdrdata.hdrinfo = hdstr




obid = nc_out.createVariable('obid',str,('nobs',),zlib=True)
obid.desc = 'observation id (station id/type code/lon/lat/time/elevation/pressure)'

obdata =\
nc_out.createVariable('obdata',np.float32,('nobs','obinfo'),\
fill_value=bufr.missing_value,zlib=True,chunksizes=(nobs_chunk,nobd))
for key in obstr.split():
    obdata.setncattr(key,mnemonics_dict[key])
obdata.obinfo = obstr
obdata.desc = 'observation data'

oedata =\
nc_out.createVariable('oberr',np.float32,('nobs','oeinfo'),\
fill_value=bufr.missing_value,zlib=True,chunksizes=(nobs_chunk,noed))
for key in oestr.split():
    oedata.setncattr(key,mnemonics_dict[key])
oedata.oeinfo = oestr
oedata.desc = 'observation error data'

qc_fillval = 255
qcdata =\
nc_out.createVariable('qcdata',np.uint8,('nobs','qcinfo'),\
fill_value=qc_fillval,zlib=True,chunksizes=(nobs_chunk,nqcd))
for key in qcstr.split():
    qcdata.setncattr(key,mnemonics_dict[key])
qcdata.qcinfo = qcstr
qcdata.desc = 'observation QC data'

msgnum = nc_out.createVariable('msgnum',np.uint32,('nobs'),\
zlib=True,chunksizes=(nobs_chunk,))
msgnum.desc = 'bufr message number'
subsetnum = nc_out.createVariable('subsetnum',np.uint16,('nobs'),\
zlib=True,chunksizes=(nobs_chunk,))
subsetnum.desc='subset number within bufr message'
msgtype = nc_out.createVariable('msgtype',str,('nmsgs'),zlib=True)
msgtype.desc='bufr message type'
msgdate = nc_out.createVariable('msgdate',np.uint32,('nmsgs'),zlib=True)
msgdate.desc='bufr message date'




######################################################################################

gsianldataarray = np.empty((obdata_nrows,ndiag_obd))
gsianldataarray[:] = np.NaN
gsigesdataarray = np.empty((obdata_nrows,ndiag_obd))
gsigesdataarray[:] = np.NaN

gsi_Hxarray = np.empty((obdata_nrows,ndiag_obd))
gsi_Hxarray[:] = np.NaN

gsierrarray = np.empty((obdata_nrows,ndiag_obd))
gsierrarray[:] = np.NaN

gsiqcarray = np.empty((obdata_nrows,ndiag_obd))
gsiqcarray[:] = np.NaN

######################################################################################

gsianldata =\
nc_out.createVariable('gsianldata',np.float32,('nobs','diaginfo'),\
fill_value=bufr.missing_value,zlib=True,chunksizes=(prep_nobs,ndiag_obd))
gsigesdata =\
nc_out.createVariable('gsigesdata',np.float32,('nobs','diaginfo'),\
fill_value=bufr.missing_value,zlib=True,chunksizes=(prep_nobs,ndiag_obd))
                
gsi_Hx =\
nc_out.createVariable('gsi_Hx',np.float32,('nobs','diaginfo'),\
fill_value=bufr.missing_value,zlib=True,chunksizes=(prep_nobs,ndiag_obd))

gsierr =\
nc_out.createVariable('gsierr',np.float32,('nobs','diaginfo'),\
fill_value=bufr.missing_value,zlib=True,chunksizes=(prep_nobs,ndiag_obd))

gsiqc =\
nc_out.createVariable('gsiqc',np.uint8,('nobs','diaginfo'),\
fill_value=qc_fillval,zlib=True,chunksizes=(prep_nobs,ndiag_obd))


## DIAG FILE from GSI ################################################################
diagfile_A = 'diag_conv_anl.2015102700'
diag_conv_A = read_diag.diag_conv(diagfile_A,endian='big')
diag_conv_A.read_obs()

diagfile_F = 'diag_conv_ges.2015102700'
diag_conv_F = read_diag.diag_conv(diagfile_F,endian='big')
diag_conv_F.read_obs()
print 'total number of diag obs = ',diag_conv_F.nobs
diag_conv_F.read_obs()

nobs_diag=diag_conv_F.nobs
#prepindx=[]
prepindx = np.empty((nobs_diag,1))
prepindx[:] = np.NaN

obcol = np.empty((nobs_diag,1))
obcol[:] = np.NaN


prnt_break=1000.0
test_stop=10000
#test_stop=diag_conv_F.nobs #full run
count_nomatch = 0

for nob in range(test_stop):
    if diag_conv_F.obtype[nob] in ['tcp','gps']: continue
    stid = diag_conv_F.station_ids[nob]
    lon = diag_conv_F.lon[nob]
    lat = diag_conv_F.lat[nob]
    time = diag_conv_F.time[nob]
    press = diag_conv_F.press[nob]
    # skip if missing or invalid pressure
    if press < 0 or press > 2.e3: continue
    elev = diag_conv_F.stnelev[nob]
    obcode = diag_conv_F.code[nob]
    obtype = diag_conv_F.obtype[nob]
    if ' q' in obtype:
        obcol[nob]=int(0)
    if ' t' in obtype:
        obcol[nob]=int(1)
    if ' u' in obtype:
        obcol[nob]=int(2)
    if ' v' in obtype:
        obcol[nob]=int(3)
    if ' ps' in obtype:
        obcol[nob]=int(4)
    if ' pw' in obtype:
        obcol[nob]=int(5)
    if 'gps' in obtype:
        obcol[nob]=int(6)
    if 'sst' in obtype:
        obcol[nob]=int(7)
    if 'tcp' in obtype:
        obcol[nob]=int(8)
    obs_F = diag_conv_F.obs[nob]
    obs_A = diag_conv_A.obs[nob]
    hx_A = diag_conv_A.hx[nob]
    oberr_A = diag_conv_A.oberr[nob]
    used_A = diag_conv_A.used[nob]

    used = used_A

    obidstr = "%s %3i %6.2f %6.2f %9.5f %5i %6.1f" % \
    (stid,obcode,lon,lat,time,elev,press)

    nobs_nc = np.nonzero(obidstrs_nop == obidstr[:-6])[0]

    if len(nobs_nc) > 1: # if more than one match, include pressure
        nobs_nc = np.nonzero(obidstrs == obidstr)[0]
    if len(nobs_nc) == 0 and used == 1:
        count_nomatch += 1
    elif len(nobs_nc) == 1:
        prepindx[nob] = nobs_nc[0]
    elif len(nobs_nc) > 1:
        raise ValueError('multiple matches found')
        prepindx[nob] = nobs_nc[0]
    if (float(nob)/prnt_break) == round(float(nob)/prnt_break,0):
        print nob,used,obidstr,len(nobs_nc),'matches'
    if not(math.isnan(prepindx[nob])):

        gsigesdataarray[int(prepindx[nob]),int(obcol[nob])] = obs_F
        gsianldataarray[int(prepindx[nob]),int(obcol[nob])] = obs_A
        gsi_Hxarray[int(prepindx[nob]),int(obcol[nob])] = hx_A
        gsierrarray[int(prepindx[nob]),int(obcol[nob])] = oberr_A
        gsiqcarray[int(prepindx[nob]),int(obcol[nob])] = used_A


print('%s no matches' % count_nomatch)


######################################################################################
gsianldata.setncattr('q','specific humidity')
gsianldata.setncattr('t','temperature')
gsianldata.setncattr('u','U-wind')
gsianldata.setncattr('v','V-wind')
gsianldata.setncattr('ps','surface pressure')
gsianldata.setncattr('gps','gps')
gsianldata.setncattr('sst','sea surface temperature')
gsianldata.setncattr('tcp','tropical cyclone pressure')
gsianldata.diaginfo = diag_varbstr
gsianldata.desc = 'diag obs ANL'

gsigesdata.setncattr('q','specific humidity')
gsigesdata.setncattr('t','temperature')
gsigesdata.setncattr('u','U-wind')
gsigesdata.setncattr('v','V-wind')
gsigesdata.setncattr('ps','surface pressure')
gsigesdata.setncattr('gps','gps')
gsigesdata.setncattr('sst','sea surface temperature')
gsigesdata.setncattr('tcp','tropical cyclone pressure')
gsigesdata.diaginfo = diag_varbstr
gsigesdata.desc = 'diag obs GES'

gsi_Hx.setncattr('q','specific humidity')
gsi_Hx.setncattr('t','temperature')
gsi_Hx.setncattr('u','U-wind')
gsi_Hx.setncattr('v','V-wind')
gsi_Hx.setncattr('ps','surface pressure')
gsi_Hx.setncattr('gps','gps')
gsi_Hx.setncattr('sst','sea surface temperature')
gsi_Hx.setncattr('tcp','tropical cyclone pressure')
gsi_Hx.diaginfo = diag_varbstr
gsi_Hx.desc = 'diag hx ANL'


gsierr.setncattr('q','specific humidity')
gsierr.setncattr('t','temperature')
gsierr.setncattr('u','U-wind')
gsierr.setncattr('v','V-wind')
gsierr.setncattr('ps','surface pressure')
gsierr.setncattr('gps','gps')
gsierr.setncattr('sst','sea surface temperature')
gsierr.setncattr('tcp','tropical cyclone pressure')
gsierr.diaginfo = diag_varbstr
gsierr.desc = 'diag oberr ANL'


gsiqc.setncattr('q','specific humidity')
gsiqc.setncattr('t','temperature')
gsiqc.setncattr('u','U-wind')
gsiqc.setncattr('v','V-wind')
gsiqc.setncattr('ps','surface pressure')
gsiqc.setncattr('gps','gps')
gsiqc.setncattr('sst','sea surface temperature')
gsiqc.setncattr('tcp','tropical cyclone pressure')
gsiqc.diaginfo = diag_varbstr
gsiqc.desc = 'gsi QC flags (1: used, 0: not used)'

######################################################################################




prep_header = nc_prepbufr['header'][:]
prep_oberr = nc_prepbufr['oberr'][:]
prep_qcdata = nc_prepbufr['qcdata'][:]
prep_obid = nc_prepbufr['obid'][:]
prep_msgnum = nc_prepbufr['msgnum'][:]
prep_subsetnum = nc_prepbufr['subsetnum'][:]

print nc_out['header'].shape
print prep_header.shape
print nc_out['obdata'].shape
print prep_obdata.shape

nc_out['header'][:] = prep_header[:]
nc_out['obdata'][:] = prep_obdata[:]
nc_out['oberr'][:]  = prep_oberr[:]
nc_out['qcdata'][:] = prep_qcdata[:]
nc_out['obid'][:] = prep_obid[:]
nc_out['msgnum'][:] = prep_msgnum[:]
nc_out['subsetnum'][:] = prep_subsetnum[:]

nc_out['gsianldata'][:] = gsianldataarray[:]
nc_out['gsi_Hx'][:] = gsi_Hxarray[:]
nc_out['gsierr'][:] = gsierrarray[:]
nc_out['gsiqc'][:] =  gsiqcarray[:]
nc_out['gsigesdata'][:] = gsigesdataarray[:]

nc_out.sync()
nc_out.close()


nc_prepbufr.close()




