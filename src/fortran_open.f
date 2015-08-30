      subroutine fortran_open(filename, lunit, format, iret)
      character*(*), intent(in) :: filename, format
      integer,intent(in) :: lunit
      integer,intent(out) :: iret
      open(lunit,file=trim(filename),form=trim(format),iostat=iret)
      return
      end
