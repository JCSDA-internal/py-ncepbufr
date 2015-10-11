#!/bin/sh
###############################################################
#
#   PURPOSE:   This script uses the make utility to update the BUFR
#              archive libraries (libbufr*.a).
#              It first reads a list of source files in the library and
#              then generates a makefile used to update the archive
#              libraries.  The make command is then executed for each
#              archive library, where the archive library name and
#              compilation flags are passed to the makefile through
#              environment variables.
#
#   REMARKS:   Only source files that have been modified since the last
#              library update are recompiled and replaced in the object
#              archive libraries.  The make utility determines this
#              from the file modification times.
#
#              New source files are also compiled and added to the object
#              archive libraries.
#
###############################################################

export FC=gfortran
export CC=gcc
#CPPFLAGS=" -P -traditional-cpp -C"
CPPFLAGS=" -P -traditional-cpp"

#-------------------------------------------------------------------------------
#     Determine the byte-ordering scheme used by the local machine.

cat > endiantest.c << ENDIANTEST

void fill(p, size) char *p; int size; {
	char *ab= "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
	int i;

	for (i=0; i<size; i++) p[i]= ab[i];
}

void endian(byte_size) int byte_size; {
	int j=0;
	unsigned int mask, i, c;

	mask=0;
	for (i=1; i<=(unsigned)byte_size; i++) mask= (mask<<1)|1;
	fill((char *)&j, (int) sizeof(j));
	for (i=1; i<=sizeof(j); i++) {
	    c=((j>>(byte_size*(sizeof(j)-i)))&mask);
	    putchar(c==0 ? '?' : (char)c);
	}
	printf("\n");
}

int cprop() {
	/* Properties of type char */
	char c;
	int byte_size;

	c=1; byte_size=0;
	do { c<<=1; byte_size++; } while(c!=0);

	return byte_size;
}

main()
{
	int byte_size;

	byte_size= cprop();
	endian(byte_size);
}
ENDIANTEST

$CC -o endiantest endiantest.c

if [ `./endiantest | cut -c1` = "A" ]
then
    byte_order=BIG_ENDIAN
else
    byte_order=LITTLE_ENDIAN
fi
echo
echo "byte_order is $byte_order"
echo

rm -f endiantest.c endiantest


#-------------------------------------------------------------------------------
#     Preprocess any Fortran *.F files into corresponding *.f files.

BNFS=""

for i in `ls *.F.orig`
do
  bn=`basename $i .F.orig`
  bnf=${bn}.f
  BNFS="$BNFS $bnf"
  cpp $CPPFLAGS -D$byte_order $i $bnf
done

#-------------------------------------------------------------------------------
#     Generate a list of object files that correspond to the
#     list of Fortran ( *.f ) files in the current directory.

OBJS=""

for i in `ls *.f`
do
  obj=`basename $i .f`
  OBJS="$OBJS ${obj}.o"
done

#-------------------------------------------------------------------------------
#     Generate a list of object files that corresponds to the
#     list of C ( .c ) files in the current directory.

for i in `ls *.c`
do
  obj=`basename $i .c`
  OBJS="$OBJS ${obj}.o"
done

#-------------------------------------------------------------------------------
#     Remove make file, if it exists.  May need a new make file
#     with an updated object file list.

if [ -f make.libbufr ]
then
  rm -f make.libbufr
fi

#-------------------------------------------------------------------------------
#     Generate a new make file ( make.libbufr), with the updated object list,
#     from this HERE file.

cat > make.libbufr << EOF
SHELL=/bin/sh

\$(LIB):	\$(LIB)( ${OBJS} )

.f.a:
	\$(FC) -c \$(FFLAGS) \$<
	ar -ruv \$(AFLAGS) \$@ \$*.o
	rm -f \$*.o

.c.a:
	\$(CC) -c \$(CFLAGS) \$<
	ar -ruv \$(AFLAGS) \$@ \$*.o
	rm -f \$*.o
EOF

#-------------------------------------------------------------------------------
#     Generate the bufrlib.prm header file.

cpp $CPPFLAGS -DBUILD=NORMAL bufrlib.PRM.orig bufrlib.prm

export LIB="libbufr.a"
export FFLAGS=" -O2 -fPIC"
export CFLAGS=" -O2 -fPIC -DUNDERSCORE"
export AFLAGS=" "
make -f make.libbufr
err_make=$?
[ $err_make -ne 0 ]  && exit 99
