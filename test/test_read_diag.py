import read_diag
import numpy as np
obsfile = 'diag_conv_ges.2015102700'
diag_conv = read_diag.diag_conv(obsfile,endian='big')
print 'total number of obs = ',diag_conv.nobs
diag_conv.read_obs()
# print o-f stats for ps obs
# all ship ps obs used in assimilation
indxps = np.logical_and(diag_conv.obtype == 'ps', diag_conv.used == 1)
indxps = np.logical_and(indxps, diag_conv.code == 180)
nobsps = indxps.sum()
fitsq = ((diag_conv.hx[indxps]-diag_conv.obs[indxps])**2).mean()
print nobsps, np.sqrt(fitsq)

