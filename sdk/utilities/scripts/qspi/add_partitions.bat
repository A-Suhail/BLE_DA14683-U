@echo OFF
SETLOCAL ENABLEDELAYEDEXPANSION
@echo .......................................................................................................................
@echo ..
@echo .. Writing partition table
@echo ..
@echo .......................................................................................................................
@echo.
set UARTBOOT=..\..\..\sdk\bsp\system\loaders\uartboot\Release\uartboot.bin
if NOT exist %UARTBOOT% (
@echo uartboot.bin not found!
@echo Please build uartboot project ^(RELEASE configuration^) and try again.
goto :Finished
)

set IMAGE=partition_table.bin
@echo Please enter your COM port number and press enter.
@set /p comprtnr=-^> 
@echo.
@echo COMPORT=COM%comprtnr% 
CALL "..\..\..\binaries\cli_programmer.exe" -b %UARTBOOT% COM%comprtnr% write_qspi 0x7F000 %IMAGE%
goto :Finished

:Finished
@echo.
@echo .......................................................................................................................
@echo ..
@echo .. FINISHED!
@echo ..
@echo .......................................................................................................................
