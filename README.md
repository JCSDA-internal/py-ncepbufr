# py-ncepbufr
python interface to NCEP bufr library ([BUFRLIB](http://www.nco.ncep.noaa.gov/sib/decoders/BUFRLIB/toc/intro/)).

to install (numpy and fortran compiler required):

* python setup.py build
   - setup.py will try to build `src/libbufr.a` if it does not
already exist using `cd src; sh makebufrlib.sh`.  You can
edit `src/makebufrlib.sh` and run it manually if this step fails.
This requires a working fortran compiler that is known to numpy.f2py.
* python setup.py install

see http://jswhit.github.io/py-ncepbufr/ for docs.

see test/test.py for example usage.
