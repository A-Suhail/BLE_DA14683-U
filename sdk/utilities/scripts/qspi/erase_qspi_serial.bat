@echo OFF
SETLOCAL ENABLEDELAYEDEXPANSION
@echo .......................................................................................................................
@echo ..
@echo .. ERASE QSPI
@echo ..
@echo .......................................................................................................................
@echo.

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


@echo Please enter your COM port number and press enter.
@set /p comprtnr=-^> 
@echo.
@echo COMPORT=COM%comprtnr% 
@echo on
CALL "..\..\..\binaries\cli_programmer.exe" COM%comprtnr% chip_erase_qspi
@echo off
goto :Finished

:Finished
@echo.
@echo .......................................................................................................................
@echo ..
@echo .. FINISHED!
@echo ..
@echo .......................................................................................................................
