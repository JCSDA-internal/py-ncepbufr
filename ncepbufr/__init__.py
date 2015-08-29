from _bufrlib import *
import random
import bisect
import numpy as np

# create list of allowed fortran unit numbers
_funits = list(xrange(1,100))
# remove unit numbers used for stdin and stdout
_funits.remove(5)
_funits.remove(6)
# missing value in decoded data.
# (if equal to missing_value, data is masked)
missing_value = 1.e11
# max size of decoded data array.
maxdim = 5000
maxevents = 255

class open(object):
    """
    open bufr file.

    resulting object can iterated to retrieve subsets.
    """
    def __init__(self,filename,mode='r',datelen=10):
        """
        filename: bufr file name
        mode: 'r' for read, 'w' for write (default 'r')
        datelen:  number of digits for date specification
                  (default 10, gives YYYYMMDDHH)
        """
        # randomly choose available fortran unit number
        self.lunit = random.choice(_funits)
        _funits.remove(self.lunit)
        if not _funits:
            raise IOError("too many files open")
        if mode == 'r':
            ioflag = 'IN'
        elif mode == 'w':
            ioflag = 'OUT'
        else:
            raise ValueError("mode must be 'r' or 'w'")
        # table embedded in bufr file
        openbf(filename,self.lunit,ioflag,self.lunit)
        # set date length (default 10 means YYYYMMDDHH)
        self.set_datelength()
        # initialized message number counter
        self.subset_counter = 0
        self.subset_type = None
        self.subset_date = None
    def set_datelength(self,charlen=10):
        """
        reset number of digits for date specification (10 gives YYYYMMDDHH)
        """
        datelen(charlen)
    def dump_table(self,filename):
        """
        dump embedded bufr table to a file
        """
        dxdump(filename,self.lunit,random.choice(_funits))
    def print_table(self):
        """
        print embedded bufr table to stdout
        """
        dxdump('stdout',self.lunit,6)
    def close(self):
        """
        close the bufr file
        """
        closbf(self.lunit)
        # add fortran unit number back to pool
        bisect.insort_left(_funits,self.lunit)
    def __iter__(self):
        return self
    def next(self):
        """
        get the next subset in the bufr file
        """
        subset, idate, iret = readmg(self.lunit)
        if iret:
            raise StopIteration
        else:
            self.subset_type = subset
            self.subset_date = idate
            self.subset_counter += 1
            self.subset_loaded = False
    def get_program_code(self, mnemonic):
        """
        return prepbufr event program code
        associated with specified mnemonic
        (see ufbqcd.f for more details)
        """
        return ncepbufr.ufbqcd(self.lunit, mnemonic)
    def load_subset(self):
        """
        load data from the current subset
        (must be called before read_subset)
        """
        iret = ireadsb(self.lunit)
        if iret == 0: self.subset_loaded = True
        return iret
    def read_subset(self,mnemonic,pivot=False,seq=False,events=False):
        """
        decode the data from the current subset
        using the specified mnemonic
        (load_subset must be called first)

        if pivot = True, the first mnemonic in the string
        is intrepreted as a "pivot".  Effectively, this
        means ufbrep instead of ufbint is used to decode
        the message.  See the comments in ufbrep.f for
        more details. Used for radiance data.

        if seq=True, ufbseq is used to read a sequence
        of mnemonics. Used for gps data.

        if events=True, ufbevn is used to read prepbufr
        'events', and a 3-d array is returned.

        Only one of seq, pivot and events cannot be True.

        returns a numpy masked array with decoded values
        (missing values are masked)
        The shape of the array is (nm,nlevs), where
        where nm is the number of elements in the specified
        mnemonic, and nlevs is the number of levels in the report.
        """
        if not self.subset_loaded:
            raise IOError('subset not loaded, call load_subset first')
        ndim = len(mnemonic.split())
        if np.array([pivot,seq,events]).sum() > 1:
            raise ValueError('only one of pivot, seq and events cannot be True')
        if seq:
            data,levs = ufbseq(self.lunit,50,maxdim,mnemonic)
        elif pivot:
            data,levs = ufbrep(self.lunit,ndim,maxdim,mnemonic)
        elif events:
            data,levs = ufbevn(self.lunit,ndim,maxdim,maxevents,mnemonic)
        else:
            data,levs = ufbint(self.lunit,ndim,maxdim,mnemonic)
        if events:
            return np.ma.masked_values(data[:,:levs,:],missing_value)
        else:
            return np.ma.masked_values(data[:,:levs],missing_value)
