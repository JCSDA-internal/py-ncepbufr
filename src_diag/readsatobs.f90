subroutine get_num_satobs(obsfile,npred,num_obs_tot,endian)
    use read_diag, only: diag_data_fix_list,diag_header_fix_list,diag_header_chan_list, &
    diag_data_chan_list,diag_data_extra_list,read_radiag_data,read_radiag_header, &
    diag_data_name_list
    implicit none
    character (len=500), intent(in) :: obsfile
    integer, intent(out) :: num_obs_tot, npred
    integer iunit, iflag, ios, n
    logical fexist,lretrieval,lverbose
    real(8) :: errorlimit,errorlimit2
    character(len=6), optional, intent(in) :: endian

    type(diag_header_fix_list )         :: header_fix0
    type(diag_header_chan_list),allocatable :: header_chan0(:)
    type(diag_data_fix_list   )         :: data_fix0
    type(diag_data_chan_list  ),allocatable :: data_chan0(:)
    type(diag_data_extra_list) ,allocatable :: data_extra0(:,:)
    type(diag_data_name_list)           :: data_name0

    character(len=6) :: convert_endian

    if (.not. present(endian)) then
      convert_endian = 'native'
    else
      convert_endian = endian
    endif

    errorlimit=1./sqrt(1.e9)
    errorlimit2=1./sqrt(1.e-6)
    iunit = 7
    lretrieval=.false.
    lverbose=.false.

    num_obs_tot = 0

    inquire(file=obsfile,exist=fexist)
    if (.not.fexist) goto 900

    if (trim(convert_endian) == 'big') then
       open(iunit,form="unformatted",file=trim(obsfile),iostat=ios,convert='big_endian')
    else if (trim(convert_endian) == 'little') then
       open(iunit,form="unformatted",file=trim(obsfile),iostat=ios,convert='little_endian')
    else if (trim(convert_endian) == 'native') then
       open(iunit,form="unformatted",file=trim(obsfile),iostat=ios)
    endif
    rewind(iunit)
    call read_radiag_header(iunit,lretrieval,header_fix0,header_chan0,data_name0,iflag,lverbose)
    npred = header_fix0%npred

    do
       call read_radiag_data(iunit,header_fix0,lretrieval,data_fix0,data_chan0,data_extra0,iflag )
       if( iflag /= 0 )exit
       chan: do n=1,header_fix0%nchan
         num_obs_tot = num_obs_tot + 1
       end do chan
    enddo
900 continue
    close(iunit)

end subroutine get_num_satobs

subroutine get_satobs_data(obsfile, nobs_max, npred, h_x, h_xnobc, x_obs, x_err, &
           x_lon, x_lat, x_time, x_channum, x_errorig, x_biaspred, x_use, x_qcmark,endian)
  use read_diag, only: diag_data_fix_list,diag_header_fix_list,diag_header_chan_list, &
  diag_data_chan_list,diag_data_extra_list,read_radiag_data,read_radiag_header, &
  diag_data_name_list
  implicit none
  character(len=6), optional, intent(in) :: endian
  character*500, intent(in) :: obsfile
  integer, intent(in) :: nobs_max, npred
  real, dimension(nobs_max) :: h_x,h_xnobc,x_obs,x_err,x_lon,&
                               x_lat,x_time,x_errorig
  integer, dimension(nobs_max) :: x_use, x_qcmark
  real, dimension(npred+1,nobs_max) :: x_biaspred
  integer, dimension(nobs_max) ::  x_channum

  integer iunit, iflag, nobs, n, ios
  logical fexist,lretrieval,lverbose,adp_anglebc,emiss_bc
  real(8) :: errorlimit, errorlimit2

  type(diag_header_fix_list )         :: header_fix
  type(diag_header_chan_list),allocatable :: header_chan(:)
  type(diag_data_fix_list   )         :: data_fix
  type(diag_data_chan_list  ),allocatable :: data_chan(:)
  type(diag_data_extra_list) ,allocatable :: data_extra(:,:)
  type(diag_data_name_list)           :: data_name

  character(len=6) :: convert_endian

  if (.not. present(endian)) then
    convert_endian = 'native'
  else
    convert_endian = endian
  endif

  errorlimit=1./sqrt(1.e9)
  errorlimit2=1./sqrt(1.e-6)

  iunit = 7
  lretrieval=.false.
  lverbose=.false.
  emiss_bc = .true.
  adp_anglebc = .true.
  x_biaspred = 0

  nobs = 0

  inquire(file=obsfile,exist=fexist)
  if(.not.fexist) go to 900

  if (trim(convert_endian) == 'big') then
     open(iunit,form="unformatted",file=trim(obsfile),iostat=ios,convert='big_endian')
  else if (trim(convert_endian) == 'little') then
     open(iunit,form="unformatted",file=trim(obsfile),iostat=ios,convert='little_endian')
  else if (trim(convert_endian) == 'native') then
     open(iunit,form="unformatted",file=trim(obsfile),iostat=ios)
  endif
  rewind(iunit)
  call read_radiag_header(iunit,lretrieval,header_fix,header_chan,data_name,iflag,lverbose)

  do
   call read_radiag_data(iunit,header_fix,lretrieval,data_fix,data_chan,data_extra,iflag )
   if( iflag /= 0 ) exit
   chan:do n=1,header_fix%nchan
      nobs = nobs + 1 
      if (nobs > nobs_max) then
          print *,'warning:  exceeding array bounds in get_satobs_data',&
          nobs,nobs_max
      end if
      x_channum(nobs) = n
      x_lon(nobs) = data_fix%lon
      x_lat(nobs) = data_fix%lat
      x_time(nobs) = data_fix%obstime
      x_obs(nobs) = data_chan(n)%tbobs 
      x_use(nobs) = header_chan(n)%iuse
      x_qcmark(nobs) = data_chan(n)%qcmark
      ! bias corrected Hx
      h_x(nobs) = x_obs(nobs) - data_chan(n)%omgbc 
      ! un-bias corrected Hx
      h_xnobc(nobs) = x_obs(nobs) - data_chan(n)%omgnbc
      ! data_chan%errinv is inverse error variance.
      x_errorig(nobs) = header_chan(n)%varch**2
      x_err(nobs) = (1./data_chan(n)%errinv)**2

      x_biaspred(1,nobs) = data_chan(n)%bifix(1) ! fixed angle dependent bias
      x_biaspred(2,nobs) = data_chan(n)%bicons ! constant bias correction
      x_biaspred(3,nobs) = data_chan(n)%biang ! scan angle bias correction
      x_biaspred(4,nobs) = data_chan(n)%biclw ! CLW bias correction
      x_biaspred(5,nobs) = data_chan(n)%bilap2 ! square lapse rate bias corr
      x_biaspred(6,nobs) = data_chan(n)%bilap ! lapse rate bias correction
      if (npred == 7) then
        x_biaspred(7,nobs) = data_chan(n)%bicos ! node*cos(lat) bias correction for SSMIS
        x_biaspred(8,nobs) = data_chan(n)%bisin ! sin(lat) bias correction for SSMIS                    
      endif
      if (emiss_bc) x_biaspred(9,nobs) = data_chan(n)%biemis

      if (adp_anglebc) then
         x_biaspred( 1,nobs)  = data_chan(n)%bifix(5) ! fixed angle dependent bias correction
         x_biaspred(npred-2,nobs)  = data_chan(n)%bifix(1) ! 4th order scan angle (predictor)
         x_biaspred(npred-1,nobs)  = data_chan(n)%bifix(2) ! 3rd order scan angle (predictor)
         x_biaspred(npred,nobs)  = data_chan(n)%bifix(3) ! 2nd order scan angle (predictor)
         x_biaspred(npred+1,nobs)    = data_chan(n)%bifix(4) ! 1st order scan angle (predictor)
      endif

  enddo chan
 enddo

900  continue
 close(iunit)

end subroutine get_satobs_data
