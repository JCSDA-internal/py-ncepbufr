from numpy.distutils.core  import setup, Extension
import os, sys, subprocess

# build fortran library if it does not yet exist.
if not os.path.isfile('src/libbufr.a'):
    strg = 'cd src; sh makebufrlib.sh'
    sys.stdout.write('executing "%s"\n' % strg)
    subprocess.call(strg,shell=True)

# interface for NCEP bufrlib.
ext_bufrlib = Extension(name  = '_bufrlib',
                sources       = ['src/_bufrlib.pyf'],
                libraries     = ['bufr'],
                library_dirs  = ['src'])

# module for reading GSI diagnostic files.
ext_diag_conv = Extension(name     = '_read_convobs',
                          sources  = ['src_diag/readconvobs.f90'])

if __name__ == "__main__":
    setup(name = 'py-ncepbufr',
          version           = "0.9.1",
          description       = "Python interface to NCEP bufrlib",
          author            = "Jeff Whitaker",
          author_email      = "jeffrey.s.whitaker@noaa.gov",
          url               = "http://github.com/jswhit/py-ncepbufr",
          ext_modules       = [ext_bufrlib,ext_diag_conv],
          packages          = ['ncepbufr','read_diag'],
          scripts           = ['utils/prepbufr2nc'],
          )
