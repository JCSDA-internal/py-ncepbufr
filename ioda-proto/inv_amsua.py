import tables
import sys
import numpy as np
from utils import sat_id_dict
sat_id_dict_inv = {v: k for k, v in sat_id_dict.items()}
h5_filename = sys.argv[1]
f = tables.open_file(h5_filename,'r')
table = f.root.amsua
satids = table.col('sat_id').tolist()
seen = set()
uniq = [sat_id_dict_inv[x]+' ' for x in satids if x not in seen and not seen.add(x)]
print('satellite ids in file: %s' % ''.join(uniq))
f.close()
