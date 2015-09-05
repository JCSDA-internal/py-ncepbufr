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
nhdd = len(hd)
ob = nc.createDimension('obinfo',len(obstr.split()))
nobd = len(ob)
oe = nc.createDimension('oeinfo',len(oestr.split()))
noed = len(oe)
qc = nc.createDimension('qcinfo',len(qcstr.split()))
nqcd = len(qc)
levs = nc.createDimension('nlevs',200)
nlevs = len(levs)

# chunksizes for netcdf
nobschunk = 10; nobschunk1 = 100

# open prepbufr file.
bufr = ncepbufr.open(prepbufr_filename)

# find number of messages, obs for each message type in bufr file.
typedict = {}
while bufr.advance() == 0: # loop over messages.
    if bufr.msg_type in skiptypes: continue
    if bufr.msg_type not in typedict.keys():
        typedict[bufr.msg_type] = 0
    while bufr.load_subset() == 0: # loop over subsets in message.
        typedict[bufr.msg_type] += 1
nmsg = bufr.msg_counter
bufr.rewind()

# create some more variables in the netcdf file (that pertain to messages).
nm = nc.createDimension('msg',nmsg)
msg_date =\
nc.createVariable('msg_date',np.int32,('msg',),fill_value=-1,zlib=True)
msg_date.info = 'BUFR MESSAGE DATE'
tank_date =\
nc.createVariable('tank_date',np.int32,('msg',),fill_value=-1,zlib=True)
tank_date.info = 'BUFR TANK RECEIPT DATE'

# read prepbufr data, write to netcdf.
nobsdict = {}
obs2 = bufr.missing_value*np.ones((nobd,nlevs),np.float)
err2 = bufr.missing_value*np.ones((noed,nlevs),np.float)
qc2 = bufr.missing_value*np.ones((nqcd,nlevs),np.float)
while bufr.advance() == 0: # loop over messages.
    if bufr.msg_type in skiptypes: continue
    # nobsdict used to keep track of number of obs written
    # for each message type.
    if bufr.msg_type not in nobsdict.keys():
        nobsdict[bufr.msg_type] = -1
    nmsg = bufr.msg_counter
    msg_date[nmsg] = bufr.msg_date
    if bufr.receipt_time is not None:
        tank_date[nmsg] = bufr.receipt_time
    else:
        tank_date[nmsg] = -1
    # each message type in a separate group.
    if bufr.msg_type not in nc.groups:
        g = nc.createGroup(bufr.msg_type)
        g.setncattr('desc',mnemonics_dict[bufr.msg_type].rstrip())
        # number of obs is the unlimited dimension.
        nobsd = g.createDimension('nobs',typedict[bufr.msg_type])
        # chunksize should not be greater than the number of obs.
        nobs_chunk1 = min(len(nobsd),nobschunk1)
        nobs_chunk = min(len(nobsd),nobschunk)
        hdrdata =\
        g.createVariable('header',np.float32,('nobs','header'),fill_value=bufr.missing_value,zlib=True,chunksizes=(nobs_chunk1,nhdd))
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
            g.createVariable('obdata',np.float32,('nobs','obinfo','nlevs'),fill_value=bufr.missing_value,zlib=True,chunksizes=(nobs_chunk,nobd,nlevs))
            oedata =\
            g.createVariable('oberr',np.float32,('nobs','oeinfo','nlevs'),fill_value=bufr.missing_value,zlib=True,chunksizes=(nobs_chunk,noed,nlevs))
            qcdata =\
            g.createVariable('qcinfo',np.float32,('nobs','qcinfo','nlevs'),fill_value=bufr.missing_value,zlib=True,chunksizes=(nobs_chunk,nqcd,nlevs))
        else:
            # single level message types.
            obdata =\
            g.createVariable('obdata',np.float32,('nobs','obinfo'),fill_value=bufr.missing_value,zlib=True,chunksizes=(nobs_chunk1,nobd))
            oedata =\
            g.createVariable('oberr',np.float32,('nobs','oeinfo'),fill_value=bufr.missing_value,zlib=True,chunksizes=(nobs_chunk1,noed))
            qcdata =\
            g.createVariable('qcinfo',np.float32,('nobs','qcinfo'),fill_value=bufr.missing_value,zlib=True,chunksizes=(nobs_chunk1,nqcd))
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
    # lists to hold data from each subset
    hdrarr = []; obsarr = []; qcarr = []; errarr = []; stnidarr = []
    while bufr.load_subset() == 0: # loop over subsets in message.
        hdr = bufr.read_subset(hdstr).squeeze()
        obs = bufr.read_subset(obstr)
        qc  = bufr.read_subset(qcstr)
        err = bufr.read_subset(oestr)
        nl = obs.shape[-1] # number of levels in data.
        nobsdict[bufr.msg_type] += 1 # ob number for this message type.
        # station id in a separate variables.
        hdrarr.append(hdr.squeeze()[1:])
        stnidarr.append(hdr[0].tostring())
        if bufr.msg_type in ['RASSDA','VADWND','PROFLR','ADPUPA']:
            # multi-level data.
            obs2[:] = bufr.missing_value; obs2[:,:nl] = obs
            obsarr.append(obs2)
            err2[:] = bufr.missing_value; err2[:,:nl] = err
            errarr.append(err2)
            qc2[:] = bufr.missing_value; qc2[:,:nl] = qc
            qcarr.append(qc2)
        else:
            # single level data.
            obsarr.append(obs.squeeze())
            errarr.append(err.squeeze())
            qcarr.append(qc.squeeze())
    # make lists into arrays.
    obsarr = np.array(obsarr)
    errarr = np.array(errarr)
    qcarr = np.array(qcarr)
    hdrarr = np.array(hdrarr)
    stnidarr = np.array(stnidarr)
    nob = nobsdict[bufr.msg_type]
    nob1 = nob-bufr.subsets+1
    #print bufr.msg_type,bufr.msg_counter,bufr.subsets,nob1,nob+1
    # write all the data from subset.
    g['header'][nob1:nob+1] = hdrarr
    g['obdata'][nob1:nob+1] = obsarr
    g['oberr'][nob1:nob+1]  = errarr
    g['qcinfo'][nob1:nob+1] = qcarr
    g['stationid'][nob1:nob+1] = stnidarr
    # keep track of message number
    g['msgnum'][nob1:nob+1] = bufr.msg_counter
    nc.sync() # dump data to disk.

# close files.
bufr.close(); nc.close()
