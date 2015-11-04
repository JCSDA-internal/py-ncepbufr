import read_diag
import numpy as np
obsfile = 'diag_conv_ges.2015102700'
diag_conv = read_diag.diag_conv(obsfile)
print 'total number of obs = ',diag_conv.nobs
diag_conv.read_obs()
# print o-f stats for ps obs
print diag_conv.obtype
# all ps obs
indxps = np.logical_and(diag_conv.obtype == 'ps', diag_conv.oberr < 1.e3)
# ship ps obs
indxps = np.logical_and(indxps, diag_conv.code == 180)
nobsps = indxps.sum()
fitsq = ((diag_conv.hx[nobsps]-diag_conv.obs[nobsps])**2).mean()
print nobsps, np.sqrt(fitsq)

