export FC="gcc -O2 -fPIC -DDYNAMIC_ALLOCATION"
export CC="gfortran -O2 -fPIC -DUNDERSCORE"
/bin/rm -f *.o *.a *.mod
$CC -c `./getdefflags_C.sh` *.c
$FC -c `./getdefflags_F.sh` modv*.F moda*.F `ls -1 *.F *.f | grep -v "mod[av]_"`
ar crv libbufr.a *.o
