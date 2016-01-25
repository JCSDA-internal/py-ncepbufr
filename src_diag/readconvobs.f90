subroutine get_num_convobs(obsfile,num_obs_tot,endian)
    character(len=500), intent(in) :: obsfile
    integer, intent(out) :: num_obs_tot
    character(len=6), optional, intent(in) :: endian
    ! local vars
    character(len=3) :: obtype
    integer iunit, nchar, nreal, ii, mype,ios, idate
    integer :: nn,nobst, nobsps, nobsq, nobsuv, nobsgps, &
         nobstcp, nobssst, nobsspd, nobsdw, nobsrw, nobspw, nobssrw
    character(len=8),allocatable,dimension(:):: cdiagbuf
    character(len=6) :: convert_endian
    real,allocatable,dimension(:,:)::rdiagbuf
    if (.not. present(endian)) then
      convert_endian = 'native'
    else
      convert_endian = endian
    endif
    iunit = 7
    num_obs_tot = 0
    nobst = 0
    nobsq = 0
    nobsps = 0
    nobsuv = 0
    nobssst = 0
    nobsspd = 0
    nobsdw = 0
    nobsrw = 0 
    nobspw = 0
    nobsgps = 0
    nobssrw = 0
    nobstcp = 0
    !print *,obsfile
    if (trim(convert_endian) == 'big') then
       open(iunit,form="unformatted",file=trim(obsfile),iostat=ios,convert='big_endian')
    else if (trim(convert_endian) == 'little') then
       open(iunit,form="unformatted",file=trim(obsfile),iostat=ios,convert='little_endian')
    else if (trim(convert_endian) == 'native') then
       open(iunit,form="unformatted",file=trim(obsfile),iostat=ios)
    endif

    read(iunit) idate
    !print *,idate
10  continue
    read(iunit,err=20,end=30) obtype,nchar,nreal,ii,mype
    allocate(cdiagbuf(ii),rdiagbuf(nreal,ii))
    read(iunit) cdiagbuf(1:ii),rdiagbuf(:,1:ii)
    !print *,obtype,nchar,nreal,ii,mype
    nn=ii
    if (obtype == '  t') then
       nobst = nobst + nn
       num_obs_tot = num_obs_tot + nn
    else if (obtype == ' uv') then
       nobsuv = nobsuv + 2*nn
       num_obs_tot = num_obs_tot + 2*nn
    else if (obtype == ' ps') then
        nobsps = nobsps + nn
        num_obs_tot = num_obs_tot + nn
    else if (obtype == '  q') then
       nobsq = nobsq + nn
       num_obs_tot = num_obs_tot + nn
    else if (obtype == 'spd') then
       nobsspd = nobsspd + nn
       num_obs_tot = num_obs_tot + nn
    else if (obtype == 'sst') then ! skip sst
       nobssst = nobssst + nn
       num_obs_tot = num_obs_tot + nn
    else if (obtype == 'srw') then
       nobssrw = nobssrw + nn
       num_obs_tot = num_obs_tot + nn
    else if (obtype == ' rw') then
       nobsrw = nobsrw + nn
       num_obs_tot = num_obs_tot + nn
    else if (obtype == 'gps') then
       nobsgps = nobsgps + nn
       num_obs_tot = num_obs_tot + nn
    else if (obtype == ' dw') then
       nobsdw = nobsdw + nn
       num_obs_tot = num_obs_tot + nn
    else if (obtype == ' pw') then
       nobspw = nobspw + nn
       num_obs_tot = num_obs_tot + nn
    else if (obtype == 'tcp') then
       nobstcp = nobstcp + nn
       num_obs_tot = num_obs_tot + nn
    else
       print *,'unknown obtype ',trim(obtype)
    end if
    deallocate(cdiagbuf,rdiagbuf)
    go to 10
20  continue
    print *,'error reading diag_conv file',obtype
30  continue
    print *,num_obs_tot,' obs in diag_conv_ges file'
    write(6,100) 't',nobst
    write(6,100) 'q',nobsq
    write(6,100) 'ps',nobsps
    write(6,100) 'uv',nobsuv
    write(6,100) 'sst',nobssst
    write(6,100) 'gps',nobsgps
    write(6,100) 'pw',nobspw
    write(6,100) 'dw',nobsdw
    write(6,100) 'srw',nobsrw
    write(6,100) 'rw',nobssrw
    write(6,100) 'tcp',nobstcp
100 format(2x,a3,2x,i9,2x,i9)
    close(iunit)
end subroutine get_num_convobs

subroutine get_convobs_data(obsfile, nobs_max, h_x, x_obs, x_err, &
           x_lon, x_lat, x_press, x_time, x_code, x_errorig, x_type, &
           x_use, x_station_id, x_stnelev, endian)

  character(len=500), intent(in) :: obsfile
  character(len=6), optional, intent(in) :: endian
  double precision, dimension(nobs_max), intent(out) :: h_x,x_obs,x_err,x_lon,&
                               x_lat,x_press,x_time,x_errorig,x_stnelev
  integer, dimension(nobs_max), intent(out) :: x_code, x_use
  integer, dimension(nobs_max,4), intent(out) ::  x_type
  integer, dimension(nobs_max,9), intent(out) ::  x_station_id
  ! local vars
  character(len=6) :: convert_endian
  character(len=3) :: obtype
  integer iunit, nobs_max, nob, n, nchar, nreal, ii, mype, ios, idate
  character(len=8),allocatable,dimension(:):: cdiagbuf
  real,allocatable,dimension(:,:)::rdiagbuf

  if (.not. present(endian)) then
    convert_endian = 'native'
  else
    convert_endian = endian
  endif

  iunit = 7

  nob  = 0
  !print *,obsfile
  if (trim(convert_endian) == 'big') then
     open(iunit,form="unformatted",file=trim(obsfile),iostat=ios,convert='big_endian')
  else if (trim(convert_endian) == 'little') then
     open(iunit,form="unformatted",file=trim(obsfile),iostat=ios,convert='little_endian')
  else if (trim(convert_endian) == 'native') then
     open(iunit,form="unformatted",file=trim(obsfile),iostat=ios)
  endif
  read(iunit) idate
10 continue
  read(iunit,err=20,end=30) obtype,nchar,nreal,ii,mype
  !print *,obtype,nchar,nreal,ii,mype
    if (obtype == '  t') then
       allocate(cdiagbuf(ii),rdiagbuf(nreal,ii))
       read(iunit) cdiagbuf(1:ii),rdiagbuf(:,1:ii)
       do n=1,ii
          nob = nob + 1
          x_code(nob) = rdiagbuf(1,n)
          x_lat(nob) = rdiagbuf(3,n)
          x_lon(nob) = rdiagbuf(4,n)
          x_press(nob) = rdiagbuf(6,n)
          x_time(nob) = rdiagbuf(8,n)
          x_stnelev(nob) = rdiagbuf(5,n)
          if (rdiagbuf(14,n) > 1.e-5) then
            x_errorig(nob) = (1.0/rdiagbuf(14,n))**2
          else
            x_errorig(nob) = 1.e10
          endif
          x_err(nob) = (1.0/rdiagbuf(16,n))**2
          x_obs(nob) = rdiagbuf(17,n)
          h_x(nob) = rdiagbuf(17,n)-rdiagbuf(18,n)
          call strtoarr(obtype, x_type(nob,:), 3)
          call strtoarr(cdiagbuf(n), x_station_id(nob,:), 8)
          x_use(nob) = rdiagbuf(12,n)
       enddo
       deallocate(cdiagbuf,rdiagbuf)
!        cdiagbuf(ii)    = station_id         ! station id
!        rdiagbuf(1,ii)  = ictype(ikx)        ! observation type
!        rdiagbuf(2,ii)  = icsubtype(ikx)     ! observation subtype
!        rdiagbuf(3,ii)  = data(ilate,i)      ! observation latitude (degrees)
!        rdiagbuf(4,ii)  = data(il1.0,i)      ! observation longitude (degrees)
!        rdiagbuf(5,ii)  = data(istnelv,i)    ! station elevation (meters)
!        rdiagbuf(6,ii)  = prest              ! observation pressure (hPa)
!        rdiagbuf(7,ii)  = data(iobshgt,i)    ! observation height (meters)
!        rdiagbuf(8,ii)  = dtime              ! obs time (hours relative to analysis time)
!        rdiagbuf(9,ii)  = data(iqc,i)        ! input prepbufr qc or event mark
!        rdiagbuf(10,ii) = data(iqt,i)        ! setup qc or event mark (currently qtflg only)
!        rdiagbuf(11,ii) = data(iuse,i)       ! read_prepbufr data usage flag
!        rdiagbuf(12,ii) = 1.0             ! analysis usage flag (1=use, -1=not used)
!        rdiagbuf(13,ii) = rwgt               ! nonlinear qc relative weight
!        rdiagbuf(14,ii) = errinv_input       ! prepbufr inverse obs error (K**-1)
!        rdiagbuf(15,ii) = errinv_adjst       ! read_prepbufr inverse obs error (K**-1)
!        rdiagbuf(16,ii) = errinv_final       ! final inverse observation error (K**-1)
!        rdiagbuf(17,ii) = data(itob,i)       ! temperature observation (K)
!        rdiagbuf(18,ii) = ddiff              ! obs-ges used in analysis (K)
!        rdiagbuf(19,ii) = tob-tges           ! obs-ges w/o bias correction (K) (future slot)
    else if (obtype == ' uv') then
       allocate(cdiagbuf(ii),rdiagbuf(nreal,ii))
       read(iunit) cdiagbuf(1:ii),rdiagbuf(:,1:ii)
       do n=1,ii
          nob = nob + 1
          x_code(nob) = rdiagbuf(1,n)
          x_lat(nob) = rdiagbuf(3,n)
          x_lon(nob) = rdiagbuf(4,n)
          x_press(nob) = rdiagbuf(6,n)
          x_time(nob) = rdiagbuf(8,n)
          x_stnelev(nob) = rdiagbuf(5,n)
          if (rdiagbuf(14,n) > 1.e-5) then
            x_errorig(nob) = (1.0/rdiagbuf(14,n))**2
          else
            x_errorig(nob) = 1.e10
          endif
          x_err(nob) = (1.0/rdiagbuf(16,n))**2
          x_obs(nob) = rdiagbuf(17,n)
          h_x(nob) = rdiagbuf(17,n)-rdiagbuf(18,n)
          obtype = '  u'
          call strtoarr(obtype, x_type(nob,:), 3)
          call strtoarr(cdiagbuf(n), x_station_id(nob,:), 8)
          x_use(nob) = rdiagbuf(12,n)
          nob = nob + 1
          x_code(nob) = rdiagbuf(1,n)
          x_lat(nob) = rdiagbuf(3,n)
          x_lon(nob) = rdiagbuf(4,n)
          x_press(nob) = rdiagbuf(6,n)
          x_time(nob) = rdiagbuf(8,n)
          x_stnelev(nob) = rdiagbuf(5,n)
          if (rdiagbuf(14,n) > 1.e-5) then
            x_errorig(nob) = (1.0/rdiagbuf(14,n))**2
          else
            x_errorig(nob) = 1.e10
          endif
          x_err(nob) = (1.0/rdiagbuf(16,n))**2
          x_obs(nob) = rdiagbuf(20,n)
          h_x(nob) = rdiagbuf(20,n)-rdiagbuf(21,n)
          obtype = '  v'
          call strtoarr(obtype, x_type(nob,:), 3)
          call strtoarr(cdiagbuf(n), x_station_id(nob,:), 8)
          x_use(nob) = rdiagbuf(12,n)
       enddo
       deallocate(cdiagbuf,rdiagbuf)
!        cdiagbuf(ii)    = station_id         ! station id
!        rdiagbuf(1,ii)  = ictype(ikx)        ! observation type
!        rdiagbuf(2,ii)  = icsubtype(ikx)     ! observation subtype
!        rdiagbuf(3,ii)  = data(ilate,i)      ! observation latitude (degrees)
!        rdiagbuf(4,ii)  = data(il1.0,i)      ! observation longitude (degrees)
!        rdiagbuf(5,ii)  = data(ielev,i)      ! station elevation (meters)
!        rdiagbuf(6,ii)  = presw              ! observation pressure (hPa)
!        rdiagbuf(7,ii)  = data(ihgt,i)       ! observation height (meters)
!        rdiagbuf(8,ii)  = dtime              ! obs time (hours relative to analysis time)
!        rdiagbuf(9,ii)  = data(iqc,i)        ! input prepbufr qc or event mark
!        rdiagbuf(10,ii) = rmiss_single       ! setup qc or event mark
!        rdiagbuf(11,ii) = data(iuse,i)       ! read_prepbufr data usage flag
!        rdiagbuf(12,ii) = 1.0             ! analysis usage flag (1=use, -1=not used)
!        rdiagbuf(13,ii) = rwgt               ! nonlinear qc relative weight
!        rdiagbuf(14,ii) = errinv_input       ! prepbufr inverse obs error (m/s)**-1
!        rdiagbuf(15,ii) = errinv_adjst       ! read_prepbufr inverse obs error (m/s)**-1
!        rdiagbuf(16,ii) = errinv_final       ! final inverse observation error (m/s)**-1
!        rdiagbuf(17,ii) = data(iuob,i)       ! u wind component observation (m/s)
!        rdiagbuf(18,ii) = dudiff             ! u obs-ges used in analysis (m/s)
!        rdiagbuf(19,ii) = uob-ugesin         ! u obs-ges w/o bias correction (m/s) (future slot)
!        rdiagbuf(20,ii) = data(ivob,i)       ! v wind component observation (m/s)
!        rdiagbuf(21,ii) = dvdiff             ! v obs-ges used in analysis (m/s)
!        rdiagbuf(22,ii) = vob-vgesin         ! v obs-ges w/o bias correction (m/s) (future slot)
!        rdiagbuf(23,ii) = factw              ! 10m wind reduction factor
    else if (obtype == ' ps') then
       allocate(cdiagbuf(ii),rdiagbuf(nreal,ii))
       read(iunit) cdiagbuf(1:ii),rdiagbuf(:,1:ii)
       do n=1,ii
          nob = nob + 1
          x_code(nob) = rdiagbuf(1,n)
          x_lat(nob) = rdiagbuf(3,n)
          x_lon(nob) = rdiagbuf(4,n)
          x_press(nob) = rdiagbuf(17,n)
          x_time(nob) = rdiagbuf(8,n)
          x_stnelev(nob) = rdiagbuf(5,n)
          if (rdiagbuf(14,n) > 1.e-5) then
            x_errorig(nob) = (1.0/rdiagbuf(14,n))**2
          else
            x_errorig(nob) = 1.e10
          endif
          ! error modified by GSI.
          x_err(nob) = (1.0/rdiagbuf(16,n))**2
          ! unmodified error from read_prepbufr
          !if (rdiagbuf(15,n) > tiny(rdiagbuf(1,1))) then
          !x_err(nob) = (1.0/rdiagbuf(15,n))**2
          x_obs(nob) = rdiagbuf(17,n)
          ! background adjusted to station height
          h_x(nob) = rdiagbuf(17,n)-rdiagbuf(19,n)
          ! apply adjustment to ob instead of background
          x_obs(nob) = x_obs(nob) + rdiagbuf(18,n)-rdiagbuf(19,n)
          x_use(nob) = rdiagbuf(12,n)
          call strtoarr(obtype, x_type(nob,:), 3)
          call strtoarr(cdiagbuf(n), x_station_id(nob,:), 8)
       enddo
       deallocate(cdiagbuf,rdiagbuf)
!        cdiagbuf(ii)    = station_id         ! station id
!        rdiagbuf(1,ii)  = ictype(ikx)        ! observation type
!        rdiagbuf(2,ii)  = icsubtype(ikx)     ! observation subtype
!        rdiagbuf(3,ii)  = data(ilate,i)      ! observation latitude (degrees)
!        rdiagbuf(4,ii)  = data(il1.0,i)      ! observation longitude (degrees)
!        rdiagbuf(5,ii)  = data(istnelv,i)    ! station elevation (meters)
!        rdiagbuf(6,ii)  = data(ipres,i)*r10  ! observation pressure (hPa)
!        rdiagbuf(7,ii)  = dhgt               ! observation height (meters)
!        rdiagbuf(8,ii)  = dtime              ! obs time (hours relative to analysis time)
!        rdiagbuf(9,ii)  = data(iqc,i)        ! input prepbufr qc or event mark
!        rdiagbuf(10,ii) = rmiss_single       ! setup qc or event mark
!        rdiagbuf(11,ii) = data(iuse,i)       ! read_prepbufr data usage flag
!        rdiagbuf(12,ii) = 1.0             ! analysis usage flag (1=use, -1=not used)
!        rdiagbuf(13,ii) = rwgt               ! nonlinear qc relative weight
!        rdiagbuf(14,ii) = errinv_input       ! prepbufr inverse obs error (hPa**-1)
!        rdiagbuf(15,ii) = errinv_adjst       ! read_prepbufr inverse obs error (hPa**-1)
!        rdiagbuf(16,ii) = errinv_final       ! final inverse observation error (hPa**-1)
!        rdiagbuf(17,ii) = pob                ! surface pressure observation (hPa)
!        rdiagbuf(18,ii) = pob-pges           ! obs-ges used in analysis (coverted to hPa)
!        rdiagbuf(19,ii) = pob-pgesorig       ! obs-ges w/o adjustment to guess surface pressure (hPa)
    else if (obtype == 'tcp') then
       allocate(cdiagbuf(ii),rdiagbuf(nreal,ii))
       read(iunit) cdiagbuf(1:ii),rdiagbuf(:,1:ii)
       do n=1,ii
          nob = nob + 1
          x_code(nob) = rdiagbuf(1,n)
          x_lat(nob) = rdiagbuf(3,n)
          x_lon(nob) = rdiagbuf(4,n)
          x_press(nob) = rdiagbuf(17,n)
          x_time(nob) = rdiagbuf(8,n)
          x_stnelev(nob) = 0
          if (rdiagbuf(14,n) > 1.e-5) then
            x_errorig(nob) = (1.0/rdiagbuf(14,n))**2
          else
            x_errorig(nob) = 1.e10
          endif
          ! error modified by GSI.
          x_err(nob) = (1.0/rdiagbuf(16,n))**2
          ! unmodified error from read_prepbufr
          !if (rdiagbuf(15,n) > tiny(rdiagbuf(1,1))) then
          !x_err(nob) = (1.0/rdiagbuf(15,n))**2
          x_obs(nob) = rdiagbuf(17,n)
          ! background adjusted to station height
          h_x(nob) = rdiagbuf(17,n)-rdiagbuf(19,n)
          ! apply adjustment to ob instead of background
          x_obs(nob) = x_obs(nob) + rdiagbuf(18,n)-rdiagbuf(19,n)
          x_use(nob) = rdiagbuf(12,n)
          call strtoarr(obtype, x_type(nob,:), 3)
          call strtoarr(cdiagbuf(n), x_station_id(nob,:), 8)
       enddo
       deallocate(cdiagbuf,rdiagbuf)
    else if (obtype == '  q') then
       allocate(cdiagbuf(ii),rdiagbuf(nreal,ii))
       read(iunit) cdiagbuf(1:ii),rdiagbuf(:,1:ii)
       do n=1,ii
          nob = nob + 1
          x_code(nob) = rdiagbuf(1,n)
          x_lat(nob) = rdiagbuf(3,n)
          x_lon(nob) = rdiagbuf(4,n)
          x_press(nob) = rdiagbuf(6,n)
          x_time(nob) = rdiagbuf(8,n)
          x_stnelev(nob) = rdiagbuf(5,n)
          if (rdiagbuf(14,n)*rdiagbuf(20,n) > 1.e-5) then
! normalize by qsatges
            x_errorig(nob) = (1./(rdiagbuf(20,n)*rdiagbuf(14,n)))**2
          else
            x_errorig(nob) = 1.e10
          endif
! normalize by qsatges
          x_err(nob) = (1./(rdiagbuf(20,n)*rdiagbuf(16,n)))**2
          x_obs(nob) = rdiagbuf(17,n)/rdiagbuf(20,n)
          h_x(nob) = (rdiagbuf(17,n)-rdiagbuf(18,n))/rdiagbuf(20,n)
          call strtoarr(obtype, x_type(nob,:), 3)
          call strtoarr(cdiagbuf(n), x_station_id(nob,:), 8)
          x_use(nob) = rdiagbuf(12,n)
       enddo
       deallocate(cdiagbuf,rdiagbuf)
!        cdiagbuf(ii)    = station_id         ! station id
!        rdiagbuf(1,ii)  = ictype(ikx)        ! observation type
!        rdiagbuf(2,ii)  = icsubtype(ikx)     ! observation subtype
!        rdiagbuf(3,ii)  = data(ilate,i)      ! observation latitude (degrees)
!        rdiagbuf(4,ii)  = data(il1.0,i)      ! observation longitude (degrees)
!        rdiagbuf(5,ii)  = data(istnelv,i)    ! station elevation (meters)
!        rdiagbuf(6,ii)  = presq              ! observation pressure (hPa)
!        rdiagbuf(7,ii)  = data(iobshgt,i)    ! observation height (meters)
!        rdiagbuf(8,ii)  = dtime              ! obs time (hours relative to analysis time)
!        rdiagbuf(9,ii)  = data(iqc,i)        ! input prepbufr qc or event mark
!        rdiagbuf(10,ii) = rmiss_single       ! setup qc or event mark 
!        rdiagbuf(11,ii) = data(iuse,i)       ! read_prepbufr data usage flag
!        rdiagbuf(12,ii) = 1.0             ! analysis usage flag (1=use, -1=not used)
!        rdiagbuf(13,ii) = rwgt               ! nonlinear qc relative weight
!        rdiagbuf(14,ii) = errinv_input       ! prepbufr inverse observation error
!        rdiagbuf(15,ii) = errinv_adjst       ! read_prepbufr inverse obs error
!        rdiagbuf(16,ii) = errinv_final       ! final inverse observation error
!        rdiagbuf(17,ii) = data(iqob,i)       ! observation
!        rdiagbuf(18,ii) = ddiff              ! obs-ges used in analysis
!        rdiagbuf(19,ii) = qob-qges           ! obs-ges w/o bias correction (future slot)
!        rdiagbuf(20,ii) = qsges              ! guess saturation specific humidity
    else if (obtype == 'spd') then
       allocate(cdiagbuf(ii),rdiagbuf(nreal,ii))
       read(iunit) cdiagbuf(1:ii),rdiagbuf(:,1:ii)
       do n=1,ii
          nob = nob + 1
          x_code(nob) = rdiagbuf(1,n)
          x_lat(nob) = rdiagbuf(3,n)
          x_lon(nob) = rdiagbuf(4,n)
          x_press(nob) = rdiagbuf(6,n)
          x_time(nob) = rdiagbuf(8,n)
          !x_stnelev(nob) = rdiagbuf(5,n)
          x_stnelev(nob) = rdiagbuf(7,n) ! use ob height instead
          if (rdiagbuf(14,n) > 1.e-5) then
            x_errorig(nob) = (1.0/rdiagbuf(14,n))**2
          else
            x_errorig(nob) = 1.e10
          endif
          x_err(nob) = (1.0/rdiagbuf(16,n))**2
          x_obs(nob) = rdiagbuf(17,n)
          h_x(nob) = rdiagbuf(17,n)-rdiagbuf(18,n)
          call strtoarr(obtype, x_type(nob,:), 3)
          call strtoarr(cdiagbuf(n), x_station_id(nob,:), 8)
          x_use(nob) = rdiagbuf(12,n)
       enddo
       deallocate(cdiagbuf,rdiagbuf)
!        cdiagbuf(ii)    = station_id         ! station id
!        rdiagbuf(1,ii)  = ictype(ikx)        ! observation type
!        rdiagbuf(2,ii)  = icsubtype(ikx)     ! observation subtype
!        rdiagbuf(3,ii)  = data(ilate,i)      ! observation latitude (degrees)
!        rdiagbuf(4,ii)  = data(il1.0,i)      ! observation longitude (degrees)
!        rdiagbuf(5,ii)  = data(istnelv,i)    ! station elevation (meters)
!        rdiagbuf(6,ii)  = presw              ! observation pressure (hPa)
!        rdiagbuf(7,ii)  = data(ihgt,i)       ! observation height (meters)
!        rdiagbuf(8,ii)  = dtime              ! obs time (hours relative to analysis time)
!        rdiagbuf(9,ii)  = data(iqc,i)        ! input prepbufr qc or event mark
!        rdiagbuf(10,ii) = rmiss_single       ! setup qc or event mark
!        rdiagbuf(11,ii) = data(iuse,i)       ! read_prepbufr data usage flag
!        rdiagbuf(12,ii) = 1.0             ! analysis usage flag (1=use, -1=not used)
!        rdiagbuf(13,ii) = rwgt               ! nonlinear qc relative weight
!        rdiagbuf(14,ii) = errinv_input       ! prepbufr inverse obs error (m/s)**-1
!        rdiagbuf(15,ii) = errinv_adjst       ! read_prepbufr inverse obs error (m/s)**-1
!        rdiagbuf(16,ii) = errinv_final       ! final inverse observation error (m/s)**-1
!        rdiagbuf(17,ii) = spdob              ! wind speed observation (m/s)
!        rdiagbuf(18,ii) = ddiff              ! obs-ges used in analysis (m/s)
!        rdiagbuf(19,ii) = spdob0-spdges      ! obs-ges w/o bias correction (m/s) (future slot)
!        rdiagbuf(20,ii) = factw              ! 10m wind reduction factor
     else if (obtype == 'sst') then ! skip sst
       allocate(cdiagbuf(ii),rdiagbuf(nreal,ii))
       read(iunit) cdiagbuf(1:ii),rdiagbuf(:,1:ii)
       do n=1,ii
          nob = nob + 1
          x_code(nob) = rdiagbuf(1,n)
          x_lat(nob) = rdiagbuf(3,n)
          x_lon(nob) = rdiagbuf(4,n)
          x_press(nob) = rdiagbuf(6,n)
          x_time(nob) = rdiagbuf(8,n)
          x_stnelev(nob) = 0
          if (rdiagbuf(14,n) > 1.e-5) then
            x_errorig(nob) = (1.0/rdiagbuf(14,n))**2
          else
            x_errorig(nob) = 1.e10
          endif
          x_err(nob) = (1.0/rdiagbuf(16,n))**2
          x_obs(nob) = rdiagbuf(17,n)
          h_x(nob) = rdiagbuf(17,n)-rdiagbuf(18,n)
          call strtoarr(obtype, x_type(nob,:), 3)
          call strtoarr(cdiagbuf(n), x_station_id(nob,:), 8)
          x_use(nob) = rdiagbuf(12,n)
       enddo
       deallocate(cdiagbuf,rdiagbuf)
!        cdiagbuf(ii)    = station_id         ! station id
!        rdiagbuf(1,ii)  = ictype(ikx)        ! observation type
!        rdiagbuf(2,ii)  = icsubtype(ikx)     ! observation subtype
!        rdiagbuf(3,ii)  = data(ilate,i)      ! observation latitude (degrees)
!        rdiagbuf(4,ii)  = data(il1.0,i)      ! observation longitude (degrees)
!        rdiagbuf(5,ii)  = data(istnelv,i)    ! station elevation (meters)
!        rdiagbuf(6,ii)  = rmiss_single       ! observation pressure (hPa)
!        rdiagbuf(7,ii)  = data(idepth,i)     ! observation height (meters)
!        rdiagbuf(8,ii)  = dtime              ! obs time (hours relative to analysis time)
!        rdiagbuf(9,ii)  = data(iqc,i)        ! input prepbufr qc or event mark
!        rdiagbuf(10,ii) = rmiss_single       ! setup qc or event mark
!        rdiagbuf(11,ii) = data(iuse,i)       ! read_prepbufr data usage flag
!        rdiagbuf(12,ii) = 1.0             ! analysis usage flag (1=use, -1=not used)
!        rdiagbuf(13,ii) = rwgt               ! nonlinear qc relative weight
!        rdiagbuf(14,ii) = errinv_input       ! prepbufr inverse obs error (K**-1)
!        rdiagbuf(15,ii) = errinv_adjst       ! read_prepbufr inverse obs error (K**-1)
!        rdiagbuf(16,ii) = errinv_final       ! final inverse observation error (K**-1)
!        rdiagbuf(17,ii) = data(isst,i)       ! SST observation (K)
!        rdiagbuf(18,ii) = ddiff              ! obs-ges used in analysis (K)
!        rdiagbuf(19,ii) = data(isst,i)-sstges! obs-ges w/o bias correction (K) (future slot)
!        rdiagbuf(20,ii) = data(iotype,i)     ! type of measurement
    else if (obtype == 'srw') then
       allocate(cdiagbuf(ii),rdiagbuf(nreal,ii))
       read(iunit) cdiagbuf(1:ii),rdiagbuf(:,1:ii)
       do n=1,ii
          nob = nob + 1
          x_code(nob) = rdiagbuf(1,n)
          x_lat(nob) = rdiagbuf(3,n)
          x_lon(nob) = rdiagbuf(4,n)
          x_press(nob) = rdiagbuf(6,n)
          x_time(nob) = rdiagbuf(8,n)
          !x_stnelev(nob) = rdiagbuf(5,n)
          x_stnelev(nob) = rdiagbuf(7,n) ! use ob height instead
          if (rdiagbuf(14,n) > 1.e-5) then
            x_errorig(nob) = (1.0/rdiagbuf(14,n))**2
          else
            x_errorig(nob) = 1.e10
          endif
          x_err(nob) = (1.0/rdiagbuf(16,n))**2
          x_obs(nob) = rdiagbuf(17,n)
          h_x(nob) = rdiagbuf(17,n)-rdiagbuf(18,n)
          call strtoarr(obtype, x_type(nob,:), 3)
          call strtoarr(cdiagbuf(n), x_station_id(nob,:), 8)
          x_use(nob) = rdiagbuf(12,n)
       enddo
       deallocate(cdiagbuf,rdiagbuf)
! radar wind superobs
!        cdiagbuf(ii)    = station_id         ! station id
!        rdiagbuf(1,ii)  = ictype(ikx)        ! observation type
!        rdiagbuf(2,ii)  = icsubtype(ikx)     ! observation subtype
!        rdiagbuf(3,ii)  = data(ilate,i)      ! observation latitude (degrees)
!        rdiagbuf(4,ii)  = data(il1.0,i)      ! observation longitude (degrees)
!        rdiagbuf(5,ii)  = rmiss_single       ! station elevation (meters)
!        rdiagbuf(6,ii)  = presw              ! observation pressure (hPa)
!        rdiagbuf(7,ii)  = data(ihgt,i)       ! observation height (meters)
!        rdiagbuf(8,ii)  = dtime              ! obs time (hours relative to analysis time)
!        rdiagbuf(9,ii)  = rmiss_single       ! input prepbufr qc or event mark
!        rdiagbuf(10,ii) = rmiss_single       ! setup qc or event mark
!        rdiagbuf(11,ii) = data(iuse,i)       ! read_prepbufr data usage flag
!        rdiagbuf(12,ii) = 1.0             ! analysis usage flag (1=use, -1=not used)
!        rdiagbuf(13,ii) = rwgt               ! nonlinear qc relative weight
!        rdiagbuf(14,ii) = errinv_input       ! prepbufr inverse obs error
!        rdiagbuf(15,ii) = errinv_adjst       ! read_prepbufr inverse obs error
!        rdiagbuf(16,ii) = errinv_final       ! final inverse observation error
!        rdiagbuf(17,ii) = data(ihat1,i)      ! observation
!        rdiagbuf(18,ii) = d1diff             ! obs-ges used in analysis
!        rdiagbuf(19,ii) = data(ihat1,i)-srw1gesin ! obs-ges w/o bias correction (future slot)
!        rdiagbuf(20,ii) = data(ihat2,i)      ! observation
!        rdiagbuf(21,ii) = d2diff             ! obs_ges used in analysis
!        rdiagbuf(22,ii) = data(ihat2,i)-srw2gesin ! obs-ges w/o bias correction (future slot)
!        rdiagbuf(23,ii) = factw              ! 10m wind reduction factor
!        rdiagbuf(24,ii)= data(irange,i)      ! superob mean range from radar (m)
    else if (obtype == ' rw') then
       allocate(cdiagbuf(ii),rdiagbuf(nreal,ii))
       read(iunit) cdiagbuf(1:ii),rdiagbuf(:,1:ii)
       do n=1,ii
          nob = nob + 1
          x_code(nob) = rdiagbuf(1,n)
          x_lat(nob) = rdiagbuf(3,n)
          x_lon(nob) = rdiagbuf(4,n)
          x_press(nob) = rdiagbuf(6,n)
          x_time(nob) = rdiagbuf(8,n)
          !x_stnelev(nob) = rdiagbuf(5,n)
          x_stnelev(nob) = rdiagbuf(7,n) ! use ob height instead
          if (rdiagbuf(14,n) > 1.e-5) then
            x_errorig(nob) = (1.0/rdiagbuf(14,n))**2
          else
            x_errorig(nob) = 1.e10
          endif
          x_err(nob) = (1.0/rdiagbuf(16,n))**2
          x_obs(nob) = rdiagbuf(17,n)
          h_x(nob) = rdiagbuf(17,n)-rdiagbuf(18,n)
          obtype = '  u'
          call strtoarr(obtype, x_type(nob,:), 3)
          call strtoarr(cdiagbuf(n), x_station_id(nob,:), 8)
          x_use(nob) = rdiagbuf(12,n)
          nob = nob + 1
          x_code(nob) = rdiagbuf(1,n)
          x_lat(nob) = rdiagbuf(3,n)
          x_lon(nob) = rdiagbuf(4,n)
          x_press(nob) = rdiagbuf(6,n)
          x_time(nob) = rdiagbuf(8,n)
          x_stnelev(nob) = rdiagbuf(5,n)
          if (rdiagbuf(14,n) > 1.e-5) then
            x_errorig(nob) = (1.0/rdiagbuf(14,n))**2
          else
            x_errorig(nob) = 1.e10
          endif
          x_err(nob) = (1.0/rdiagbuf(16,n))**2
          x_obs(nob) = rdiagbuf(20,n)
          h_x(nob) = rdiagbuf(20,n)-rdiagbuf(21,n)
          obtype = '  v'
          call strtoarr(obtype, x_type(nob,:), 3)
          call strtoarr(cdiagbuf(n), x_station_id(nob,:), 8)
          x_use(nob) = rdiagbuf(12,n)
       enddo
       deallocate(cdiagbuf,rdiagbuf)
! radar radial winds
!        cdiagbuf(ii)    = station_id         ! station id
!        rdiagbuf(1,ii)  = ictype(ikx)        ! observation type
!        rdiagbuf(2,ii)  = icsubtype(ikx)     ! observation subtype
!        rdiagbuf(3,ii)  = data(ilate,i)      ! observation latitude (degrees)
!        rdiagbuf(4,ii)  = data(il1.0,i)      ! observation longitude (degrees)
!        rdiagbuf(5,ii)  = data(ielev,i)      ! station elevation (meters)
!        rdiagbuf(6,ii)  = presw              ! observation pressure (hPa)
!        rdiagbuf(7,ii)  = data(ihgt,i)       ! observation height (meters)
!        rdiagbuf(8,ii)  = dtime              ! obs time (hours relative to analysis time)
!        rdiagbuf(9,ii)  = rmiss_single       ! input prepbufr qc or event mark
!        rdiagbuf(10,ii) = rmiss_single       ! setup qc or event mark
!        rdiagbuf(11,ii) = data(iuse,i)       ! read_prepbufr data usage flag
!        rdiagbuf(12,ii) = 1.0             ! analysis usage flag (1=use, -1=not used)
!        rdiagbuf(12,ii) = -1.0
!        rdiagbuf(13,ii) = rwgt               ! nonlinear qc relative weight
!        rdiagbuf(14,ii) = errinv_input       ! prepbufr inverse obs error (m/s)**-1
!        rdiagbuf(15,ii) = errinv_adjst       ! read_prepbufr inverse obs error (m/s)**-1
!        rdiagbuf(16,ii) = errinv_final       ! final inverse observation error (m/s)**-1
!        rdiagbuf(17,ii) = data(irwob,i)      ! radial wind speed observation (m/s)
!        rdiagbuf(18,ii) = ddiff              ! obs-ges used in analysis (m/s)
!        rdiagbuf(19,ii) = data(irwob,i)-rwwind  ! obs-ges w/o bias correction (m/s) (future slot)
!        rdiagbuf(20,ii)=data(iazm,i)*rad2deg ! azimuth angle
!        rdiagbuf(21,ii)=data(itilt,i)*rad2deg! tilt angle
!        rdiagbuf(22,ii) = factw              ! 10m wind reduction factor
    else if (obtype == 'gps') then
       allocate(cdiagbuf(ii),rdiagbuf(nreal,ii))
       read(iunit) cdiagbuf(1:ii),rdiagbuf(:,1:ii)
       do n=1,ii
          nob = nob + 1
          x_code(nob) = rdiagbuf(1,n)
          x_lat(nob) = rdiagbuf(3,n)
          x_lon(nob) = rdiagbuf(4,n)
          x_press(nob) = rdiagbuf(6,n)
          x_time(nob) = rdiagbuf(8,n)
          x_stnelev(nob) = rdiagbuf(7,n)
          if (rdiagbuf(14,n) > 1.e-5) then
            x_errorig(nob) = (1.0/rdiagbuf(14,n))**2
          else
            x_errorig(nob) = 1.e10
          end if
          x_err(nob) = (1.0/rdiagbuf(16,n))**2
          x_obs(nob) = rdiagbuf(17,n)
! Convert to innovation (as pointed out by Lidia)
          h_x(nob) = rdiagbuf(17,n) - (rdiagbuf(5,n)*rdiagbuf(17,n))
          call strtoarr(obtype, x_type(nob,:), 3)
          call strtoarr(cdiagbuf(n), x_station_id(nob,:), 8)
          x_use(nob) = rdiagbuf(12,n)
       enddo
       deallocate(cdiagbuf,rdiagbuf)
! refractivity (setupref.f90)
!    rdiagbuf(1,i)         = ictype(ikx)    ! observation type
!    rdiagbuf(2,i)         = 0.0           ! uses gps_ref (1.0=use of bending angle)
!    rdiagbuf(3,i)         = data(ilate,i)  ! lat in degrees
!    rdiagbuf(4,i)         = data(il1.0,i)  ! lon in degrees
!    rdiagbuf(5,i)    = gps2work(3,i) ! incremental bending angle (x100 %)
!    rdiagbuf(6,i)         = pressure(i)    ! guess observation pressure (hPa)
!    rdiagbuf(7,i)         = elev           ! height in meters
!    rdiagbuf(8,i)         = dtime          ! obs time (hours relative to analysis time)
!    rdiagbuf(9,i)         = data(ipctc,i)  ! input bufr qc - index of per cent confidence    
!    rdiagbuf(9,i)         = elev-zsges     ! height above model terrain (m)      
!    rdiagbuf(11,i)        = data(iuse,i)   ! data usage flag
! bending angle (setupbend.f90)
!    rdiagbuf(1,i)         = ictype(ikx)     ! observation type
!    rdiagbuf(2,i)         = 1.0             ! uses gps_ref (1.0 = use of bending angle)
!    rdiagbuf(3,i)         = data(ilate,i)   ! lat in degrees
!    rdiagbuf(4,i)         = data(il1.0,i)   ! lon in degrees
!    rdiagbuf(5,i)    = gps2work(3,i) ! incremental bending angle (x100 %)
!    rdiagbuf(6,i)         = dpressure(i)    ! guess observation pressure (hPa)
!    rdiagbuf(7,i)         = tpdpres-rocprof ! impact height in meters
!    rdiagbuf(8,i)         = dtptimes        ! obs time (hours relative to analysis time)
!    rdiagbuf(9,i)         = data(ipctc,i)   ! input bufr qc - index of per cent confidence
!    if(qcfail_loc(i) == 1.0) rdiagbuf(10,i) = 1.0
!    if(qcfail_high(i) == 1.0) rdiagbuf(10,i) = two
!    if(qcfail_gross(i) == 1.0) then
!        if(qcfail_high(i) == 1.0) then
!           rdiagbuf(10,i) = four
!        else
!           rdiagbuf(10,i) = three
!        endif
!    else if(qcfail_stats_1(i) == 1.0) then
!       if(qcfail_high(i) == 1.0) then
!           rdiagbuf(10,i) = six
!        else
!           rdiagbuf(10,i) = five
!        endif
!    else if(qcfail_stats_2(i) == 1.0) then
!       if(qcfail_high(i) == 1.0) then
!           rdiagbuf(10,i) = eight
!        else
!           rdiagbuf(10,i) = seven
!        endif
!    end if
!    if(muse(i)) then            ! modified in genstats_gps due to toss_gps
!       rdiagbuf(12,i) = 1.0     ! minimization usage flag (1=use, -1=not used)
!    else
!       rdiagbuf(12,i) = -1.0
!    endif
!     rdiagbuf(13,i) = 0.0 !nonlinear qc relative weight - will be defined in genstats_gps
!     rdiagbuf(14,i) = errinv_input ! original inverse gps obs error (N**-1)
!     rdiagbuf(15,i) = errinv_adjst ! original + represent error inverse gps 
!                                   ! obs error (N**-1)
!     rdiagbuf(16,i) = errinv_final ! final inverse observation error due to 
!                                   ! superob factor (N**-1)
!                                   ! modified in genstats_gps
!      rdiagbuf (17,i)  = data(igps,i)  ! refractivity observation (units of N)
!      rdiagbuf (18,i)  = data(igps,i)-nrefges ! obs-ges used in analysis (units of N) 
!      rdiagbuf (19,i)  = data(igps,i)-nrefges ! obs-ges w/o bias correction (future slot)  
!    rdiagbuf(11,i)        = data(iuse,i)    ! data usage flag
!    rdiagbuf (17,i)  = data(igps,i)  ! bending angle observation (degrees)
!    rdiagbuf (18,i)  = data(igps,i)-dbend(i) ! obs-ges used in analysis (degrees)
!    rdiagbuf (19,i)  = data(igps,i)-dbend(i) ! obs-ges w/o bias correction (future slot)
    else if (obtype == ' dw') then
       allocate(cdiagbuf(ii),rdiagbuf(nreal,ii))
       read(iunit) cdiagbuf(1:ii),rdiagbuf(:,1:ii)
       do n=1,ii
          nob = nob + 1
          x_code(nob) = rdiagbuf(1,n)
          x_lat(nob) = rdiagbuf(3,n)
          x_lon(nob) = rdiagbuf(4,n)
          x_press(nob) = rdiagbuf(6,n)
          x_time(nob) = rdiagbuf(8,n)
          x_stnelev(nob) = rdiagbuf(5,n)
          if (rdiagbuf(14,n) > 1.e-5) then
            x_errorig(nob) = (1.0/rdiagbuf(14,n))**2
          else
            x_errorig(nob) = 1.e10
          endif
          x_err(nob) = (1.0/rdiagbuf(16,n))**2
          x_obs(nob) = rdiagbuf(17,n)
          h_x(nob) = rdiagbuf(17,n)-rdiagbuf(18,n)
          call strtoarr(obtype, x_type(nob,:), 3)
          call strtoarr(cdiagbuf(n), x_station_id(nob,:), 8)
          x_use(nob) = rdiagbuf(12,n)
       enddo
       deallocate(cdiagbuf,rdiagbuf)
! doppler lidar winds
!        cdiagbuf(ii)    = station_id         ! station id
!        rdiagbuf(1,ii)  = ictype(ikx)        ! observation type
!        rdiagbuf(2,ii)  = icsubtype(ikx)     ! observation subtype
!        rdiagbuf(3,ii)  = data(ilate,i)      ! observation latitude (degrees)
!        rdiagbuf(4,ii)  = data(il1.0,i)      ! observation longitude (degrees)
!        rdiagbuf(5,ii)  = rmiss_single       ! station elevation (meters)
!        rdiagbuf(6,ii)  = presw              ! observation pressure (hPa)
!        rdiagbuf(7,ii)  = data(ihgt,i)       ! observation height (meters)
!        rdiagbuf(8,ii)  = dtime              ! obs time (hours relative to analysis time)
!        rdiagbuf(9,ii)  = rmiss_single       ! input prepbufr qc or event mark
!        rdiagbuf(10,ii) = rmiss_single       ! setup qc or event mark
!        rdiagbuf(11,ii) = data(iuse,i)       ! read_prepbufr data usage flag
!        rdiagbuf(12,ii) = 1.0             ! analysis usage flag (1=use, -1=not used)
!        rdiagbuf(12,ii) = -1.0
!        rdiagbuf(13,ii) = rwgt               ! nonlinear qc relative weight
!        rdiagbuf(14,ii) = errinv_input       ! prepbufr inverse obs error
!        rdiagbuf(15,ii) = errinv_adjst       ! read_prepbufr inverse obs error
!        rdiagbuf(16,ii) = errinv_final       ! final inverse observation error
!        rdiagbuf(17,ii) = data(ilob,i)       ! observation
!        rdiagbuf(18,ii) = ddiff              ! obs-ges used in analysis 
!        rdiagbuf(19,ii) = data(ilob,i)-dwwind! obs-ges w/o bias correction (future slot)
!        rdiagbuf(20,ii) = factw              ! 10m wind reduction factor
!        rdiagbuf(21,ii) = data(ielva,i)*rad2deg! elevation angle (degrees)
!        rdiagbuf(22,ii) = data(iazm,i)*rad2deg ! bearing or azimuth (degrees)
!        rdiagbuf(23,ii) = data(inls,i)         ! number of laser shots
!        rdiagbuf(24,ii) = data(incls,i)        ! number of cloud laser shots
!        rdiagbuf(25,ii) = data(iatd,i)         ! atmospheric depth
!        rdiagbuf(26,ii) = data(ilob,i)         ! line of sight component of wind orig.
    else if (obtype == ' pw') then
       allocate(cdiagbuf(ii),rdiagbuf(nreal,ii))
       read(iunit) cdiagbuf(1:ii),rdiagbuf(:,1:ii)
       do n=1,ii
          nob = nob + 1
          x_code(nob) = rdiagbuf(1,n)
          x_lat(nob) = rdiagbuf(3,n)
          x_lon(nob) = rdiagbuf(4,n)
          x_press(nob) = rdiagbuf(6,n)
          x_time(nob) = rdiagbuf(8,n)
          x_stnelev(nob) = rdiagbuf(5,n)
          if (rdiagbuf(14,n) > 1.e-5) then
            x_errorig(nob) = (1.0/rdiagbuf(14,n))**2
          else
            x_errorig(nob) = 1.e10
          endif
          x_err(nob) = (1.0/rdiagbuf(16,n))**2
          x_obs(nob) = rdiagbuf(17,n)
          h_x(nob) = rdiagbuf(17,n)-rdiagbuf(18,n)
          call strtoarr(obtype, x_type(nob,:), 3)
          call strtoarr(cdiagbuf(n), x_station_id(nob,:), 8)
          x_use(nob) = rdiagbuf(12,n)
       enddo
       deallocate(cdiagbuf,rdiagbuf)
! total column water
!        cdiagbuf(ii)    = station_id         ! station id
!        rdiagbuf(1,ii)  = ictype(ikx)        ! observation type
!        rdiagbuf(2,ii)  = icsubtype(ikx)     ! observation subtype
!        rdiagbuf(3,ii)  = data(ilate,i)      ! observation latitude (degrees)
!        rdiagbuf(4,ii)  = data(il1.0,i)      ! observation longitude (degrees)
!        rdiagbuf(5,ii)  = data(istnelv,i)    ! station elevation (meters)
!        rdiagbuf(6,ii)  = data(iobsprs,i)    ! observation pressure (hPa)
!        rdiagbuf(7,ii)  = data(iobshgt,i)    ! observation height (meters)
!        rdiagbuf(8,ii)  = dtime              ! obs time (hours relative to analysis time)
!        rdiagbuf(9,ii)  = data(iqc,i)        ! input prepbufr qc or event mark
!        rdiagbuf(10,ii) = rmiss_single       ! setup qc or event mark
!        rdiagbuf(11,ii) = data(iuse,i)       ! read_prepbufr data usage flag
!        rdiagbuf(12,ii) = 1.0             ! analysis usage flag (1=use, -1=not used)
!        rdiagbuf(12,ii) = -1.0
!        rdiagbuf(13,ii) = rwgt               ! nonlinear qc relative weight
!        rdiagbuf(14,ii) = errinv_input       ! prepbufr inverse obs error
!        rdiagbuf(15,ii) = errinv_adjst       ! read_prepbufr inverse obs error
!        rdiagbuf(16,ii) = errinv_final       ! final inverse observation error
!        rdiagbuf(17,ii) = dpw                ! total precipitable water obs (kg/m**2)
!        rdiagbuf(18,ii) = ddiff              ! obs-ges used in analysis (kg/m**2)
!        rdiagbuf(19,ii) = dpw-pwges          ! obs-ges w/o bias correction (kg/m**2) (future slot)
    else
          print *,'warning - unknown ob type ',obtype
    end if
    go to 10
20  continue
    print *,'error reading diag_conv file'
30  continue
    if (nob .ne. nobs_max) then
        print *,'number of obs not what expected in get_convobsata',nob,nobs_max
        stop
    end if
    close(iunit)

end subroutine get_convobs_data

subroutine strtoarr(strin, chararr, n_str)
  integer, intent(in) :: n_str
  character(len=n_str), intent(in) :: strin
  integer, intent(out) ::  chararr(n_str+1)
  chararr = 32 ! space
  do j=1,n_str
     chararr(j) = ichar(strin(j:j))
  enddo
  chararr(n_str+1) = 124 ! '|'
end subroutine strtoarr
