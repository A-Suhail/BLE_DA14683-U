@SETLOCAL
@set on_off=OFF
@echo %on_off%
SETLOCAL ENABLEDELAYEDEXPANSION
@echo .......................................................................................................................
@echo ..
@echo .. QSPI PROGRAMMING
@echo ..
@echo .......................................................................................................................
@echo.

set TMPCFG=
set jlink=

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

if not defined %jlink goto no_jlink_path

REM Remove trailing slash if any
IF %jlink:~-2,-1%==/ SET jlink=%jlink:~0,-2%"

REM Transform slashes to backslashes
set jlink=%jlink:/=\%
@echo JlinkGDBServer path used: %jlink%

@REM Remove quotes if any
for /F "tokens=*" %%i in (%jlink%) do set jlink_path=%%~i
:no_jlink_path

if NOT exist %1 (
@echo %1 not found!
@echo Please select the folder which contains the binary you want to program and try again.
goto :Finished
)

set IMAGE=%~1

if exist program_qspi_ini.cmd goto config_found
call program_qspi_config.bat

:config_found
call program_qspi_ini.cmd

if not "%PRODUCT_ID%"=="" set PRODUCT_ID=--prod-id %PRODUCT_ID%

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
"..\..\..\binaries\cli_programmer.exe" --cfg "%CFG%" %PRODUCT_ID% gdbserver write_qspi_exec "%IMAGE%"

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
