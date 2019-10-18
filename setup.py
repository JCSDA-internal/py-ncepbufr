from numpy.distutils.core  import setup, Extension
import os, sys, subprocess

# check env vars for path to pre-build bufr lib
bufrdir = os.environ.get('bufrlib_ROOT') # check bufrlib_ROOT/BUFRLIB_ROOT first
if not bufrdir:
    bufrdir = os.environ.get('BUFRLIB_ROOT')
if not bufrdir:
    bufrdir = os.environ.get('bufrlib_PATH') # fall back on bufrlib_PATH/BUFRLIB_PATH
    if not bufrdir:
        bufrdir = os.environ.get('BUFRLIB_PATH')
# if path to bufr lib not specified by env var, build from source
if bufrdir:
    bufrlibdir = os.path.join(bufrdir,'lib')
    bufrincdir = os.path.join(bufrdir,'include')
    ext_bufrlib = Extension(name  = '_bufrlib',
                    sources = ['src/_bufrlib.pyf','src/fortran_open.f','src/fortran_close.f'],
                    libraries     = ['bufr'],
                    include_dirs  = [bufrincdir],
                    library_dirs  = [bufrlibdir])
else:
    ext_bufrlib = Extension(name  = '_bufrlib',
                    sources       = ['src/_bufrlib.pyf'],
                    libraries     = ['bufr'],
                    library_dirs  = ['src'])
    if not os.path.isfile('src/libbufr.a'):
        strg = 'cd src; sh makebufrlib.sh'
        sys.stdout.write('executing "%s"\n' % strg)
        subprocess.call(strg,shell=True)

if __name__ == "__main__":
    setup(name = 'py-ncepbufr',
          version           = "1.1.1",
          description       = "Python interface to NCEP bufrlib",
          author            = "Jeff Whitaker",
          author_email      = "jeffrey.s.whitaker@noaa.gov",
          url               = "http://github.com/jswhit/py-ncepbufr",
          ext_modules       = [ext_bufrlib],
          packages          = ['ncepbufr'],
          scripts           = ['utils/prepbufr2nc'],
          )
