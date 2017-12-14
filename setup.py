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

# modules for reading GSI diagnostic files.
ext_diag_conv = Extension(name     = '_read_convobs',
                          sources  = ['src_diag/readconvobs.f90'])
ext_diag_sat = Extension(name     = '_read_satobs',
                         sources  = ['src_diag/_readsatobs.pyf','src_diag/readsatobs.f90', 'src_diag/sparsearr.f90', 'src_diag/read_diag.f90'])
ext_diag_oz = Extension(name     = '_read_ozobs',
                          sources  = ['src_diag/readozobs.f90'])

if __name__ == "__main__":
    setup(name = 'py-ncepbufr',
          version           = "0.9.3",
          description       = "Python interface to NCEP bufrlib",
          author            = "Jeff Whitaker",
          author_email      = "jeffrey.s.whitaker@noaa.gov",
          url               = "http://github.com/jswhit/py-ncepbufr",
          ext_modules       = [ext_bufrlib,ext_diag_conv,ext_diag_sat,ext_diag_oz],
          packages          = ['ncepbufr','read_diag'],
          scripts           = ['utils/prepbufr2nc'],
          )
