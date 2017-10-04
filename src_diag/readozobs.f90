subroutine get_num_ozobs(obsfile,num_obs_tot,endian)
    character (len=500), intent(in) :: obsfile
    integer, intent(out) :: num_obs_tot
    character(len=6), optional, intent(in) :: endian

    integer :: nlevs  ! number of levels (layer amounts + total column) per obs   
    character(20) :: isis     ! sensor/instrument/satellite id
    character(10) :: obstype  !  type of ozone obs
    character(10) :: dplat    ! sat sensor
    real, allocatable, dimension(:) :: err,grs,pob
    real,allocatable,dimension(:,:)::diagbuf
    real,allocatable,dimension(:,:,:)::rdiagbuf
    integer,allocatable,dimension(:,:)::idiagbuf
    integer :: iunit,jiter,ii,ireal,irdim1,ioff0,iint,idate,ios
    integer, allocatable, dimension(:) :: iouse
    character(len=6) :: convert_endian

    if (.not. present(endian)) then
      convert_endian = 'native'
    else
      convert_endian = endian
    endif

    iunit = 7
    num_obs_tot = 0

    if (trim(convert_endian) == 'big') then
       open(iunit,form="unformatted",file=trim(obsfile),iostat=ios,convert='big_endian')
    else if (trim(convert_endian) == 'little') then
       open(iunit,form="unformatted",file=trim(obsfile),iostat=ios,convert='little_endian')
    else if (trim(convert_endian) == 'native') then
       open(iunit,form="unformatted",file=trim(obsfile),iostat=ios)
    endif

    read(iunit,err=20,end=30) isis,dplat,obstype,jiter,nlevs,idate,iint,ireal,irdim1,ioff0
    allocate(pob(nlevs),grs(nlevs),err(nlevs),iouse(nlevs))
    read(iunit,err=20,end=30) pob,grs,err,iouse

10  continue
    read(iunit,err=20,end=30) ii
    allocate(idiagbuf(iint,ii))
    allocate(diagbuf(ireal,ii))
    allocate(rdiagbuf(irdim1,nlevs,ii))
    read(iunit,err=20,end=30) idiagbuf,diagbuf,rdiagbuf
    num_obs_tot = num_obs_tot + nlevs * ii
    deallocate(idiagbuf,diagbuf,rdiagbuf)
    go to 10
20  continue
    print *,'error reading diag_sbuv file'
30  continue
    close(iunit)
    print *,num_obs_tot,' ozone obs'
    if(allocated(pob))deallocate(pob,grs,err,iouse)
end subroutine get_num_ozobs

subroutine get_ozobs_data(obsfile, nobs_max, h_x, x_obs, x_sprd, x_err, &
           x_lon, x_lat, x_press, x_time, x_errorig, endian)

  character*500, intent(in) :: obsfile
  character(len=6), optional, intent(in) :: endian

  double precision, dimension(nobs_max), intent(out) :: h_x,x_obs,x_sprd,x_err,x_lon,&
                               x_lat,x_press,x_time,x_errorig

  character(len=6) :: convert_endian

  integer :: nlevs  ! number of levels (layer amounts + total column) per obs   
  character(20) :: isis        ! sensor/instrument/satellite id
  character(10) :: obstype  !  type of ozone obs
  character(10) :: dplat      ! sat sensor
  integer nob, n, ios, k
  integer iunit,jiter,ii,ireal,iint,irdim1,idate,ioff0

  real,allocatable,dimension(:,:)::diagbuf
  real,allocatable,dimension(:,:,:)::rdiagbuf
  integer,allocatable,dimension(:,:)::idiagbuf
  real, allocatable, dimension(:) :: err,grs,pob
  integer, allocatable, dimension(:) :: iouse
 
! make consistent with screenobs
  if (.not. present(endian)) then
     convert_endian = 'native'
  else
     convert_endian = endian
  endif

  iunit = 7
  nob = 0

  x_sprd = 1.e10
  !print *,obsfile
  if (trim(convert_endian) == 'big') then
     open(iunit,form="unformatted",file=trim(obsfile),iostat=ios,convert='big_endian')
  else if (trim(convert_endian) == 'little') then
     open(iunit,form="unformatted",file=trim(obsfile),iostat=ios,convert='little_endian')
  else if (trim(convert_endian) == 'native') then
     open(iunit,form="unformatted",file=trim(obsfile),iostat=ios)
  endif

  read(iunit,err=20,end=30) isis,dplat,obstype,jiter,nlevs,idate,iint,ireal,irdim1,ioff0
  allocate(pob(nlevs),grs(nlevs),err(nlevs),iouse(nlevs))
  read(iunit,err=20,end=30) pob,grs,err,iouse

10  continue
  read(iunit,err=20,end=30) ii
  allocate(idiagbuf(iint,ii))
  allocate(diagbuf(ireal,ii))
  allocate(rdiagbuf(irdim1,nlevs,ii))
  read(iunit,err=20,end=30) idiagbuf,diagbuf,rdiagbuf
  do k=1,nlevs
     do n=1,ii
        nob = nob + 1
        x_lat(nob) = diagbuf(1,n)
        x_lon(nob) = diagbuf(2,n)
        x_press(nob) = pob(k)
        x_time(nob) = diagbuf(3,n)
        x_err(nob) = (1./rdiagbuf(3,k,n))**2
        x_errorig(nob) = x_err(nob)
        x_obs(nob) = rdiagbuf(1,k,n)
        h_x(nob) = rdiagbuf(1,k,n)-rdiagbuf(2,k,n)
        if (irdim1 > 6) x_sprd(nob) = rdiagbuf(7,k,n)
     end do ! nn
  end do ! k
  deallocate(idiagbuf,diagbuf,rdiagbuf)
  go to 10
20  continue
  print *,'error reading diag_sbuv file'
30  continue
  close(iunit)

  if(allocated(pob))deallocate(pob,grs,err,iouse)

 end subroutine get_ozobs_data

