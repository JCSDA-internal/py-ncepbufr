from netCDF4 import Dataset
import numpy as np
import os, sys, dateutils

msg = 'date1 date2 datapath runid hem outfile'
if len(sys.argv) < 6:
    print msg
    raise SystemExit

date1 = sys.argv[1] # date range
date2 = sys.argv[2]
datapath = sys.argv[3] # path to diag files.
runid = sys.argv[4] # suffix for diag file
hem = sys.argv[5] # NH,TR,SH,GL
outfile = sys.argv[6] # profile stats saved here
sondesonly = False # use only 120,132,220,221,232 (sondes,pibals,drops)
# if sondesonly False, aircraft, pibals and surface data included also

dates = dateutils.daterange(date1,date2,6)
deltap = 50.; pbot = 975
nlevs = 23
levs = np.zeros(nlevs, np.float)
levs1 = np.zeros(nlevs, np.float)
levs2 = np.zeros(nlevs, np.float)
levs[0:18] = pbot - deltap*np.arange(18)
levs1[0:18] = levs[0:18] + 0.5*deltap
levs2[0:18] = levs[0:18] - 0.5*deltap
levs1[18] = levs2[17]
levs2[18] = 70.; levs1[19] = 70.
levs2[19] = 50.; levs1[20] = 50.
levs2[20] = 30.; levs1[21] = 30.
levs2[21] = 10.; levs1[22] = 10.
levs2[22] = 0.
levs1[0] = 1200.
pbins = np.zeros(nlevs+1,np.float)
pbins[0:nlevs] = levs1; pbins[nlevs] = levs2[-1]
for nlev in range(18,nlevs):
    levs[nlev] = 0.5*(levs1[nlev]+levs2[nlev])

rms_wind = np.zeros(len(levs),np.float)
rms_temp = np.zeros(len(levs),np.float)
rms_humid = np.zeros(len(levs),np.float)
bias_temp = np.zeros(len(levs),np.float)
bias_humid = np.zeros(len(levs),np.float)
count_temp = np.zeros(len(levs),np.int)
count_humid = np.zeros(len(levs),np.int)
count_wind = np.zeros(len(levs),np.int)

#datapath2='/scratch3/BMC/gsienkf/whitaker/t1534_t574'

for date in dates:
    obsfile_uv = os.path.join(datapath,'%s/diag_conv_uv_ges.%s_%s.nc4' % (date,date,runid))
    obsfile_t  = os.path.join(datapath,'%s/diag_conv_t_ges.%s_%s.nc4' % (date,date,runid))
    obsfile_q  = os.path.join(datapath,'%s/diag_conv_q_ges.%s_%s.nc4' % (date,date,runid))
    nc_uv = Dataset(obsfile_uv); nc_t = Dataset(obsfile_t); nc_q = Dataset(obsfile_q)
    uv_code = nc_uv['Observation_Type'][:]
    t_code = nc_t['Observation_Type'][:]
    q_code = nc_q['Observation_Type'][:]
    uv_used = nc_uv['Analysis_Use_Flag'][:]
    t_used = nc_t['Analysis_Use_Flag'][:]
    q_used = nc_q['Analysis_Use_Flag'][:]
    uv_oberrinv = nc_uv['Errinv_Final'][:]
    t_oberrinv = nc_t['Errinv_Final'][:]
    q_oberrinv = nc_q['Errinv_Final'][:]
    uv_press = nc_uv['Pressure'][:]
    t_press = nc_t['Pressure'][:]
    q_press = nc_q['Pressure'][:]
    uv_lon = nc_uv['Longitude'][:]
    t_lon = nc_t['Longitude'][:]
    q_lon = nc_q['Longitude'][:]
    uv_lat = nc_uv['Latitude'][:]
    t_lat = nc_t['Latitude'][:]
    q_lat = nc_q['Latitude'][:]
    omf_u = nc_uv['u_Obs_Minus_Forecast_adjusted'][:]
    omf_v = nc_uv['v_Obs_Minus_Forecast_adjusted'][:]
    omf_t = nc_t['Obs_Minus_Forecast_adjusted'][:]
    omf_q = nc_q['Obs_Minus_Forecast_adjusted'][:]
    if sondesonly:
        insitu_wind = np.logical_or(uv_code == 220, # sondes
                                    uv.code == 232) # drops
        insitu_wind = np.logical_or(insitu_wind, uv_code == 221) # pibals
    else:
        insitu_wind = np.logical_and(uv_code >= 280, uv_code <= 282) #sfc
        # sones, pibals
        insitu_wind = np.logical_or(insitu_wind,\
                      np.logical_or(uv_code == 220, uv_code == 221)) 
        print 'sondes,pibals',np.logical_and(uv_code >= 220, uv_code <= 221).sum()
        # aircraft, drops
        insitu_wind = np.logical_or(insitu_wind,\
                      np.logical_and(uv_code >= 230, uv_code <= 235))
        print 'aircraft,drops',np.logical_and(uv_code >= 230, uv_code <= 235).sum()
        print 'drops',(uv_code == 232).sum()
    if sondesonly:
        insitu_temp = np.logical_or(t_code == 120, # sondes
                                    t_code == 132) # drops
        insitu_q = np.logical_or(q_code == 120, # sondes
                                 q_code == 132) # drops
    else:
        insitu_temp = np.logical_and(t_code >= 180, t_code <= 182) #sfc
        insitu_temp = np.logical_or(insitu_temp, t_code == 120) # sondes
        # aircraft, drops
        insitu_temp = np.logical_or(insitu_temp,\
                      np.logical_and(t_code >= 130, t_code <= 135))
        insitu_q = np.logical_and(q_code >= 180, q_code <= 182) #sfc
        insitu_q = np.logical_or(insitu_q, q_code == 120) # sondes
        # aircraft, drops
        insitu_q = np.logical_or(insitu_q,\
                      np.logical_and(q_code >= 130, q_code <= 135))
    # consider this of if used flag is 1, inverse oberr is < 1.e-5 and a valid pressure level is included
    uv_used = np.logical_and(uv_used == 1, uv_oberrinv > 1.e-5)
    uv_used = np.logical_and(uv_used, np.isfinite(uv_press))
    insitu_wind = np.logical_and(insitu_wind,uv_used)
    t_used = np.logical_and(t_used == 1, t_oberrinv > 1.e-5)
    t_used = np.logical_and(t_used, np.isfinite(t_press))
    insitu_temp = np.logical_and(insitu_temp,t_used)
    q_used = np.logical_and(q_used == 1, q_oberrinv > 1.e-5)
    q_used = np.logical_and(q_used, np.isfinite(q_press))
    insitu_q = np.logical_and(insitu_q,q_used)
    if hem == 'NH':
        uv_latcond = uv_lat > 20. 
        t_latcond = t_lat > 20. 
        q_latcond = q_lat > 20. 
    elif hem == 'SH':
        uv_latcond = uv_lat < -20.
        t_latcond = t_lat < -20.
        q_latcond = q_lat < -20.
    elif hem == 'TR':
        uv_latcond = np.logical_and(uv_lat <= 20.,uv_lat >= -20)
        t_latcond = np.logical_and(t_lat <= 20.,t_lat >= -20)
        q_latcond = np.logical_and(q_lat <= 20.,q_lat >= -20)
    if hem in ['NH','TR','SH']:
        indxuv = np.logical_and(insitu_wind,uv_latcond)
        indxt = np.logical_and(insitu_temp,t_latcond)
        indxq = np.logical_and(insitu_q,q_latcond)
    else:
        indxuv = insitu_wind; indxt = insitu_temp; indxq = insitu_q
    omf_u = omf_u[indxuv]
    omf_v = omf_v[indxuv]
    omf_t = omf_t[indxt]
    omf_q = omf_q[indxq]
    press_u = uv_press[indxuv]
    press_t = t_press[indxt]
    press_q = q_press[indxq]
    # compute innovation stats for temperature.
    pindx =  np.digitize(press_t,pbins)-1
    # check on pindx calculation
    #for n in range(len(press_t)):
    #    ip = pindx[n]
    #    p = press_t[n]
    #    if not (p < levs1[ip] and p >= levs2[ip]):
    #        print p, levs2[ip], levs1[ip]
    #        raise IndexError('wind p mismatch')
    rms_temp += np.bincount(pindx,minlength=nlevs,weights=omf_t**2)
    bias_temp += np.bincount(pindx,minlength=nlevs,weights=omf_t)
    counts, bin_edges = np.histogram(press_t,pbins[::-1])
    count_temp += counts[::-1]
    rms_temp_mean = np.sqrt(np.bincount(pindx,minlength=nlevs,weights=omf_t**2)/counts[::-1])[0:18].mean()
    # compute innovation stats for humidity.
    pindx =  np.digitize(press_q,pbins)-1
    # check on pindx calculation
    #for n in range(len(press_q)):
    #    ip = pindx[n]
    #    p = press_q[n]
    #    if not (p < levs1[ip] and p >= levs2[ip]):
    #        print p, levs2[ip], levs1[ip]
    #        raise IndexError('wind p mismatch')
    rms_humid += np.bincount(pindx,minlength=nlevs,weights=omf_q**2)
    bias_humid += np.bincount(pindx,minlength=nlevs,weights=omf_q)
    counts, bin_edges = np.histogram(press_q,pbins[::-1])
    counts = np.where(counts == 0, -1, counts)
    count_humid += counts[::-1]
    rms_humid_mean = np.sqrt(np.bincount(pindx,minlength=nlevs,weights=omf_q**2)/counts[::-1])[0:18].mean()
    # compute innovation stats for wind.
    pindx =  np.digitize(press_u,pbins)-1
    # check on pindx calculation
    #for n in range(len(press_u)):
    #    ip = pindx[n]
    #    p = press_u[n]
    #    if not (p < levs1[ip] and p >= levs2[ip]):
    #        print p, levs2[ip], levs1[ip]
    #        raise IndexError('wind p mismatch')
    rms_wind += np.bincount(pindx,minlength=nlevs,weights=np.sqrt(omf_u**2+omf_v**2))
    counts, bin_edges = np.histogram(press_u,pbins[::-1])
    count_wind += counts[::-1]
    rms_wind_mean = (np.bincount(pindx,minlength=nlevs,weights=np.sqrt(omf_u**2+omf_v**2))/counts[::-1])[0:18].mean()
    print 'vertical mean:',date, rms_wind_mean, rms_temp_mean, rms_humid_mean

rms_wind = rms_wind/count_wind
rms_temp = np.sqrt(rms_temp/count_temp)
bias_temp = bias_temp/count_temp
rms_humid = np.sqrt(rms_humid/count_humid)
bias_humid = bias_humid/count_humid

fout = open(outfile,'w')
fout.write('# %s %s %s %s-%s\n' % (datapath,runid,hem,date1,date2))
fout.write('# press wind_count wind_rms temp_count temp_rms temp_bias humid_rmsx1000 humid_biasx1000\n')
fout.write('# 1000-0 %10i %7.4f %10i %7.4f %7.4f %10i %7.4f %7.4f\n' % (count_wind.sum(), rms_wind.mean(), count_temp.sum(), rms_temp.mean(), bias_temp.mean(), count_humid.sum(), 1000*rms_humid.mean(), 1000*bias_humid.mean()))
for n,p in enumerate(levs):
    fout.write('%8.2f %10i %7.4f %10i %7.4f %7.4f %10i %7.4f %7.4f\n' % (p,count_wind[n],rms_wind[n],count_temp[n],rms_temp[n],bias_temp[n],count_humid[n],1000*rms_humid[n],1000*bias_humid[n]))
fout.close()
