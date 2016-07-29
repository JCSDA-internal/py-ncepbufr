import read_diag
import numpy as np
import os, sys, dateutils

date1 = sys.argv[1] # date range
date2 = sys.argv[2]
datapath = sys.argv[3] # path to diag files.
runid = sys.argv[4] # suffix for diag file
hem = sys.argv[5] # NH,TR,SH,GL
outfile = sys.argv[6] # profile stats saved here
endian = 'little'
if len(sys.argv) > 7: # is diag file big endian?
    endian = sys.argv[7]
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
bias_temp = np.zeros(len(levs),np.float)
count_temp = np.zeros(len(levs),np.int)
count_wind = np.zeros(len(levs),np.int)
for date in dates:
    obsfile = os.path.join(datapath,'%s/diag_conv_ges.%s_%s' % (date,date,runid))
    print obsfile
    diag_conv = read_diag.diag_conv(obsfile,endian=endian)
    diag_conv.read_obs()
    if sondesonly:
        insitu_wind = np.logical_or(diag_conv.code == 220, # sondes
                                    diag_conv.code == 232) # drops
        insitu_wind = np.logical_or(insitu_wind, diag_conv.code == 221) # pibals
    else:
        insitu_wind = np.logical_and(diag_conv.code >= 280, diag_conv.code <= 282) #sfc
        # sones, pibals
        insitu_wind = np.logical_or(insitu_wind,\
                      np.logical_or(diag_conv.code == 220, diag_conv.code == 221)) 
        # aircraft, drops
        insitu_wind = np.logical_or(insitu_wind,\
                      np.logical_and(diag_conv.code >= 230, diag_conv.code <= 235))
    if sondesonly:
        insitu_temp = np.logical_or(diag_conv.code == 120, # sondes
                                    diag_conv.code == 132) # drops
    else:
        insitu_temp = np.logical_and(diag_conv.code >= 180, diag_conv.code <= 182) #sfc
        insitu_temp = np.logical_or(insitu_temp, diag_conv.code == 120) # sondes
        # aircraft, drops
        insitu_temp = np.logical_or(insitu_temp,\
                      np.logical_and(diag_conv.code >= 130, diag_conv.code <= 135))
    indxt=np.logical_and(diag_conv.obtype=='  t',insitu_temp)
    indxu=np.logical_and(diag_conv.obtype=='  u',insitu_wind)
    indxv=np.logical_and(diag_conv.obtype=='  v',insitu_wind)
    # consider this of if used flag is 1, oberr is < 1.e5 and a valid pressure level is included
    used = np.logical_and(diag_conv.used == 1, diag_conv.oberr < 1.e5)
    used = np.logical_and(used, np.isfinite(diag_conv.press))
    indxu = np.logical_and(indxu,used)
    indxv = np.logical_and(indxv,used)
    indxt = np.logical_and(indxt,used)
    if hem == 'NH':
        latcond = diag_conv.lat > 20. 
    elif hem == 'SH':
        latcond = diag_conv.lat < -20.
    elif hem == 'TR':
        latcond = np.logical_and(diag_conv.lat <= 20.,diag_conv.lat >= -20)
    if hem in ['NH','TR','SH']:
        indxu = np.logical_and(indxu,latcond)
        indxv = np.logical_and(indxv,latcond)
        indxt = np.logical_and(indxt,latcond)
    if not (indxu.sum() == indxv.sum()) or \
       not np.all(np.flatnonzero(indxu)+1 == np.flatnonzero(indxv)):
       raise IndexError('error in u,v indices')
    omf_u = diag_conv.hx[indxu]-diag_conv.obs[indxu] 
    omf_v = diag_conv.hx[indxv]-diag_conv.obs[indxv] 
    omf_t = diag_conv.hx[indxt]-diag_conv.obs[indxt] 
    press_u = diag_conv.press[indxu]
    press_t = diag_conv.press[indxt]
    # compute innovation stats for temperature.
    pindx =  np.digitize(press_t,pbins)-1
    # check on pindx calculation
    #for n in range(len(press_t)):
    #    ip = pindx[n]
    #    p = press_t[n]
    #    if not (p < levs1[ip] and p >= levs2[ip]):
    #        print p, levs2[ip], levs1[ip]
    #        raise IndexError('wind p mismatch')
    rms_temp += np.bincount(pindx,weights=omf_t**2)
    bias_temp += np.bincount(pindx,weights=omf_t)
    counts, bin_edges = np.histogram(press_t,pbins[::-1])
    count_temp += counts[::-1]
    # compute innovation stats for wind.
    pindx =  np.digitize(press_u,pbins)-1
    # check on pindx calculation
    #for n in range(len(press_u)):
    #    ip = pindx[n]
    #    p = press_u[n]
    #    if not (p < levs1[ip] and p >= levs2[ip]):
    #        print p, levs2[ip], levs1[ip]
    #        raise IndexError('wind p mismatch')
    rms_wind += np.bincount(pindx,weights=np.sqrt(omf_u**2+omf_v**2))
    counts, bin_edges = np.histogram(press_u,pbins[::-1])
    count_wind += counts[::-1]

rms_wind = rms_wind/count_wind
rms_temp = np.sqrt(rms_temp/count_temp)
bias_temp = bias_temp/count_temp

fout = open(outfile,'w')
fout.write('# %s %s %s %s-%s\n' % (datapath,runid,hem,date1,date2))
fout.write('# press wind_count wind_rms temp_count temp_rms temp_bias\n')
fout.write('# 1000-0 %10i %7.4f %10i %7.4f %7.4f\n' % (count_wind.sum(), rms_wind.mean(), count_temp.sum(), rms_temp.mean(), bias_temp.mean()))
for n,p in enumerate(levs):
    fout.write('%8.2f %10i %7.4f %10i %7.4f %7.4f\n' % (p,count_wind[n],rms_wind[n],count_temp[n],rms_temp[n],bias_temp[n]))
fout.close()
