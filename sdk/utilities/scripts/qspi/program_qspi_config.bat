@echo OFF
SETLOCAL ENABLEDELAYEDEXPANSION
@echo .......................................................................................................................
@echo ..
@echo .. QSPI PROGRAMMING CONFIGURATION
@echo ..
@echo .......................................................................................................................
@echo.
set config_file=program_qspi_ini.cmd

if not exist %config_file% goto PRODUCT_ID_input
call %config_file%
if "%PRODUCT_ID%"=="" goto PRODUCT_ID_input
REM Dump existing configuration
@echo Existing configuration:
@echo ----------------------------
@echo PRODUCT_ID=%PRODUCT_ID%
@echo ----------------------------
@echo.
@echo.

REM Ask for changing existing configuration
set change_config=n
@echo Change existing configuration? ^(y/n or [ENTER] for n^) 
@set /p change_config=-^> 
@echo.
set result=false
if %change_config% == y set result=true
if %change_config% == Y set result=true
if %result% == false (
	goto Finished
)


REM User input for new configuration
:PRODUCT_ID_input
set PRODUCT_ID=1
@echo Product id options:  
@echo        0:  DA14680/1-01 
@echo        1:  DA14682/3-00, DA15XXX-00 (default)
@echo Product id ?  ^(0..1 or [ENTER] for 1^)
@set /p PRODUCT_ID=-^> 
@echo.
set result=false
if %PRODUCT_ID% GEQ 0 if %PRODUCT_ID% LEQ 1 set result=true
if %result% == false (
	echo "Invalid input" 
	goto PRODUCT_ID_input
)
if %PRODUCT_ID% == 0 set PRODUCT_ID=DA14681-01
if %PRODUCT_ID% == 1 set PRODUCT_ID=DA14683-00
@echo PRODUCT_ID=%PRODUCT_ID% 
@echo.

echo set PRODUCT_ID=%PRODUCT_ID% > program_qspi_ini.cmd

:Finished
@echo.
@echo .......................................................................................................................
@echo ..
@echo .. CONFIGURATION FINISHED!
@echo ..
@echo .......................................................................................................................

