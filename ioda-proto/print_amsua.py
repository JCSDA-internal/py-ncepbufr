import tables
import sys
import numpy as np
h5_filename = sys.argv[1]
f = tables.open_file(h5_filename,'a')
table = f.root.amsua
for row in table.iterrows():
    if not np.isnan(row['tb_model']):
        print row.nrow,row['obid'],row['tb'],row['tb_model'],row['tb_biascorr']
