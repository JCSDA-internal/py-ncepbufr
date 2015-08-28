from _bufrlib import *
import random
import bisect

# create list of allowed fortran units numbers
_funits = list(xrange(1,100))
# remove unit numbers used for stdin and stdout
_funits.remove(5)
_funits.remove(6)

class table(object):
    def __init__(filename):
        pass

class open(object):
    def __init__(self,filename,mode='r',table=None,datelen=10):
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
        if table is not None:
            # use existing table instance
            openbf(filename,self.lunit,ioflag,table.lunit)
        else:
            # table embedded in bufr file
            openbf(filename,self.lunit,ioflag,self.lunit)
        # set date length (default 10 means YYYYMMDDHH)
        self.set_datelength()
    def set_datelength(self,charlen=10):
        datelen(charlen)
    def dump_table(self,filename):
        dxdump(filename,self.lunit,random.choice(_funits))
    def close(self):
        closbf(self.lunit)
        # add fortran unit number back to pool
        bisect.insort_left(_funits,self.lunit)

if __name__ == "__main__":
    bufr = open('../test/prepbufr')
    print bufr.lunit
    print _funits
    bufr.dump_table('prepbufr.table')
    subset, idate, iret = readmg(bufr.lunit)
    print 'subset, date, iret =',subset, idate, iret
    bufr.close()
    print _funits
