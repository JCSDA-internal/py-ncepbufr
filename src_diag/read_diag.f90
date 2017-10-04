!$$$  subprogram documentation block
!                .      .    .                                       .
! subprogram:    read_raddiag                       read rad diag file
!   prgmmr: tahara           org: np20                date: 2003-01-01
!
! abstract:  This module contains code to process radiance
!            diagnostic files.  The module defines structures
!            to contain information from the radiance
!            diagnostic files and then provides two routines
!            to access contents of the file.
!
! program history log:
!   2005-07-22 treadon - add this doc block
!   2010-10-05 treadon - refactor code to GSI standard
!   2010-10-08 zhu     - use data_tmp to handle various npred values
!   2011-02-22 kleist  - changes related to memory allocate/deallocate
!   2011-04-08 li      - add tref, dtw, dtc to diag_data_fix_list, add tb_tz to diag_data_chan_list
!                      - correspondingly, change ireal_radiag (26 -> 30) and ipchan_radiag (7 -> 8)
!   2011-07-24 safford - make structure size for reading data_fix data version dependent 
!   2013-11-21 todling - revisit how versions are set (add set/get_radiag)
!   2014-01-27 todling - add ob sensitivity index
!
! contains
!   read_radiag_header - read radiance diagnostic file header
!   read_radiag_data   - read radiance diagnostic file data
!
! attributes:
!   language: f90
!   machine:  ibm RS/6000 SP
!
!$$$

module read_diag

  implicit none

! Declare public and private
  private

  public :: diag_header_fix_list
  public :: diag_header_chan_list
  public :: diag_data_name_list
  public :: diag_data_fix_list
  public :: diag_data_chan_list
  public :: diag_data_extra_list
  public :: read_radiag_header
  public :: read_radiag_data
  public :: iversion_radiag
! public :: iversion_radiag_1
! public :: iversion_radiag_2
! public :: iversion_radiag_3
! public :: iversion_radiag_4
  public :: ireal_radiag
  public :: ipchan_radiag
  public :: set_radiag
  public :: get_radiag

  interface set_radiag
         module procedure set_radiag_int_ ! internal procedure for integers
  end interface
  interface get_radiag
         module procedure get_radiag_int_ ! internal procedure for integers
  end interface

  integer,parameter :: ireal_radiag  = 30   ! number of real entries per spot in radiance diagnostic file
  integer,parameter :: ireal_old_radiag  = 26   ! number of real entries per spot in versions older than iversion_radiag_2
  integer,parameter :: ipchan_radiag = 8    ! number of entries per channel per spot in radiance diagnostic file

! Declare structures for radiance diagnostic file information
  type diag_header_fix_list
     character(len=20) :: isis           ! sat and sensor type
     character(len=10) :: id             ! sat type
     character(len=10) :: obstype        ! observation type
     integer :: jiter            ! outer loop counter
     integer :: nchan            ! number of channels in the sensor
     integer :: npred            ! number of updating bias correction predictors
     integer :: idate            ! time (yyyymmddhh)
     integer :: ireal            ! # of real elements in the fix part of a data record
     integer :: ipchan           ! # of elements for each channel except for bias correction terms
     integer :: iextra           ! # of extra elements for each channel
     integer :: jextra           ! # of extra elements
     integer :: idiag            ! first dimension of diag_data_chan
     integer :: angord           ! order of polynomial for adp_anglebc option
     integer :: iversion         ! radiance diagnostic file version number
     integer :: inewpc           ! indicator of newpc4pred (1 on, 0 off)
     integer :: ijacob           ! indicates whether jacobian included (1 yes, 0 no)
     integer :: isens            ! sensitivity index
  end type diag_header_fix_list

  type diag_data_name_list
     character(len=10),dimension(ireal_radiag) :: fix
     character(len=10),dimension(:),allocatable :: chn
  end type diag_data_name_list
  
  type diag_header_chan_list
     real :: freq              ! frequency (Hz)
     real :: polar             ! polarization
     real :: wave              ! wave number (cm^-1)
     real :: varch             ! error variance (or SD error?)
     real :: tlapmean          ! mean lapse rate
     integer:: iuse              ! use flag
     integer:: nuchan            ! sensor relative channel number
     integer:: iochan            ! satinfo relative channel number
  end type diag_header_chan_list

  type diag_data_fix_list
     real :: lat               ! latitude (deg)
     real :: lon               ! longitude (deg)
     real :: zsges             ! guess elevation at obs location (m)
     real :: obstime           ! observation time relative to analysis
     real :: senscn_pos        ! sensor scan position (integer)
     real :: satzen_ang        ! satellite zenith angle (deg)
     real :: satazm_ang        ! satellite azimuth angle (deg)
     real :: solzen_ang        ! solar zenith angle (deg)
     real :: solazm_ang        ! solar azimumth angle (deg)
     real :: sungln_ang        ! sun glint angle (deg)
     real :: water_frac        ! fractional coverage by water
     real :: land_frac         ! fractional coverage by land
     real :: ice_frac          ! fractional coverage by ice
     real :: snow_frac         ! fractional coverage by snow
     real :: water_temp        ! surface temperature over water (K)
     real :: land_temp         ! surface temperature over land (K)
     real :: ice_temp          ! surface temperature over ice (K)
     real :: snow_temp         ! surface temperature over snow (K)
     real :: soil_temp         ! soil temperature (K)
     real :: soil_mois         ! soil moisture 
     real :: land_type         ! land type (integer)
     real :: veg_frac          ! vegetation fraction
     real :: snow_depth        ! snow depth
     real :: sfc_wndspd        ! surface wind speed
     real :: qcdiag1           ! ir=cloud fraction, mw=cloud liquid water
     real :: qcdiag2           ! ir=cloud top pressure, mw=total column water
     real :: tref              ! reference temperature (Tr) in NSST
     real :: dtw               ! dt_warm at zob
     real :: dtc               ! dt_cool at zob
     real :: tz_tr             ! d(Tz)/d(Tr)
  end type diag_data_fix_list

  type diag_data_chan_list
     real :: tbobs              ! Tb (obs) (K)
     real :: omgbc              ! Tb_(obs) - Tb_(simulated w/ bc)  (K)
     real :: omgnbc             ! Tb_(obs) - Tb_(simulated_w/o bc) (K)
     real :: sprd               ! ensemble spread
     real :: errinv             ! inverse error (K**(-1))
     real :: qcmark             ! quality control mark
     real :: emiss              ! surface emissivity
     real :: tlap               ! temperature lapse rate
     real :: tb_tz              ! d(Tb)/d(Tz)
     real :: bicons             ! constant bias correction term
     real :: biang              ! scan angle bias correction term
     real :: biclw              ! CLW bias correction term
     real :: bilap2             ! square lapse rate bias correction term
     real :: bilap              ! lapse rate bias correction term
     real :: bicos              ! node*cos(lat) bias correction term
     real :: bisin              ! sin(lat) bias correction term
     real :: biemis             ! emissivity sensitivity bias correction term
     real,dimension(:),allocatable :: bifix          ! angle dependent bias
     real :: bisst              ! SST bias correction term
  end type diag_data_chan_list

  type diag_data_extra_list
     real :: extra              ! extra information
  end type diag_data_extra_list

  integer,save     :: iversion_radiag             ! Current version (see set routine)
  integer,parameter:: iversion_radiag_1 = 11104   ! Version when bias-correction entries were modified 
  integer,parameter:: iversion_radiag_2 = 13784   ! Version when NSST entries were added 
  integer,parameter:: iversion_radiag_3 = 19180   ! Version when SSMIS added
  integer,parameter:: iversion_radiag_4 = 30303   ! Version when emissivity predictor added
  integer,parameter:: iversion_radiag_5 = 40000   ! Version when ensemble spread added

  real,parameter::  rmiss_radiag    = -9.9e11

contains

subroutine set_radiag_int_ (what,iv,ier)
character(len=*),intent(in) :: what
integer,intent(in) :: iv
integer,intent(out):: ier
ier=-1
if(trim(what)=='version') then
  iversion_radiag = iv
  ier=0
endif
end subroutine set_radiag_int_

subroutine get_radiag_int_ (what,iv,ier)
character(len=*),intent(in) :: what
integer,intent(out):: iv
integer,intent(out):: ier
ier=-1
if(trim(what)=='version') then
  iv = iversion_radiag
  ier=0
endif
end subroutine get_radiag_int_

subroutine read_radiag_header(ftin,retrieval,header_fix,header_chan,data_name,iflag,lverbose)
!                .      .    .                                       .
! subprogram:    read_diag_header                 read rad diag header
!   prgmmr: tahara           org: np20                date: 2003-01-01
!
! abstract:  This routine reads the header record from a radiance
!            diagnostic file
!
! program history log:
!   2010-10-05 treadon - add this doc block
!   2011-02-22 kleist  - changes related to memory allocation and standard output
!
! input argument list:
!   ftin          - unit number connected to diagnostic file 
!   retrieval     - .true. if sst retrieval
!
! output argument list:
!   header_fix    - header information structure
!   header_chan   - channel information structure
!   data_name     - diag file data names
!   iflag         - error code
!   lverbose      - optional flag to turn off default output to standard out 
!
! attributes:
!   language: f90
!   machine:  ibm RS/6000 SP
!
!$$$

! Declare passed arguments
  integer,intent(in)             :: ftin
  logical,intent(in)                     :: retrieval
  type(diag_header_fix_list ),intent(out):: header_fix
  type(diag_header_chan_list),allocatable :: header_chan(:)
  type(diag_data_name_list)              :: data_name
  integer,intent(out)            :: iflag
  logical,optional,intent(in)            :: lverbose    

!  Declare local variables
  character(len=2):: string
  character(len=10):: satid,sentype
  character(len=20):: sensat
  integer :: i,ich
  integer:: jiter,nchanl,npred,ianldate,ireal,ipchan,iextra,jextra
  integer:: idiag,angord,iversion,inewpc,isens,ijacob
  integer:: iuse_tmp,nuchan_tmp,iochan_tmp
  real :: freq_tmp,polar_tmp,wave_tmp,varch_tmp,tlapmean_tmp
  logical loutall

  loutall=.true.
  if(present(lverbose)) loutall=lverbose

! Read header (fixed_part).
  read(ftin,IOSTAT=iflag)  sensat,satid,sentype,jiter,nchanl,npred,ianldate,&
          ireal,ipchan,iextra,jextra,idiag,angord,iversion,inewpc,isens,ijacob
  if (iflag/=0) then
     rewind(ftin)
     read(ftin,IOSTAT=iflag) sensat,satid,sentype,jiter,nchanl,npred,ianldate,&
          ireal,ipchan,iextra,jextra,idiag,angord,iversion,inewpc,isens
     ijacob=0
     if (iflag/=0) then
        rewind(ftin)
        read(ftin,IOSTAT=iflag) sensat,satid,sentype,jiter,nchanl,npred,ianldate,&
             ireal,ipchan,iextra,jextra,idiag,angord,iversion,inewpc
        isens=0
     end if
  end if

  if (iflag/=0) then
     rewind(ftin)
     read(ftin,IOSTAT=iflag) sensat,satid,sentype,jiter,nchanl,npred,ianldate,&
          ireal,ipchan,iextra,jextra
     idiag=ipchan+npred+1
     angord=0
     iversion=0
     inewpc=0
     isens=0
     if (iflag/=0) then
        write(6,*)'READ_RADIAG_HEADER:  ***ERROR*** Unknown file format.  Cannot read'
        return
     endif
  endif

  header_fix%isis    = sensat
  header_fix%id      = satid
  header_fix%obstype = sentype
  header_fix%jiter   = jiter
  header_fix%nchan   = nchanl
  header_fix%npred   = npred
  header_fix%idate   = ianldate
  header_fix%ireal   = ireal
  header_fix%ipchan  = ipchan
  header_fix%iextra  = iextra
  header_fix%jextra  = jextra
  header_fix%idiag   = idiag
  header_fix%ijacob  = ijacob
  header_fix%angord  = angord
  header_fix%iversion= iversion
  header_fix%inewpc  = inewpc
  header_fix%isens   = isens

  if (loutall) then
     write(6,*)'READ_RADIAG_HEADER:  isis=',header_fix%isis,&
          ' nchan=',header_fix%nchan,&
          ' npred=',header_fix%npred,&
          ' angord=',header_fix%angord,&
          ' idiag=',header_fix%idiag,&
          ' iversion=',header_fix%iversion,&
          ' inewpc=',header_fix%inewpc,&
          ' isens=',header_fix%isens,&
          ' ijacob=',header_fix%ijacob
     
     if ( header_fix%iextra /= 0) &
          write(6,*)'READ_RADIAG_HEADER:  extra diagnostic information available, ',&
          'iextra=',header_fix%iextra
  end if

! Allocate and initialize as needed
     if (allocated(header_chan)) deallocate(header_chan)
     if (allocated(data_name%chn))  deallocate(data_name%chn)

     allocate(header_chan( header_fix%nchan))
     allocate(data_name%chn(header_fix%idiag))

     data_name%fix(1) ='lat       '
     data_name%fix(2) ='lon       '
     data_name%fix(3) ='zsges     '
     data_name%fix(4) ='obstim    '
     data_name%fix(5) ='scanpos   '
     data_name%fix(6) ='satzen    '
     data_name%fix(7) ='satazm    '
     data_name%fix(8) ='solzen    '
     data_name%fix(9) ='solazm    '
     data_name%fix(10)='sungln    '
     data_name%fix(11)='fwater    '
     data_name%fix(12)='fland     '
     data_name%fix(13)='fice      '
     data_name%fix(14)='fsnow     '
     data_name%fix(15)='twater    '
     data_name%fix(16)='tland     '
     data_name%fix(17)='tice      '
     data_name%fix(18)='tsnow     '
     data_name%fix(19)='tsoil     '
     data_name%fix(20)='soilmoi   '
     data_name%fix(21)='landtyp   '
     data_name%fix(22)='vegfrac   '
     data_name%fix(23)='snowdep   '
     data_name%fix(24)='wndspd    '
     data_name%fix(25)='qc1       '
     data_name%fix(26)='qc2       '
     data_name%fix(27)='tref      '
     data_name%fix(28)='dtw       '
     data_name%fix(29)='dtc       '
     data_name%fix(30)='tz_tr     '

     data_name%chn(1)='obs       '
     data_name%chn(2)='omgbc     '
     data_name%chn(3)='omgnbc    '
     data_name%chn(4)='errinv    '
     data_name%chn(5)='qcmark    '
     data_name%chn(6)='emiss     '
     data_name%chn(7)='tlap      '
     data_name%chn(8)='tb_tz     '

     if (header_fix%iversion < iversion_radiag_1) then
        data_name%chn( 8)= 'bifix     '
        data_name%chn( 9)= 'bilap     '
        data_name%chn(10)= 'bilap2    '
        data_name%chn(11)= 'bicons    '
        data_name%chn(12)= 'biang     '
        data_name%chn(13)= 'biclw     '
        if (retrieval) data_name%chn(13)= 'bisst     '
     elseif ( header_fix%iversion < iversion_radiag_2 .and. header_fix%iversion >= iversion_radiag_1 ) then
        data_name%chn( 8)= 'bicons    '
        data_name%chn( 9)= 'biang     '
        data_name%chn(10)= 'biclw     '
        data_name%chn(11)= 'bilap2    '
        data_name%chn(12)= 'bilap     '
        do i=1,header_fix%angord
           write(string,'(i2.2)') header_fix%angord-i+1
           data_name%chn(12+i)= 'bifix' // string
        end do
        data_name%chn(12+header_fix%angord+1)= 'bifix     '
        data_name%chn(12+header_fix%angord+2)= 'bisst     '
     elseif ( header_fix%iversion < iversion_radiag_3 .and. header_fix%iversion >= iversion_radiag_2 ) then
        data_name%chn( 9)= 'bicons    '
        data_name%chn(10)= 'biang     '
        data_name%chn(11)= 'biclw     '
        data_name%chn(12)= 'bilap2    '
        data_name%chn(13)= 'bilap     '
        do i=1,header_fix%angord
           write(string,'(i2.2)') header_fix%angord-i+1
           data_name%chn(13+i)= 'bifix' // string
        end do
        data_name%chn(13+header_fix%angord+1)= 'bifix     '
        data_name%chn(13+header_fix%angord+2)= 'bisst     '
     elseif ( header_fix%iversion < iversion_radiag_4 .and. header_fix%iversion >= iversion_radiag_3 ) then
        data_name%chn( 9)= 'bicons    '
        data_name%chn(10)= 'biang     '
        data_name%chn(11)= 'biclw     '
        data_name%chn(12)= 'bilap2    '
        data_name%chn(13)= 'bilap     '
        data_name%chn(14)= 'bicos     '
        data_name%chn(15)= 'bisin     '
        do i=1,header_fix%angord
           write(string,'(i2.2)') header_fix%angord-i+1
           data_name%chn(15+i)= 'bifix' // string
        end do
        data_name%chn(15+header_fix%angord+1)= 'bifix     '
        data_name%chn(15+header_fix%angord+2)= 'bisst     '
     else
        data_name%chn( 9)= 'bicons    '
        data_name%chn(10)= 'biang     '
        data_name%chn(11)= 'biclw     '
        data_name%chn(12)= 'bilap2    '
        data_name%chn(13)= 'bilap     '
        data_name%chn(14)= 'bicos     '
        data_name%chn(15)= 'bisin     '
        data_name%chn(16)= 'biemis    '
        do i=1,header_fix%angord
           write(string,'(i2.2)') header_fix%angord-i+1
           data_name%chn(16+i)= 'bifix' // string
        end do
        data_name%chn(16+header_fix%angord+1)= 'bifix     '
        data_name%chn(16+header_fix%angord+2)= 'bisst     '
     endif

! Read header (channel part)
  do ich=1, header_fix%nchan
      read(ftin,IOSTAT=iflag) freq_tmp,polar_tmp,wave_tmp,varch_tmp,tlapmean_tmp,iuse_tmp,nuchan_tmp,iochan_tmp
      header_chan(ich)%freq     = freq_tmp
      header_chan(ich)%polar    = polar_tmp
      header_chan(ich)%wave     = wave_tmp
      header_chan(ich)%varch    = varch_tmp
      header_chan(ich)%tlapmean = tlapmean_tmp
      header_chan(ich)%iuse     = iuse_tmp
      header_chan(ich)%nuchan   = nuchan_tmp
      header_chan(ich)%iochan   = iochan_tmp
     if (iflag/=0) return
  end do

! Construct array containing menonics for data record entries
  
     
end subroutine read_radiag_header

subroutine read_radiag_data(ftin,header_fix,retrieval,data_fix,data_chan,data_extra,iflag )
!                .      .    .                                       .
! subprogram:    read_radiag_dat                    read rad diag data
!   prgmmr: tahara           org: np20                date: 2003-01-01
!
! abstract:  This routine reads the data record from a radiance
!            diagnostic file
!
! program history log:
!   2010-10-05 treadon - add this doc block
!   2011-02-22 kleist  - changes related to memory allocation
!
! input argument list:
!   ftin - unit number connected to diagnostic file
!   header_fix - header information structure
!
! output argument list:
!   data_fix   - spot header information structure
!   data_chan  - spot channel information structure
!   data_extra - spot extra information
!   iflag      - error code
!
! attributes:
!   language: f90
!   machine:  ibm RS/6000 SP
!
!$$$


! Declare passed arguments
  integer,intent(in)             :: ftin
  type(diag_header_fix_list ),intent(in) :: header_fix
  logical,intent(in)                     :: retrieval
  type(diag_data_fix_list)   ,intent(out):: data_fix
  type(diag_data_chan_list)  ,allocatable :: data_chan(:)
  type(diag_data_extra_list) ,allocatable :: data_extra(:,:)
  integer,intent(out)            :: iflag
    
  integer :: ich,iang,i,j
  real,dimension(:,:),allocatable :: data_tmp
  real,dimension(:),allocatable   :: fix_tmp
  real,dimension(:,:),allocatable :: extra_tmp

! Allocate arrays as needed
  if (allocated(data_chan)) deallocate(data_chan)
  allocate(data_chan(header_fix%nchan))

  do ich=1,header_fix%nchan
     if (allocated(data_chan(ich)%bifix)) deallocate(data_chan(ich)%bifix)
     allocate(data_chan(ich)%bifix(header_fix%angord+1))
  end do

  if (header_fix%iextra > 0) then
     if (allocated(data_extra))   deallocate(data_extra)
     allocate(data_extra(header_fix%iextra,header_fix%jextra))
     allocate(extra_tmp(header_fix%iextra,header_fix%jextra))
  end if

! Allocate arrays to hold data record
  allocate(data_tmp(header_fix%idiag,header_fix%nchan))

  if (header_fix%iversion < iversion_radiag_2) then
     allocate( fix_tmp( ireal_old_radiag ) )
  else
     allocate( fix_tmp( ireal_radiag ) )
  end if

! Read data record

  if (header_fix%iextra == 0) then
     read(ftin,IOSTAT=iflag) fix_tmp, data_tmp
  else
     read(ftin,IOSTAT=iflag) fix_tmp, data_tmp, extra_tmp
  endif

  if (iflag /= 0) return

! Transfer fix_tmp record to output structure
  data_fix%lat = fix_tmp(1)
  data_fix%lon = fix_tmp(2)
  data_fix%zsges = fix_tmp(3)
  data_fix%obstime = fix_tmp(4) 
  data_fix%senscn_pos = fix_tmp(5)
  data_fix%satzen_ang = fix_tmp(6)
  data_fix%satazm_ang = fix_tmp(7)
  data_fix%solzen_ang = fix_tmp(8)
  data_fix%solazm_ang = fix_tmp(9)
  data_fix%sungln_ang = fix_tmp(10)
  data_fix%water_frac = fix_tmp(11)
  data_fix%land_frac = fix_tmp(12)
  data_fix%ice_frac = fix_tmp(13)
  data_fix%snow_frac = fix_tmp(14)
  data_fix%water_temp = fix_tmp(15)
  data_fix%land_temp = fix_tmp(16)
  data_fix%ice_temp = fix_tmp(17)
  data_fix%snow_temp = fix_tmp(18)
  data_fix%soil_temp = fix_tmp(19)
  data_fix%soil_mois = fix_tmp(20)
  data_fix%land_type = fix_tmp(21)
  data_fix%veg_frac = fix_tmp(22)
  data_fix%snow_depth = fix_tmp(23)
  data_fix%sfc_wndspd = fix_tmp(24)
  data_fix%qcdiag1 = fix_tmp(25)
  data_fix%qcdiag2 = fix_tmp(26)

  if ( header_fix%iversion <= iversion_radiag_1 ) then
     data_fix%tref = rmiss_radiag
     data_fix%dtw = rmiss_radiag
     data_fix%dtc = rmiss_radiag
     data_fix%tz_tr = rmiss_radiag
  else
     data_fix%tref = fix_tmp(27)
     data_fix%dtw = fix_tmp(28)
     data_fix%dtc = fix_tmp(29)
     data_fix%tz_tr = fix_tmp(30)
  end if


! Transfer data record to output structure
  do ich=1,header_fix%nchan
     data_chan(ich)%tbobs =data_tmp(1,ich)
     data_chan(ich)%omgbc =data_tmp(2,ich)
     data_chan(ich)%omgnbc=data_tmp(3,ich)
     data_chan(ich)%errinv=data_tmp(4,ich)
     data_chan(ich)%qcmark=data_tmp(5,ich)
     data_chan(ich)%emiss =data_tmp(6,ich)
     data_chan(ich)%tlap  =data_tmp(7,ich)
     data_chan(ich)%tb_tz =data_tmp(8,ich)
  end do
  if (header_fix%iversion < iversion_radiag_1) then
     do ich=1,header_fix%nchan
        data_chan(ich)%bifix(1)=data_tmp(8,ich)
        data_chan(ich)%bilap   =data_tmp(9,ich)
        data_chan(ich)%bilap2  =data_tmp(10,ich)
        data_chan(ich)%bicons  =data_tmp(11,ich)
        data_chan(ich)%biang   =data_tmp(12,ich)
        data_chan(ich)%biclw   =data_tmp(13,ich)
        data_chan(ich)%bisst   = rmiss_radiag
        if (retrieval) then
           data_chan(ich)%biclw   =rmiss_radiag
           data_chan(ich)%bisst   =data_tmp(13,ich) 
        endif
     end do
  elseif ( header_fix%iversion < iversion_radiag_2 .and. header_fix%iversion >= iversion_radiag_1 ) then
     do ich=1,header_fix%nchan
        data_chan(ich)%bicons=data_tmp(8,ich)
        data_chan(ich)%biang =data_tmp(9,ich)
        data_chan(ich)%biclw =data_tmp(10,ich)
        data_chan(ich)%bilap2=data_tmp(11,ich)
        data_chan(ich)%bilap =data_tmp(12,ich)
     end do
     do ich=1,header_fix%nchan
        do iang=1,header_fix%angord+1
           data_chan(ich)%bifix(iang)=data_tmp(12+iang,ich)
        end do
        data_chan(ich)%bisst = data_tmp(12+header_fix%angord+2,ich)  
     end do
  elseif ( header_fix%iversion < iversion_radiag_3 .and. header_fix%iversion >= iversion_radiag_2 ) then
     do ich=1,header_fix%nchan
        data_chan(ich)%bicons=data_tmp(9,ich)
        data_chan(ich)%biang =data_tmp(10,ich)
        data_chan(ich)%biclw =data_tmp(11,ich)
        data_chan(ich)%bilap2=data_tmp(12,ich)
        data_chan(ich)%bilap =data_tmp(13,ich)
     end do
     do ich=1,header_fix%nchan
        do iang=1,header_fix%angord+1
           data_chan(ich)%bifix(iang)=data_tmp(13+iang,ich)
        end do
        data_chan(ich)%bisst = data_tmp(13+header_fix%angord+2,ich)
     end do
  elseif ( header_fix%iversion < iversion_radiag_4 .and. header_fix%iversion >= iversion_radiag_3 ) then
     do ich=1,header_fix%nchan
        data_chan(ich)%bicons=data_tmp(9,ich)
        data_chan(ich)%biang =data_tmp(10,ich)
        data_chan(ich)%biclw =data_tmp(11,ich)
        data_chan(ich)%bilap2=data_tmp(12,ich)
        data_chan(ich)%bilap =data_tmp(13,ich)
        data_chan(ich)%bicos =data_tmp(14,ich) ! 1st bias correction term node*cos(lat) for SSMIS
        data_chan(ich)%bisin =data_tmp(15,ich) ! 2nd bias correction term sin(lat) for SSMI      
     end do
     do ich=1,header_fix%nchan
        do iang=1,header_fix%angord+1
           data_chan(ich)%bifix(iang)=data_tmp(15+iang,ich)
        end do
        data_chan(ich)%bisst = data_tmp(15+header_fix%angord+2,ich)
     end do
  elseif ( header_fix%iversion < iversion_radiag_5 .and. header_fix%iversion >= iversion_radiag_4 ) then
     do ich=1,header_fix%nchan
        data_chan(ich)%bicons=data_tmp(9,ich)
        data_chan(ich)%biang =data_tmp(10,ich)
        data_chan(ich)%biclw =data_tmp(11,ich)
        data_chan(ich)%bilap2=data_tmp(12,ich)
        data_chan(ich)%bilap =data_tmp(13,ich)
        data_chan(ich)%bicos =data_tmp(14,ich) 
        data_chan(ich)%bisin =data_tmp(15,ich)
        data_chan(ich)%biemis=data_tmp(16,ich)
     end do
     do ich=1,header_fix%nchan
        do iang=1,header_fix%angord+1
           data_chan(ich)%bifix(iang)=data_tmp(16+iang,ich)
        end do
        data_chan(ich)%bisst = data_tmp(16+header_fix%angord+2,ich)
     end do
  else
     do ich=1,header_fix%nchan
        data_chan(ich)%bicons=data_tmp(9,ich)
        data_chan(ich)%biang =data_tmp(10,ich)
        data_chan(ich)%biclw =data_tmp(11,ich)
        data_chan(ich)%bilap2=data_tmp(12,ich)
        data_chan(ich)%bilap =data_tmp(13,ich)
        data_chan(ich)%bicos =data_tmp(14,ich)
        data_chan(ich)%bisin =data_tmp(15,ich)
        data_chan(ich)%biemis=data_tmp(16,ich)
     end do
     do ich=1,header_fix%nchan
        do iang=1,header_fix%angord+1
           data_chan(ich)%bifix(iang)=data_tmp(16+iang,ich)
        end do
        data_chan(ich)%bisst = data_tmp(16+header_fix%angord+2,ich)  
        data_chan(ich)%sprd  = data_tmp(16+header_fix%angord+3,ich)
     end do
  endif

  if (header_fix%iextra > 0) then
     do j=1,header_fix%jextra
        do i=1,header_fix%iextra
           data_extra(i,j)%extra=extra_tmp(i,j)
        end do
     end do
  endif

  deallocate(data_tmp, fix_tmp)
  if (header_fix%iextra > 0) deallocate(extra_tmp)

end subroutine read_radiag_data

end module read_diag

