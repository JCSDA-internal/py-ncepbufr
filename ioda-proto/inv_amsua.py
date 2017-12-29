import tables
import sys
import numpy as np
from utils import sat_id_dict
sat_id_dict_inv = {v: k for k, v in sat_id_dict.items()}
h5_filename = sys.argv[1]
f = tables.open_file(h5_filename,'r')
table = f.root.amsua
satids = table.col('sat_id')
satids_uniq = np.unique(satids)
satids_uniq = [sat_id_dict_inv[s]+" " for s in satids_uniq]
print('satellite ids in file: %s' % ''.join(satids_uniq))
f.close()
