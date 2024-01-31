@echo OFF
SETLOCAL ENABLEDELAYEDEXPANSION
@echo .......................................................................................................................
@echo ..
@echo .. QSPI PROGRAMMING
@echo ..
@echo .......................................................................................................................
@echo.

if NOT exist %1 (
@echo %1 not found!
@echo Please select the folder which contains the binary you want to program and try again.
goto :Finished
)

set IMAGE=%~1
set PRODUCT_ID=DA14683-BA

if exist program_qspi_ini.cmd goto config_found
call program_qspi_config.bat

:config_found
call program_qspi_ini.cmd

@echo Please enter your COM port number and press enter.
@set /p comprtnr=-^> 
@echo.
@echo COMPORT=COM%comprtnr% 
@echo on
CALL "..\..\..\binaries\cli_programmer.exe" --prod-id %PRODUCT_ID% %RAM_SHUFFLING% COM%comprtnr% write_qspi_exec "%IMAGE%"
@echo off
goto :Finished

:Finished
@echo.
@echo .......................................................................................................................
@echo ..
@echo .. FINISHED!
@echo ..
@echo .......................................................................................................................
