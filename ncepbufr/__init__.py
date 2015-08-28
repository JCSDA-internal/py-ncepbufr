from _bufrlib import *
import random
import bisect
import numpy as np

# create list of allowed fortran unit numbers
_funits = list(xrange(1,100))
# remove unit numbers used for stdin and stdout
_funits.remove(5)
_funits.remove(6)
missing_value = 1.e11
_mxlvs = 255

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
    def load_subset(self):
        """
        load data from the current subset
        (must be called before read_subset)
        """
        iret = ireadsb(self.lunit)
        if iret == 0: self.subset_loaded = True
        return iret
    def read_subset(self,mnemonic,pivot=False):
        """
        decode the data from the current subset
        using the specified mnemonic
        (load_subset must be called first)

        if pivot = True, the first mnemonic in the string
        is intrepreted as a "pivot".  Effectively, this
        means ufbrep instead of ufbint is used to decode
        the message.  See the comments in ufbrep.f for
        more details.

        returns a numpy masked array with decoded values
        (missing values are masked)
        The shape of the array is (nm,nlevs), where
        where nm is the number of elements in the specified
        mnemonic, and nlevs is the number of levels in the report.
        """
        if not self.subset_loaded:
            raise IOError('subset not loaded, call load_subset first')
        ndim = len(mnemonic.split())
        if not pivot:
            data,levs = ufbint(self.lunit,ndim,_mxlvs,mnemonic)
        else:
            data,levs = ufbrep(self.lunit,ndim,_mxlvs,mnemonic)
        return np.ma.masked_values(data[:,:levs],missing_value)

if __name__ == "__main__":
    # read prepbufr file
    hdstr='SID XOB YOB DHR TYP ELV SAID T29'
    obstr='POB QOB TOB ZOB UOB VOB PWO MXGS HOVI CAT PRSS TDO PMO'
    qcstr='PQM QQM TQM ZQM WQM NUL PWQ PMQ'
    oestr='POE QOE TOE NUL WOE NUL PWE     '
    bufr = open('../test/prepbufr')
    print _funits
    bufr.print_table()
    for subset in bufr:
        print bufr.subset_counter, bufr.subset_type, bufr.subset_date
        #bufr.read_subset(obstr) # should raise subset not loaded error
        while (bufr.load_subset() == 0):
            hdr = bufr.read_subset(hdstr)
            station_id = hdr[0].tostring()
            obs = bufr.read_subset(obstr)
            nlevs = obs.shape[-1]
            oer = bufr.read_subset(oestr)
            qcf = bufr.read_subset(qcstr)
            print 'station_id, lon, lat, time, station_type, levels =',\
            station_id,hdr[1].item(),hdr[2].item(),hdr[3].item(),int(hdr[4].item()),nlevs
            if bufr.subset_counter == 1: # print data from first subset
                for k in xrange(nlevs):
                    print 'level',k+1
                    print 'obs',obs[:,k]
                    print 'oer',oer[:,k]
                    print 'qcf',qcf[:,k]
    bufr.close()
    print _funits

    # read radiance file.
    hdstr1 ='SAID SIID FOVN YEAR MNTH DAYS HOUR MINU SECO CLAT CLON CLATH CLONH HOLS'
    hdstr2 ='SAZA SOZA BEARAZ SOLAZI'
    bufr = open('../test/1bamua')
    bufr.print_table()
    print_data = True
    for subset in bufr:
        print bufr.subset_counter, bufr.subset_type, bufr.subset_date
        while (bufr.load_subset() == 0):
            hdr1 = bufr.read_subset(hdstr1)
            hdr2 = bufr.read_subset(hdstr2)
            yyyymmddhhss ='%04i%02i%02i%02i%02i%02i' % tuple(hdr1[3:9])
            # for satellite id, see common code table c-5
            # (http://www.emc.ncep.noaa.gov/mmb/data_processing/common_tbl_c1-c5.htm#c-5)
            # for sensor id, see common code table c-8
            # (http://www.emc.ncep.noaa.gov/mmb/data_processing/common_tbl_c8-c14.htm#c-8)
            print 'sat id, sensor id, lat, lon, yyyymmddhhmmss =',int(hdr1[0].item()),\
            int(hdr1[1].item()),hdr1[9].item(),hdr1[10].item(),yyyymmddhhss
            if print_data: # print data from first subset with data
                obs = bufr.read_subset('TMBR',pivot=True)
                nchanl = obs.shape[-1]
                for k in xrange(nchanl):
                    print 'channel, tb =',k+1,obs[0,k]
                print_data = False
    bufr.close()
