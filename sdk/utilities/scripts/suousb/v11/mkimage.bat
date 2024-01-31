@SETLOCAL
@set on_off=OFF
@echo %on_off%
SETLOCAL ENABLEEXTENSIONS
SETLOCAL ENABLEDELAYEDEXPANSION

set thisfile=%~0
set version_file=sw_version.h
set image_file=
set bin_file=
set this_folder=%~dp0

:more_options
shift
set verbose=%on_off%
if "%~0"=="" goto :no_more_options
if /i "%~0"=="-v" (set verbose=on
    goto :more_options)
if /i "%~0"=="-q" (set quiet=1
    goto :more_options)
if /i "%~0"=="/?" goto :help
if /i "%~0"=="--help" goto :help
if /i "%~0"=="-h" goto :help

:no_more_options
@rem ----------------------------------------------------------------
@rem Setup SDK root
@rem ----------------------------------------------------------------

if DEFINED SDKROOT goto :sdk_set

pushd %this_folder%\..\..\..\..
set SDKROOT=%CD%
popd

:sdk_set
if not defined quiet echo Using SDK from %SDKROOT%

set mkimage=%SDKROOT%\binaries\mkimage.exe

if not exist "%mkimage%" (
  echo "mkimage.exe not found, please build it"
  exit /B 1
)

if "%~0" == "" (
  echo No binary file specified
  exit /B 2
)

if not exist "%~0" (
  echo Binary file %0 does not exist
  exit /B 2
)
set bin_file=%~f0
shift

if not "%~0" == "" (
  set image_file=%~f0
  shift
)

set build=
if not exist %version_file% goto create_first_version_file

@rem Check version from version.h
for /F "tokens=*" %%i in ('type sw_version.h') do (call :extract_version %%i)

if defined build goto version_extracted

echo sw_version.h does not contain valid version info, recreating file
if exist sw_version.err del sw_version.err
ren sw_version.h sw_version.err

:create_first_version_file
set v1=1
set v2=0
set v3=0
set build=1

:version_extracted
set version_string=%v1%.%v2%.%v3%.%build%

:create_version_file
@rem Create sw_version.h in not present
for /f "tokens=2 delims==" %%a in ('WMIC OS Get LocalDateTime /value') do set dt=%%a
if not exist %version_file% (
  if not defined quiet echo Creating version info file
  echo #define BLACKORCA_SW_VERSION ^"%version_string%^" >%version_file%
  echo #define BLACKORCA_SW_VERSION_DATE ^"%dt:~0,4%-%dt:~4,2%-%dt:~6,2% %dt:~8,2%:%dt:~10,2% ^">>%version_file%
  echo #define BLACKORCA_SW_VERSION_STATUS ^"REPOSITORY VERSION^" >>%version_file%
)

if defined image_file goto makeimage
if not defined quiet echo No image file specified creating %bin_file:~0,-3%%version_string%.img
set image_file=%bin_file:~0,-3%%version_string%.img

:makeimage
@rem Run image creating tool
@echo %verbose%
echo "%mkimage%" single "%bin_file%" "%version_file%" "%image_file%" 
"%mkimage%" single "%bin_file%" "%version_file%" "%image_file%" 
@echo %on_off%

exit /B 0

:extract_version
set val=%3
if "%2"=="BLACKORCA_SW_VERSION" (
  for /F "tokens=1-4 delims=." %%a in ("%val:~1,-1%") do (
    set v1=%%a
    set v2=%%b
    set v3=%%c
    set build=%%d
  )
)
goto:eof

:help
echo Usage:
echo %thisfile% [/h] [/q] bin_file [image_file]
echo    where:
echo      -h - prints this help
echo      -q - reduce number of prints
echo.
echo "     bin_file - file with application binary"
echo "     image_file - output image file for SUOUSB"
echo.
echo Run this script from folder containing sw_wersion.h file
exit /b 0

