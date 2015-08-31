import _bufrlib
import random
import bisect
import numpy as np

# create list of allowed fortran unit numbers
_funits = list(range(1,100))
# remove unit numbers used for stdin and stdout
_funits.remove(5)
_funits.remove(6)
# missing value in decoded data.
# (if equal to _missing_value, data is masked)
_missing_value = _bufrlib.getbmiss()
_maxdim = 5000 # max number of data levels in message
_maxevents = 255 # max number of prepbufr events in message
_nmaxseq = _maxevents # max size of sequence in message

class open(object):
    """
    open bufr file.

    'advance' method can be used step through bufr messages.
    """
    def __init__(self,filename,mode='r',table=None,datelen=10):
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
            self.mode = 'r'
        elif mode == 'w':
            if table is None:
                msg="must specify file containing bufr table when mode='w'"
                raise ValueError(msg)
            ioflag = 'OUT'
            self.mode = 'w'
        elif mode == 'a':
            ioflag = 'APN'
            self.mode = 'a'
        else:
            raise ValueError("mode must be 'r', 'w' or 'a'")
        if mode == 'r' or mode == 'a':
            # table embedded in bufr file
            iret = _bufrlib.fortran_open(filename,self.lunit,"unformatted")
            if iret != 0:
                msg='error opening %s' % filename
                raise IOError(msg)
            _bufrlib.openbf(self.lunit,ioflag,self.lunit)
            self.lundx = None
            self.table = None
        elif mode == 'w':
            self.lundx = random.choice(_funits)
            self.table = table
            iret = _bufrlib.fortran_open(table,self.lundx,"formatted")
            if iret != 0:
                msg='error opening %s' % table
            iret = _bufrlib.fortran_open(filename,self.lunit,"unformatted")
            if iret != 0:
                msg='error opening %s' % filename
            _bufrlib.openbf(self.lunit,ioflag,self.lundx)
        # set date length (default 10 means YYYYMMDDHH)
        self.set_datelength()
        # initialized message number counter
        self.msg_counter = 0
        self.msg_type = None
        self.msg_date = None
    def set_datelength(self,charlen=10):
        """
        reset number of digits for date specification (10 gives YYYYMMDDHH)
        """
        _bufrlib.datelen(charlen)
    def dump_table(self,filename):
        """
        dump embedded bufr table to a file
        """
        lundx = random.choice(_funits)
        iret = _bufrlib.fortran_open(filename,lundx,'formatted')
        if iret != 0:
            msg='error opening %s' % filename
        _bufrlib.dxdump(self.lunit,lundx)
        iret = _bufrlib.fortran_close(lundx)
        if iret == 0:
            bisect.insort_left(_funits,self.lundx)
        else:
            raise IOError('error closing %s' % filename)
    def print_table(self):
        """
        print embedded bufr table to stdout
        """
        _bufrlib.dxdump(self.lunit,6)
    def close(self):
        """
        close the bufr file
        """
        _bufrlib.closbf(self.lunit)
        # add fortran unit number back to pool
        bisect.insort_left(_funits,self.lunit)
        if self.lundx is not None:
            iret = _bufrlib.fortran_close(self.lundx)
            if iret == 0:
                bisect.insort_left(_funits,self.lundx)
            else:
                raise IOError('error closing %s' % self.table)
    def advance(self):
        """
        advance to the next msg in the bufr file
        returns 0 if advance was sucessful,
        1 if not (presumably because the end
        of the file was reached).

        The following attributes are set each time
        file is advanced to the next message:

        msg_type - string describing type of message.
        msg_date - reference date (YYYYMMDDHH) for message.
        msg_counter - message number.

        To loop through all the bufr messages in a file:

        bufr = ncepbufr.open(filename)
        while bufr.advance() == 0:
            <processing code for each message here>

        """
        subset, idate, iret = _bufrlib.readmg(self.lunit)
        if iret:
            return iret
        else:
            self.msg_type = subset
            self.msg_date = idate
            self.msg_counter += 1
            self.subset_loaded = False
            return 0
    def get_program_code(self):
        """
        return prepbufr event program code
        associated with specified mnemonic
        (see ufbqcd.f for more details)
        """
        return _bufrlib.ufbqcd(self.lunit, mnemonic)
    def checkpoint(self):
        """
        mark where we are in the bufr file,
        and rewind the file.
        The 'restore' method can then be
        used to go back to this state.
        """
        _bufrlib.rewnbf(self.lunit,0)
    def restore(self):
        """
        restore the state of the bufr
        file that recorded by a previous call
        to 'checkpoint'.
        """
        _bufrlib.rewnbf(self.lunit,1)
    def open_message(self,msg_type,msg_date):
        """
        open new bufr message
        """
        _bufrlib.openmb(self.lunit,msg_type,int(msg_date))
    def close_message(self):
        """
        close bufr message
        """
        _bufrlib.closmg(self.lunit)
    def load_subset(self):
        """
        load subset data from the current message
        (must be called before read_subset).
        To loop through all messages in a file, and
        all subsets in each message:

        bufr = ncepbufr.open(filename)
        while bufr.advance() == 0:
            while bufr.load_subset() == 0:
                <processing code for each subset here>

        """
        iret = _bufrlib.ireadsb(self.lunit)
        if iret == 0: self.subset_loaded = True
        return iret
    def read_subset(self,mnemonic,pivot=False,seq=False,events=False):
        """
        decode the data from the currently loaded message subset
        using the specified mnemonic
        (load_subset must be called first)

        if pivot = True, the first mnemonic in the string
        is intrepreted as a "pivot".  Effectively, this
        means _bufrlib.ufbrep instead of _bufrlib.ufbint is used to decode
        the message subset.  See the comments in _bufrlib.ufbrep.f for
        more details. Used for radiance data.

        if seq=True, _bufrlib.ufbseq is used to read a sequence
        of mnemonics. Used for gps data.

        if events=True, _bufrlib.ufbevn is used to read prepbufr
        'events', and a 3-d array is returned.

        Only one of seq, pivot and events can be True.

        returns a numpy masked array with decoded values
        (missing values are masked).
        The shape of the array is (nm,nlevs), where
        where nm is the number of elements in the specified
        mnemonic, and nlevs is the number of levels in the report.
        If events=True, a 3rd dimension representing the prepbufr
        event codes is added.
        """
        if not self.subset_loaded:
            raise IOError('subset not loaded, call load_subset first')
        ndim = len(mnemonic.split())
        if np.array([pivot,seq,events]).sum() > 1:
            raise ValueError('only one of pivot, seq and events cannot be True')
        if seq:
            data = np.empty((_nmaxseq,_maxdim),np.float,order='F')
            levs = _bufrlib.ufbseq(self.lunit,data,mnemonic,_nmaxseq,_maxdim)
        elif pivot:
            data = np.empty((ndim,_maxdim),np.float,order='F')
            levs = _bufrlib.ufbrep(self.lunit,data,mnemonic,ndim,_maxdim)
        elif events:
            data = np.empty((ndim,_maxdim,maxevent),np.float,order='F')
            levs = _bufrlib.ufbevn(self.lunit,data,mnemonic,ndim,_maxdim,_maxevents)
        else:
            data = np.empty((ndim,_maxdim),np.float,order='F')
            levs = _bufrlib.ufbint(self.lunit,data,mnemonic,ndim,_maxdim)
        if events:
            return np.ma.masked_values(data[:,:levs,:],_missing_value)
        else:
            return np.ma.masked_values(data[:,:levs],_missing_value)
    def write_subset(self,data,mnemonic,pivot=False,seq=False,events=False,end=False):
        """
        write data to message subset using the specified mnemonic

        if pivot = True, the first mnemonic in the string
        is intrepreted as a "pivot".  Effectively, this
        means _bufrlib.ufbrep instead of _bufrlib.ufbint is used to write
        the subset.  See the comments in _bufrlib.ufbrep.f for
        more details. Used for radiance data.

        if seq=True, _bufrlib.ufbseq is used to write a sequence
        of mnemonics. Used for gps data.

        if events=True, _bufrlib.ufbevn is used to write prepbufr
        'events' (a 3-d data array is required)

        Only one of seq, pivot and events can be True.

        If end=True, the message subset is closed and written
        to the bufr file (default False).
        """
        # make a fortran contiguous copy of input data.
        if len(data.shape) in [2,3]:
            dataf = np.empty(data.shape, np.float, order='F')
            dataf[:] = data[:]
        elif len(data.shape) == 1:
            # make 1d array into 2d array with 1 level
            dataf = np.empty((data.shape[0],1), np.float, order='F')
            dataf[:,0] = data[:]
        else:
            msg = 'data in write_subset must be 1,2 or 3d'
            raise ValueError(msg)
        if np.array([pivot,seq,events]).sum() > 1:
            raise ValueError('only one of pivot, seq and events cannot be True')
        if seq:
            levs = _bufrlib.ufbseq(self.lunit,dataf,mnemonic,dataf.shape[0],\
                    dataf.shape[1])
        elif pivot:
            levs = _bufrlib.ufbrep(self.lunit,dataf,mnemonic,dataf.shape[0],\
                    dataf.shape[1])
        elif events:
            levs = _bufrlib.ufbevn(self.lunit,dataf,mnemonic,dataf.shape[0],\
                    dataf.shape[1],dataf.shape[2])
        else:
            levs = _bufrlib.ufbint(self.lunit,dataf,mnemonic,dataf.shape[0],\
                    dataf.shape[1])
        # end subset if desired.
        if end:
            _bufrlib.writsb(self.lunit)
