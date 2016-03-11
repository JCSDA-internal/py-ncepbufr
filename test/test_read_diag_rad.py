import read_diag
import numpy as np
obsfile = 'diag_amsua_n15_ges.2016030100'
diag_rad = read_diag.diag_rad(obsfile,endian='big')
print 'total number of obs = ',diag_rad.nobs
diag_rad.read_obs()
# print o-f stats for one channel
ichan = 7
idxall = diag_rad.channel == ichan
nobsall = idxall.sum()
idx = np.logical_and(np.logical_and(diag_rad.channel == ichan, diag_rad.used == 1), diag_rad.oberr < 1.e9)
nobs = idx.sum()
fitsq = ((diag_rad.hx[idx]-diag_rad.obs[idx])**2).mean()
print diag_rad.obs[6],diag_rad.hx[6],diag_rad.biascorr[6],diag_rad.biaspred[1:,6].sum()
print nobs,'obs used for channel',ichan,'out of',nobsall,'rms o-f', np.sqrt(fitsq)
