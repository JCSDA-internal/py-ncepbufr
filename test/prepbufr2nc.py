import ncepbufr
import numpy as np
from netCDF4 import Dataset
from prepbufr_mnemonics import mnemonics_dict
import sys

prepbufr_filename = sys.argv[1]
netcdf_filename = sys.argv[2]
if prepbufr_filename == netcdf_filename:
    raise IOError('cannot overwrite input prepbufr file')

hdstr='SID XOB YOB DHR TYP ELV SAID T29'
obstr='POB QOB TOB ZOB UOB VOB PWO MXGS HOVI CAT PRSS TDO PMO'
qcstr='PQM QQM TQM ZQM WQM NUL PWQ PMQ'
oestr='POE QOE TOE NUL WOE NUL PWE'

# read prepbufr file, write data to netcdf file.

nc = Dataset(netcdf_filename,'w',format='NETCDF4')
hd = nc.createDimension('header',len(hdstr.split())-1)
ob = nc.createDimension('obinfo',len(obstr.split()))
oe = nc.createDimension('oeinfo',len(oestr.split()))
qc = nc.createDimension('qcinfo',len(qcstr.split()))
nlevs = nc.createDimension('nlevs',255)

bufr = ncepbufr.open(prepbufr_filename)
while bufr.advance() == 0: # loop over messages.
    g = nc.createGroup(bufr.msg_type)
    if not g.variables.has_key('obdata'):
        g.setncattr('desc',mnemonics_dict[bufr.msg_type].rstrip())
        nobs = g.createDimension('nobs',None)
        hdrdata = g.createVariable('header',np.float32,('nobs','header'),zlib=True)
        stnid = g.createVariable('stationid',str,('nobs',))
        stnid.info = 'STATION IDENTIFICATION'
        for key in hdstr.split()[1:]:
            hdrdata.setncattr(key,mnemonics_dict[key])
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
        for key in obstr.split():
            obdata.setncattr(key,mnemonics_dict[key])
        obdata.missing_value=1.e11
        obdata.info = obstr
        for key in oestr.split():
            oedata.setncattr(key,mnemonics_dict[key])
        oedata.missing_value = 1.e11
        oedata.info = oestr
        for key in qcstr.split():
            qcdata.setncattr(key,mnemonics_dict[key])
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
