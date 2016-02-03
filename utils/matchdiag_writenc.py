import ncepbufr
import numpy as np
from netCDF4 import Dataset
from ncepbufr import prepbufr_mnemonics_dict as mnemonics_dict
import sys, os
import read_diag
import math




# match records in diag_conv_F file to records in prepbufr netcdf file.


out_ncfilename='testing_write.nc'
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
hd = nc_out.createDimension('hdrinfo',len(hdstr.split())-1)
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
oedata =\
nc_out.createVariable('oberr',np.float32,('nobs','oeinfo'),\
fill_value=bufr.missing_value,zlib=True,chunksizes=(nobs_chunk,noed))
qc_fillval = 255
qcdata =\
nc_out.createVariable('qcdata',np.uint8,('nobs','qcinfo'),\
fill_value=qc_fillval,zlib=True,chunksizes=(nobs_chunk,nqcd))
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

obdata_Aarray = np.empty((obdata_nrows,ndiag_obd))
obdata_Aarray[:] = np.NaN
obdata_Farray = np.empty((obdata_nrows,ndiag_obd))
obdata_Farray[:] = np.NaN

hxdata_Aarray = np.empty((obdata_nrows,ndiag_obd))
hxdata_Aarray[:] = np.NaN
hxdata_Farray = np.empty((obdata_nrows,ndiag_obd))
hxdata_Farray[:] = np.NaN

oberrdata_Aarray = np.empty((obdata_nrows,ndiag_obd))
oberrdata_Aarray[:] = np.NaN
oberrdata_Farray = np.empty((obdata_nrows,ndiag_obd))
oberrdata_Farray[:] = np.NaN

useddata_Aarray = np.empty((obdata_nrows,ndiag_obd))
useddata_Aarray[:] = np.NaN
useddata_Farray = np.empty((obdata_nrows,ndiag_obd))
useddata_Farray[:] = np.NaN

######################################################################################
#unique(diag_obtype)=    '   q'    '   t'    '   u'    '   v'    '  ps'    '  pw'    ' gps'    ' sst'    ' tcp'



obdata_A =\
nc_out.createVariable('obdata_A',np.float32,('nobs','diaginfo'),\
fill_value=bufr.missing_value,zlib=True,chunksizes=(prep_nobs,ndiag_obd))
obdata_F =\
nc_out.createVariable('obdata_F',np.float32,('nobs','diaginfo'),\
fill_value=bufr.missing_value,zlib=True,chunksizes=(prep_nobs,ndiag_obd))
                
hxdata_A =\
nc_out.createVariable('hxdata_A',np.float32,('nobs','diaginfo'),\
fill_value=bufr.missing_value,zlib=True,chunksizes=(prep_nobs,ndiag_obd))
hxdata_F =\
nc_out.createVariable('hxdata_F',np.float32,('nobs','diaginfo'),\
fill_value=bufr.missing_value,zlib=True,chunksizes=(prep_nobs,ndiag_obd))
                             
oberrdata_A =\
nc_out.createVariable('oberrdata_A',np.float32,('nobs','diaginfo'),\
fill_value=bufr.missing_value,zlib=True,chunksizes=(prep_nobs,ndiag_obd))
oberrdata_F =\
nc_out.createVariable('oberrdata_F',np.float32,('nobs','diaginfo'),\
fill_value=bufr.missing_value,zlib=True,chunksizes=(prep_nobs,ndiag_obd))
                             
useddata_A =\
nc_out.createVariable('useddata_A',np.float32,('nobs','diaginfo'),\
fill_value=bufr.missing_value,zlib=True,chunksizes=(prep_nobs,ndiag_obd))
useddata_F =\
nc_out.createVariable('useddata_F',np.float32,('nobs','diaginfo'),\
fill_value=bufr.missing_value,zlib=True,chunksizes=(prep_nobs,ndiag_obd))


## DIAG FILE from GSI ################################################################
obsfile_A = 'diag_conv_anl.2015102700'
diag_conv_A = read_diag.diag_conv(obsfile_A,endian='big')
diag_conv_A.read_obs()

obsfile_F = 'diag_conv_ges.2015102700'
diag_conv_F = read_diag.diag_conv(obsfile_F,endian='big')
diag_conv_F.read_obs()
print 'total number of diag obs = ',diag_conv_F.nobs
diag_conv_F.read_obs()

nobs_diag=diag_conv_F.nobs
#prepindx=[]
prepindx = np.empty((nobs_diag,1))
prepindx[:] = np.NaN

obcol = np.empty((nobs_diag,1))
obcol[:] = np.NaN


######################################################################################
obdata_A.setncattr('q','specific humidity')
obdata_A.setncattr('t','temperature')
obdata_A.setncattr('u','U-wind')
obdata_A.setncattr('v','V-wind')
obdata_A.setncattr('ps','surface pressure')
obdata_A.setncattr('gps','gps')
obdata_A.setncattr('sst','sea surface temperature')
obdata_A.setncattr('tcp','tropical cyclone pressure')
obdata_A.diaginfo = diag_varbstr
obdata_A.desc = 'diag obs ANL'

obdata_F.setncattr('q','specific humidity')
obdata_F.setncattr('t','temperature')
obdata_F.setncattr('u','U-wind')
obdata_F.setncattr('v','V-wind')
obdata_F.setncattr('ps','surface pressure')
obdata_F.setncattr('gps','gps')
obdata_F.setncattr('sst','sea surface temperature')
obdata_F.setncattr('tcp','tropical cyclone pressure')
obdata_F.diaginfo = diag_varbstr
obdata_F.desc = 'diag obs GES'

hxdata_A.setncattr('q','specific humidity')
hxdata_A.setncattr('t','temperature')
hxdata_A.setncattr('u','U-wind')
hxdata_A.setncattr('v','V-wind')
hxdata_A.setncattr('ps','surface pressure')
hxdata_A.setncattr('gps','gps')
hxdata_A.setncattr('sst','sea surface temperature')
hxdata_A.setncattr('tcp','tropical cyclone pressure')
hxdata_A.diaginfo = diag_varbstr
hxdata_A.desc = 'diag hx ANL'

hxdata_F.setncattr('q','specific humidity')
hxdata_F.setncattr('t','temperature')
hxdata_F.setncattr('u','U-wind')
hxdata_F.setncattr('v','V-wind')
hxdata_F.setncattr('ps','surface pressure')
hxdata_F.setncattr('gps','gps')
hxdata_F.setncattr('sst','sea surface temperature')
hxdata_F.setncattr('tcp','tropical cyclone pressure')
hxdata_F.diaginfo = diag_varbstr
hxdata_F.desc = 'diag hx GES'

oberrdata_A.setncattr('q','specific humidity')
oberrdata_A.setncattr('t','temperature')
oberrdata_A.setncattr('u','U-wind')
oberrdata_A.setncattr('v','V-wind')
oberrdata_A.setncattr('ps','surface pressure')
oberrdata_A.setncattr('gps','gps')
oberrdata_A.setncattr('sst','sea surface temperature')
oberrdata_A.setncattr('tcp','tropical cyclone pressure')
oberrdata_A.diaginfo = diag_varbstr
oberrdata_A.desc = 'diag oberr ANL'

oberrdata_F.setncattr('q','specific humidity')
oberrdata_F.setncattr('t','temperature')
oberrdata_F.setncattr('u','U-wind')
oberrdata_F.setncattr('v','V-wind')
oberrdata_F.setncattr('ps','surface pressure')
oberrdata_F.setncattr('gps','gps')
oberrdata_F.setncattr('sst','sea surface temperature')
oberrdata_F.setncattr('tcp','tropical cyclone pressure')
oberrdata_F.diaginfo = diag_varbstr
oberrdata_F.desc = 'diag oberr GES'

useddata_A.setncattr('q','specific humidity')
useddata_A.setncattr('t','temperature')
useddata_A.setncattr('u','U-wind')
useddata_A.setncattr('v','V-wind')
useddata_A.setncattr('ps','surface pressure')
useddata_A.setncattr('gps','gps')
useddata_A.setncattr('sst','sea surface temperature')
useddata_A.setncattr('tcp','tropical cyclone pressure')
useddata_A.diaginfo = diag_varbstr
useddata_A.desc = 'diag use ANL'

useddata_F.setncattr('q','specific humidity')
useddata_F.setncattr('t','temperature')
useddata_F.setncattr('u','U-wind')
useddata_F.setncattr('v','V-wind')
useddata_F.setncattr('ps','surface pressure')
useddata_F.setncattr('gps','gps')
useddata_F.setncattr('sst','sea surface temperature')
useddata_F.setncattr('tcp','tropical cyclone pressure')
useddata_F.diaginfo = diag_varbstr
useddata_F.desc = 'diag use GES'
######################################################################################

trystop=100

count_nomatch = 0
#for nob in range(diag_conv_F.nobs):
for nob in range(trystop):
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
    #print obtype
    obs_F = diag_conv_F.obs[nob]
    obs_A = diag_conv_A.obs[nob]
    hx_F = diag_conv_F.hx[nob]
    hx_A = diag_conv_A.hx[nob]
    oberr_F = diag_conv_F.oberr[nob]
    oberr_A = diag_conv_A.oberr[nob]
    used_F = diag_conv_F.used[nob]
    used_A = diag_conv_A.used[nob]

    used = used_F

    obidstr = "%s %3i %6.2f %6.2f %9.5f %5i %6.1f" % \
    (stid,obcode,lon,lat,time,elev,press)  #### OBIDSTR HERE is one made with diag data

    nobs_nc = np.nonzero(obidstrs_nop == obidstr[:-6])[0]
    #if the diag matches the no pressure prepbufr....
    ## how is len(nobs_nc) > 1 ever supposed to happen when there is the [0] indx selected above?????
    
    
    #    print 'prepobdata = ',prep_obdata[nobs_nc]
    #    print 'prepobdata shape = ',prep_obdata[nobs_nc].shape
    if len(nobs_nc) > 1: # if more than one match, include pressure
        #        print obidstr
        #        print nobs_nc
        #        print obidstrs[nobs_nc]
        nobs_nc = np.nonzero(obidstrs == obidstr)[0]
        #        print nobs_nc
        #        print obidstrs[nobs_nc]
    if len(nobs_nc) == 0 and used == 1:
        # count obs with no matches that were used by GSI
        count_nomatch += 1
        #raise ValueError('no match found')
    elif len(nobs_nc) == 1:
        prepindx[nob] = nobs_nc[0]
    elif len(nobs_nc) > 1:
        raise ValueError('multiple matches found')
        prepindx[nob] = nobs_nc[0]
#    print prepindx[nob]
    if (float(nob)/10.0) == round(float(nob)/10.0,0):
        #print obtype, prepindx[nob], nob,used,obidstr,len(nobs_nc),'matches'
        #        print obtype, obcol[nob],prepindx[nob], obs_F
        print nob,used,obidstr,len(nobs_nc),'matches'

##if we match the obtype to u v t q etc, place it in that column of the out matrix

    if not(math.isnan(prepindx[nob])):
        obdata_Farray[int(prepindx[nob]),int(obcol[nob])] = obs_F
        obdata_Aarray[int(prepindx[nob]),int(obcol[nob])] = obs_A
        hxdata_Farray[int(prepindx[nob]),int(obcol[nob])] = hx_F
        hxdata_Aarray[int(prepindx[nob]),int(obcol[nob])] = hx_A
        oberrdata_Farray[int(prepindx[nob]),int(obcol[nob])] = oberr_F
        oberrdata_Aarray[int(prepindx[nob]),int(obcol[nob])] = oberr_A
        useddata_Farray[int(prepindx[nob]),int(obcol[nob])] = used_F
        useddata_Aarray[int(prepindx[nob]),int(obcol[nob])] = used_A
#print obdata_F[int(prepindx[nob]),:]




print('%s no matches' % count_nomatch)




#prep_header = nc_prepbufr['header'][:]
print 'prep header shape=',prep_header.shape
#prep_obdata = nc_prepbufr['obdata'][:]
print 'prepobdata whole shape = ',prep_obdata.shape
print 'obdata_Aarray shape = ',obdata_Aarray.shape
#print 'out header shape = ',header.shape
print 'obdata_A shape = ',obdata_A.shape
#hhhh=[]
#hhhh =  nc_prepbufr['header'][:]
#print 'header shape = ',hhhh.shape


prep_header = nc_prepbufr['header'][:]
prep_oberr = nc_prepbufr['oberr'][:]
prep_qcdata = nc_prepbufr['qcdata'][:]
prep_obid = nc_prepbufr['obid'][:]
prep_msgnum = nc_prepbufr['msgnum'][:]
prep_subsetnum = nc_prepbufr['subsetnum'][:]



#nc_out['header'][:] = prep_header[:]
nc_out['obdata'][:] = prep_obdata[:]
nc_out['oberr'][:]  = prep_oberr[:]
nc_out['qcdata'][:] = prep_qcdata[:]
nc_out['obid'][:] = prep_obid[:]
nc_out['msgnum'][:] = prep_msgnum[:]
nc_out['subsetnum'][:] = prep_subsetnum[:]


nc_out['obdata_A'][:] = obdata_Aarray[:]
nc_out['hxdata_A'][:] = hxdata_Aarray[:]
nc_out['oberrdata_A'][:] = oberrdata_Aarray[:]
nc_out['useddata_A'][:] =  useddata_Aarray[:]
nc_out['obdata_F'][:] = obdata_Farray[:]
nc_out['hxdata_F'][:] = hxdata_Farray[:]
nc_out['oberrdata_F'][:] = oberrdata_Farray[:]
nc_out['useddata_F'][:] = useddata_Farray[:]

nc_out.sync()
nc_out.close()


nc_prepbufr.close()




