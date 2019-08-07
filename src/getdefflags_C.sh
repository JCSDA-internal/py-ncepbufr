#!/bin/sh
    
#-------------------------------------------------------------------------------
#     Set define flags for the C compiler.

cflags_defs="-DDYNAMIC_ALLOCATION"

#-------------------------------------------------------------------------------
#     Use the bufrlib.prm header file to generate a few additional corresponding
#     define flags for the C compiler.

for bprm in MAXNC MXNAF
do
  bprmval=`grep " ${bprm} = " bufrlib.prm | cut -f2 -d= | cut -f2 -d" "`
  cflags_defs="${cflags_defs} -D${bprm}=${bprmval}"
done

#-------------------------------------------------------------------------------
#     Print (to standard output) the define flags for the C compiler.
echo ${cflags_defs}
