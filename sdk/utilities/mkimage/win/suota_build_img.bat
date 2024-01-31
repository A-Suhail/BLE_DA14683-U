@echo off

set version_file=../sw_version.h

echo.
echo Welcome to Dialog suota image builder
echo.

if "%1"=="" goto usage_info
if "%2"=="" goto usage_info
if not exist %version_file% goto missig_version
if not exist %1 goto missing_file_1
if not exist %2 goto missing_file_2

for %%I in (%1) do (set file1=%%~nI)
for %%I in (%2) do (set file2=%%~nI)

echo.
echo Files used in build:
echo %file1%.bin
echo %file2%.bin
echo.

echo Build image:
mkimage.exe single %file1%.bin %version_file% %file1%.img
mkimage.exe single %file2%.bin %version_file% %file2%.img

for /F "usebackq tokens=1,2 delims==" %%i in (`wmic os get LocalDateTime /VALUE 2^>NUL`) do if '.%%i.'=='.LocalDateTime.' set ldt=%%j
set timestamp=%ldt:~8,2%_%ldt:~10,2%_%ldt:~12,2%_%ldt:~0,4%_%ldt:~4,2%_%ldt:~6,2%

for %%I in (%file1%.img) do (set img_size=%%~zI)
echo Image size: %img_size%
set /a offset=(%img_size% / 64 + 1) * 64 + 0x1040

call:to_hex %offset% hex_offset

echo Offset: 0x%hex_offset%
echo.

mkimage.exe multi spi %file1%.img 0x1000 %file2%.img 0x%hex_offset% 0x00000 suota.bin
mkimage.exe single suota.bin %version_file% suota_image_%timestamp%.img

del suota.bin
del %file1%.img
del %file2%.img

echo.
echo Suota image created

goto end

:usage_info
	echo usage suota_build_img.bat ^<file1^> ^<file2^>
	goto end
	
:missig_version
	echo The sw_version.h file is missing
	goto end
	
:to_hex dec hex
	SETLOCAL ENABLEDELAYEDEXPANSION
	set /a dec=%~1
	set "hex="
	set "map=0123456789ABCDEF"
	for /L %%N in (1,1,8) do (
		set /a "d=dec&15,dec>>=4"
		for %%D in (!d!) do set "hex=!map:~%%D,1!!hex!"
	)
	
	for /f "tokens=* delims=0" %%A in ("%hex%") do set "hex=%%A"&if not defined hex set "hex=0"
	( ENDLOCAL & REM RETURN VALUES
		IF "%~2" NEQ "" (SET %~2=%hex%) ELSE ECHO.%hex%
	)
	EXIT /b
	
:missing_file_1
	echo Error: File %1 does not exist.
	goto end
	
:missing_file_2
	echo Error: File %2 does not exist.
	goto end
	
:end
