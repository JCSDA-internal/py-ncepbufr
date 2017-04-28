* `amsuabufr2h5`: script to convert bufr to pytables hdf5 file (`python amsuabufr2h5 amsuabufr amsua.h5`)

* `mergediag_amsuah5`:  script to merge GSI diagnostic file information into amsua hdf5 file  
  (`python mergediag_amsuah5 amsua.h5`)

* `print_amsua.py`: print info from merged file (`python print_amsua.py amsua.h5`).

* `inv_amsua.py`: inventory of satellite ids in amsua hdf5 file (`python inv_amsua.py amsua.h5`).

* `utils.py`:  some utilities used in the above scripts.

screenshot of [vitables](http://vitables.org) showing structure of `amsua.h5` file.

![amsua.h5](vitables.png?raw=true "AMSUA pytables file")
