import pandas, sys
h5_filename = sys.argv[1]
table_name = sys.argv[2]
df = pandas.read_hdf(h5_filename,table_name)
print df
