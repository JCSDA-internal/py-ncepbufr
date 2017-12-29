import tables
import sys
import numpy as np
h5_filename = sys.argv[1]
f = tables.open_file(h5_filename,'r')
table = f.root.amsua
print """
index sat_id sensor_id lat lon channel yyyymmddhhmmss tb tb_model biascorr
--------------------------------------------------------------------------
(obs thinned by GSI are excluded)
"""
for row in table.iterrows():
    if not np.isnan(row['tb_model']):
        print '%6i %46s %7.3f %7.3f %6.3f' %\
        (row.nrow,row['obid'],row['tb'],row['tb_model'],row['tb_biascorr'])
f.close()
