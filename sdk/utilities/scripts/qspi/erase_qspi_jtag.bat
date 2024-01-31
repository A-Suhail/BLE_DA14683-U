@SETLOCAL
@set on_off=OFF
@echo %on_off%
SETLOCAL ENABLEDELAYEDEXPANSION
@echo .......................................................................................................................
@echo ..
@echo .. ERASE QSPI 
@echo ..
@echo .......................................................................................................................
@echo.

set TMPCFG=

:more_options
if "%~1"=="" goto :no_more_options
if /i "%~1"=="--id" (set id=%2
    set device_sn=%2
    shift
    shift
    goto :more_options)
if /i "%~1"=="--cfg" (set id=%2
    set cfg=%2
    shift
    shift
    goto :more_options)
if /i "%~1"=="--jlink_path" (set jlink=%2
    shift
    shift
    goto :more_options)
    
:no_more_options

REM Ask for erasing qspi
set erase_confirm=n
@echo Are you sure you want to completely erase QSPI ^(y/n or [ENTER] for n^) ?
@set /p erase_confirm=-^>
@echo.

set result=false
if %erase_confirm% == y set result=true
if %erase_confirm% == Y set result=true
if %result% == false (
        goto Finished
)

if not defined %jlink goto no_jlink_path

REM Remove trailing slash if any
IF %jlink:~-2,-1%==/ SET jlink=%jlink:~0,-2%"

REM Transform slashes to backslashes
set jlink=%jlink:/=\%
@echo JlinkGDBServer path used: %jlink%

@REM Remove quotes if any
for /F "tokens=*" %%i in (%jlink%) do set jlink_path=%%~i
:no_jlink_path

IF NOT "%CFG%"=="" goto :exec_cli

set TMPCFG=%TEMP%\cfg_%RANDOM%.ini
set CFG=%TMPCFG%


set jlink_output_file=%CD%\t

if exist %CFG% goto add_device_id
@rem create cli_programmer.ini in current directory
"..\..\..\binaries\cli_programmer.exe" --save "%CFG%"

:add_device_id
@rem Put device sn in cli_programmer.ini file

if "%jlink_path%"=="" if "%device_sn%"=="" (
%windir%\system32\CScript /Nologo prepare_local_ini_file.vbs --cfg "%CFG%"
goto exec_cli
)

if "%jlink_path%"=="" (
%windir%\system32\CScript /Nologo prepare_local_ini_file.vbs --id %device_sn% --cfg "%CFG%"
goto exec_cli
)

if "%device_sn%"=="" (
%windir%\system32\CScript /Nologo prepare_local_ini_file.vbs --cfg "%CFG%" --jlink_path "%jlink_path%"
goto exec_cli
)

%windir%\system32\CScript /Nologo prepare_local_ini_file.vbs --id %device_sn% --cfg "%CFG%" --jlink_path "%jlink_path%"

:exec_cli

@echo on
"..\..\..\binaries\cli_programmer.exe" --cfg "%CFG%" gdbserver chip_erase_qspi

@echo %on_off%

if not "%TMPCFG%"=="" del %TMPCFG%

goto :Finished

:Finished
@echo.
@echo .......................................................................................................................
@echo ..
@echo .. FINISHED!
@echo ..
@echo .......................................................................................................................
