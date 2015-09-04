import ncepbufr
import numpy as np
from netCDF4 import Dataset

hdstr='SID XOB YOB DHR TYP ELV SAID T29'
hdrstr_dict = {}
hdrstr_dict['XOB'] = 'longitude (degrees)'
hdrstr_dict['YOB'] = 'latitude (degrees)'
hdrstr_dict['DHR'] = 'observation time minus cycle time (hours)'
hdrstr_dict['TYP'] = 'prepbufr report type'
hdrstr_dict['ELV'] =  'station elevation (m)'
hdrstr_dict['T29'] = 'data dump report type'
hdrstr_dict['SAID'] = 'satellite identifier'
obstr='POB QOB TOB ZOB UOB VOB PWO MXGS HOVI CAT PRSS TDO PMO'
obstr_dict = {}
obstr_dict['POB'] = 'pressure observation (mb)'
obstr_dict['QOB'] = 'specific humidity observation (mg/Kg)'
obstr_dict['TOB'] = 'temperature observation (C)'
obstr_dict['ZOB'] = 'height observation (m)'
obstr_dict['UOB'] = 'zonal wind observation (m/s)'
obstr_dict['VOB'] = 'meridional wind observation (m/s)'
obstr_dict['PWO'] = 'precipitable water observation (mm)'
obstr_dict['MXGS'] = 'maximum wind speed (gusts) (m/s)'
obstr_dict['HOVI'] = 'horizontal visibility (m)'
obstr_dict['CAT'] = 'prepbufr data level category'
obstr_dict['PRSS'] = 'surface pressure observation (Pa)'
obstr_dict['TDO'] = 'dewpoint temperature observation (C)'
obstr_dict['PMO'] = 'mean sea-level observation (mb)'
qcstr='PQM QQM TQM ZQM WQM NUL PWQ PMQ'
qcstr_dict={}
qcstr_dict['PQM'] = 'pressure quality marker'
qcstr_dict['QQM'] = 'specific humidity quality marker'
qcstr_dict['TQM'] = 'temperature quality marker'
qcstr_dict['ZQM'] = 'height quality marker'
qcstr_dict['WQM'] = 'wind quality marker'
qcstr_dict['NUL'] = 'empty'
qcstr_dict['PWQ'] = 'precipitable water quality marker'
qcstr_dict['PMQ'] = 'mean sea-level quality marker'
oestr='POE QOE TOE NUL WOE NUL PWE'
oestr_dict={}
oestr_dict['POE'] = 'pressure observation error'
oestr_dict['QOE'] = 'specific humidity observation error'
oestr_dict['TOE'] = 'temperature observation error'
oestr_dict['WOE'] = 'wind observation error'
oestr_dict['NUL'] = 'missing'
oestr_dict['PWE'] = 'precipitable water observation error'

# read prepbufr file, write data to netcdf file.

nc = Dataset('prepbufr.nc','w',format='NETCDF4')
hd = nc.createDimension('header',len(hdstr.split())-1)
ob = nc.createDimension('obinfo',len(obstr.split()))
oe = nc.createDimension('oeinfo',len(oestr.split()))
qc = nc.createDimension('qcinfo',len(qcstr.split()))
nlevs = nc.createDimension('nlevs',255)

bufr = ncepbufr.open('prepbufr')
while bufr.advance() == 0: # loop over messages.
    g = nc.createGroup(bufr.msg_type)
    if not g.variables.has_key('obdata'):
        nobs = g.createDimension('nobs',None)
        hdrdata = g.createVariable('header',np.float32,('nobs','header'),zlib=True)
        stnid = g.createVariable('stationid',str,('nobs',))
        for key in hdrstr_dict:
            hdrdata.setncattr(key,hdrstr_dict[key])
        hdrdata.missing_value = 1.e11
        hdrdata.info = hdstr[4:]
        if bufr.msg_type in ['RASSDA','VADWND','PROFLR','ADPUPA']:
            obdata = g.createVariable('obdata',np.float32,('nobs','nlevs','obinfo'),zlib=True)
            oedata = g.createVariable('oberr',np.float32,('nobs','nlevs','oeinfo'),zlib=True)
            qcdata = g.createVariable('qcinfo',np.float32,('nobs','nlevs','qcinfo'),zlib=True)
        else:
            obdata = g.createVariable('obdata',np.float32,('nobs','obinfo'),zlib=True)
            oedata = g.createVariable('oberr',np.float32,('nobs','oeinfo'),zlib=True)
            qcdata = g.createVariable('qcinfo',np.float32,('nobs','qcinfo'),zlib=True)
        for key in obstr_dict:
            obdata.setncattr(key,obstr_dict[key])
        obdata.missing_value=1.e11
        obdata.info = obstr
        for key in oestr_dict:
            oedata.setncattr(key,oestr_dict[key])
        oedata.missing_value = 1.e11
        oedata.info = oestr
        for key in qcstr_dict:
            qcdata.setncattr(key,qcstr_dict[key])
        qcdata.missing_value = 1.e11
        qcdata.info = qcstr
    while bufr.load_subset() == 0: # loop over subsets in message.
        hdr = bufr.read_subset(hdstr).squeeze()
        obs = bufr.read_subset(obstr)
        qc  = bufr.read_subset(qcstr)
        err = bufr.read_subset(oestr)
        n = obs.shape[-1]
        nob = g['header'].shape[0]
        g['header'][nob] = hdr.squeeze()[1:]
        id = hdr[0].tostring()
        g['stationid'][nob] = id
        if bufr.msg_type in ['RASSDA','VADWND','PROFLR','ADPUPA']:
            g['obdata'][nob,:n] = obs.T
            g['oberr'][nob,:n]  = err.T
            g['qcinfo'][nob,:n] = qc.T
        else:
            g['obdata'][nob] = obs.squeeze()
            g['oberr'][nob]  = err.squeeze()
            g['qcinfo'][nob] = qc.squeeze()
    nc.sync()

bufr.close()
nc.close()
