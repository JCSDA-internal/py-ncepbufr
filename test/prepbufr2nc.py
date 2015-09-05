import ncepbufr
import numpy as np
from netCDF4 import Dataset
from prepbufr_mnemonics import mnemonics_dict
import sys

# input and output file names from command line args.
prepbufr_filename = sys.argv[1]
netcdf_filename = sys.argv[2]
if prepbufr_filename == netcdf_filename:
    raise IOError('cannot overwrite input prepbufr file')

# mnemonics to extract data from prepbufr file.
hdstr='SID XOB YOB DHR TYP ELV SAID T29'
obstr='POB QOB TOB ZOB UOB VOB PWO MXGS HOVI CAT PRSS TDO PMO'
qcstr='PQM QQM TQM ZQM WQM PWQ PMQ'
oestr='POE QOE TOE NUL WOE PWE'

# skip these report types
skiptypes = []
#skiptypes = ['SATWND']

# open netcdf file
nc = Dataset(netcdf_filename,'w',format='NETCDF4')
hd = nc.createDimension('header',len(hdstr.split())-1)
ob = nc.createDimension('obinfo',len(obstr.split()))
oe = nc.createDimension('oeinfo',len(oestr.split()))
qc = nc.createDimension('qcinfo',len(qcstr.split()))
nm = nc.createDimension('msg',None)
msg_date =\
nc.createVariable('msg_date',np.int32,('msg',),fill_value=-1)
msg_date.info = 'BUFR MESSAGE DATE'
tank_date =\
nc.createVariable('tank_date',np.int32,('msg',),fill_value=-1)
tank_date.info = 'BUFR TANK RECEIPT DATE'
nlevs = nc.createDimension('nlevs',200)

# open prepbufr file.
bufr = ncepbufr.open(prepbufr_filename)

# read prepbufr data, write to netcdf.
while bufr.advance() == 0: # loop over messages.
    if bufr.msg_type in skiptypes: continue
    # each message type in a separate group.
    g = nc.createGroup(bufr.msg_type)
    nmsg = bufr.msg_counter
    msg_date[nmsg] = bufr.msg_date
    if bufr.receipt_time is not None:
        tank_date[nmsg] = bufr.receipt_time
    else:
        tank_date[nmsg] = -1
    if not g.variables.has_key('obdata'):
        g.setncattr('desc',mnemonics_dict[bufr.msg_type].rstrip())
        # number of obs is the unlimited dimension.
        nobs = g.createDimension('nobs',None)
        hdrdata =\
        g.createVariable('header',np.float32,('nobs','header'),fill_value=bufr.missing_value)
        stnid = g.createVariable('stationid',str,('nobs',))
        stnid.info = 'STATION IDENTIFICATION'
        # retain association of ob data with bufr message number.
        msgnum = g.createVariable('msgnum',np.int32,('nobs',))
        msgnum.info = 'BUFR MESSAGE NUMBER'
        for key in hdstr.split()[1:]:
            hdrdata.setncattr(key,mnemonics_dict[key])
        hdrdata.info = hdstr[4:]
        if bufr.msg_type in ['RASSDA','VADWND','PROFLR','ADPUPA']:
            # these message types are multi-level
            obdata =\
            g.createVariable('obdata',np.float32,('nobs','obinfo','nlevs'),fill_value=bufr.missing_value)
            oedata =\
            g.createVariable('oberr',np.float32,('nobs','oeinfo','nlevs'),fill_value=bufr.missing_value)
            qcdata =\
            g.createVariable('qcinfo',np.float32,('nobs','qcinfo','nlevs'),fill_value=bufr.missing_value)
        else:
            # single level message types.
            obdata = g.createVariable('obdata',np.float32,('nobs','obinfo'))
            oedata = g.createVariable('oberr',np.float32,('nobs','oeinfo'))
            qcdata = g.createVariable('qcinfo',np.float32,('nobs','qcinfo'))
        # mnemonic descriptions as variable attributes.
        for key in obstr.split():
            obdata.setncattr(key,mnemonics_dict[key])
        obdata.info = obstr
        for key in oestr.split():
            oedata.setncattr(key,mnemonics_dict[key])
        oedata.info = oestr
        for key in qcstr.split():
            qcdata.setncattr(key,mnemonics_dict[key])
        qcdata.info = qcstr
    while bufr.load_subset() == 0: # loop over subsets in message.
        hdr = bufr.read_subset(hdstr).squeeze()
        obs = bufr.read_subset(obstr)
        qc  = bufr.read_subset(qcstr)
        err = bufr.read_subset(oestr)
        n = obs.shape[-1]
        nob = g['header'].shape[0]
        # station id in a separate variables.
        g['header'][nob] = hdr.squeeze()[1:]
        g['stationid'][nob] = hdr[0].tostring()
        # keep track of message number
        g['msgnum'][nob] = bufr.msg_counter
        if bufr.msg_type in ['RASSDA','VADWND','PROFLR','ADPUPA']:
            # multi-level data
            g['obdata'][nob,:,:n] = obs
            g['oberr'][nob,:,:n]  = err
            g['qcinfo'][nob,:,:n] = qc
        else:
            # single level data
            g['obdata'][nob,:] = obs.squeeze()
            g['oberr'][nob,:]  = err.squeeze()
            g['qcinfo'][nob,:] = qc.squeeze()
    nc.sync() # write data to file.

# close files.
bufr.close()
nc.close()
