      subroutine fortran_close(lunit,iret)
      integer,intent(in) :: lunit
      integer,intent(out) :: iret
      close(lunit, iostat=iret)
      return
      end
