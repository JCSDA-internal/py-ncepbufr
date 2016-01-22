# py-ncepbufr
python interface to NCEP [BUFR](https://en.wikipedia.org/wiki/BUFR) library
([BUFRLIB](http://www.nco.ncep.noaa.gov/sib/decoders/BUFRLIB/toc/)).

to install ([numpy](http://numpy.org) and fortran compiler (preferably 
[gfortran](https://gcc.gnu.org/wiki/GFortran)) required):

* python setup.py build
   - setup.py will try to build `src/libbufr.a` if it does not
already exist using `cd src; sh makebufrlib.sh`. `src/makebufrlib.sh`
is set up to use [gfortran](https://gcc.gnu.org/wiki/GFortran) by default.  You can
edit `src/makebufrlib.sh` and run it manually if this step fails.
If you change the fortran compiler, you may have to add the 
flags `config_fc --fcompiler=<compiler name>` when setup.py is run
(see docs for [numpy.distutils] (http://docs.scipy.org/doc/numpy-dev/f2py/distutils.html)).
* python setup.py install

*Probably will not work on Windows!*

see http://jswhit.github.io/py-ncepbufr/ for docs.

see test/test.py for example usage.

utils/prepbufr2nc is a utility to convert [NCEP prepbufr](http://www.emc.ncep.noaa.gov/mmb/data_processing/prepbufr.doc/document.htm) files to netcdf format.

utils/nc2prepbufr does the reverse (netcdf back to prepbufr).
