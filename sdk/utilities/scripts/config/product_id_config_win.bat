@echo off
set PRODUCT_ID=DA14683-00
if %1 == DA14680-01 set PRODUCT_ID=DA14681-01
if %1 == DA14681-01 set PRODUCT_ID=DA14681-01

echo set PRODUCT_ID=%PRODUCT_ID% > ..\qspi\program_qspi_ini.cmd