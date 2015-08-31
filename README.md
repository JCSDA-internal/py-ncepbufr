# py-ncepbufr
python interface to NCEP bufr library ([BUFRLIB](http://www.nco.ncep.noaa.gov/sib/decoders/BUFRLIB/toc/intro/)).

to install (fortran compiler required):

1) build fortran library
   - cd src, sh makefile.sh
2) build python module
   - python setup.py build
   - python setup.py install

see http://jswhit.github.io/py-ncepbufr/ for docs.

see test/test.py for example usage.
