from numpy.distutils.core  import setup, Extension
import os, sys, subprocess

srcs_read_convobs =\
['src_diag/readconvobs.f90']

ext_conv = Extension(name     = '_read_convobs',
                     sources       = srcs_read_convobs)

if __name__ == "__main__":
    setup(name = 'read_diag',
          version           = "0.0.1",
          description       = "Modules and utilities for reading GFS output",
          author            = "Jeff Whitaker",
          author_email      = "jeffrey.s.whitaker@noaa.gov",
          url               = "http://github.com/jswhit/py-ncepbufr",
          ext_modules       = [ext_conv],
          packages          = ['read_diag'],
          )
