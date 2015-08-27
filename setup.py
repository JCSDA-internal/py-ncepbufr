# use "config_fc --fcompiler=<compiler name> install" to build and install with
# another fortran compiler.

from numpy.distutils.core  import setup, Extension
import os, sys

ext = Extension(name          = '_bufrlib',
                sources       = ['src/_bufrlib.pyf'],
                libraries     = ['bufr'],
                library_dirs  = ['src'])

if __name__ == "__main__":
    setup(name = 'py-ncepbufr',
          version           = "0.0.1",
          description       = "Python interface to NCEP bufrlib",
          author            = "Jeff Whitaker",
          author_email      = "jeffrey.s.whitaker@noaa.gov",
          url               = "http://github.com/jswhit/py-ncepbufr",
          ext_modules       = [ext],
          packages          = ['ncepbufr'],
          )
