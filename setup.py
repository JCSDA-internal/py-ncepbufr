from numpy.distutils.core  import setup, Extension
import os, sys, subprocess

# build fortran library if it does not yet exist.
bufrdir = os.environ.get('BUFRDIR')
if bufrdir:
    bufrlibdir = os.path.join(bufrdir,'lib')
    bufrincdir = os.path.join(bufrdir,'include')
    ext_bufrlib = Extension(name  = '_bufrlib',
                    sources = ['src/_bufrlib.pyf','src/fortran_open.f','src/fortran_close.f',],
                    libraries     = ['bufr'],
                    include_dirs  = [bufrincdir],
                    library_dirs  = [bufrlibdir])
elif not os.path.isfile('src/libbufr.a'):
    strg = 'cd src; sh makebufrlib.sh'
    sys.stdout.write('executing "%s"\n' % strg)
    subprocess.call(strg,shell=True)
    ext_bufrlib = Extension(name  = '_bufrlib',
                    sources       = ['src/_bufrlib.pyf'],
                    libraries     = ['bufr'],
                    library_dirs  = ['src'])

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
