# py-ncepbufr
python interface to NCEP [BUFR](https://en.wikipedia.org/wiki/BUFR) library
([BUFRLIB](https://www.emc.ncep.noaa.gov/index.php?branch=BUFRLIB)).

to install ([numpy](http://numpy.org) and fortran compiler (preferably 
[gfortran](https://gcc.gnu.org/wiki/GFortran)) required):

* python setup.py build
   - setup.py will try to build `src/libbufr.a` if it does not
already exist using `cd src; sh makebufrlib.sh`. `src/makebufrlib.sh`
is set up to use [gfortran](https://gcc.gnu.org/wiki/GFortran) by default.  You can
edit `src/makebufrlib.sh` and run it manually if this step fails.
If you change the fortran compiler, you may have to add the 
flags `config_fc --fcompiler=<compiler name>` when setup.py is run
(see docs for [numpy.distutils](https://docs.scipy.org/doc/numpy/f2py/distutils.html)).
If you have built and installed the bufr library from https://github.com/JCSDA/BUFRLIB, 
you can set the `BUFRLIB_ROOT` environment variable to point to where you installed it, and
setup.py should use this one instead of building the library from the included source.
However, you have to make sure that cmake (when building bufrlib) and numpy.distutils (when building 
the python extension) are using the same fortran compiler.  Since numpy.distutils uses gfortran by
default, one way to do this is to set FC=gfortran before building bufrlib. The other option is to
specify the fortran compiler for python to use via `python setup.py build config_fc --fcompiler=<compiler name>`
(`python setup.py build --help-fcompiler` lists the names of available compilers).
* python setup.py install

*Probably will not work on Windows!*

to test, run `test/test.py`. Note that `git-lfs` must be installed and initialized
to checkout test data in `test/data`. If no errors are raised, the tests pass.

a Jupyter notebook from the 2018 [NOAA Modelling Fair](http:polar.ncep.noaa.gov/ngmmf_python) is available at [`test/Python_tutorial_bufr.ipynb`](https://nbviewer.jupyter.org/github/JCSDA/py-ncepbufr/blob/master/test/Python_tutorial_bufr.ipynb).

full API documentation in [`docs/ncepbufr/index.html`](http://htmlpreview.github.io/?https://github.com/JCSDA/py-ncepbufr/blob/master/docs/ncepbufr/index.html).
