@SETLOCAL
@set on_off=OFF
@echo %on_off%
SETLOCAL ENABLEEXTENSIONS
SETLOCAL ENABLEDELAYEDEXPANSION
@rem store this script name for help
set thisfile=%~0
set this_folder=%~dp0

@rem parameters:
@rem   %1   = output path
@rem   %2.. = paths to look for nvparam config files

if "%~2" == "" (
  echo "Usage: %thisfile% <output path> <include path 1> [<include path N> ...]"
  exit /b 1
)

if not exist "%ARM_TOOLCHAIN%/bin/arm-none-eabi-gcc.exe" goto toolchain2
  set CROSS=%ARM_TOOLCHAIN%/bin/arm-none-eabi-
  goto toolchain_ok

:toolchain2
if not exist "%ARM_TOOLCHAIN%/arm-none-eabi-gcc.exe" goto toolchain3
  set CROSS=%ARM_TOOLCHAIN%/arm-none-eabi-
  goto toolchain_ok

:toolchain3
if not exist "arm-none-eabi-gcc.exe" goto toolchain_failed
  set CROSS=arm-none-eabi-
  goto toolchain_ok

:toolchain_failed
  call :error "Cannot find arm-none-eabi-gcc.exe, check you PATH or ARM_TOOLCHAIN settings!"
  exit /b 1

:toolchain_ok

set DIR_OUT=%~1
set DIR_NVPARAM=%this_folder%
set NVPARAM_BIN=%DIR_OUT%/nvparam.bin

set include=
:include_loop
if "%~2" == "" goto no_more_includes
set include=%include% -I"%~2"
shift
goto include_loop

:no_more_includes

@rem FIXME: need some better error messages

echo "Creating %NVPARAM_BIN%"

"%CROSS%gcc.exe" -c %include% -o "%DIR_OUT%/nvparam-symbols.o" "%DIR_NVPARAM%symbols.c"
if ERRORLEVEL 1 (
  call :error "Failed to create nvparam-symbols.o"
  exit /b 1
)

"%CROSS%gcc.exe" -E -P -c %include% -o "%DIR_OUT%/nvparam-sections.ld" "%DIR_NVPARAM%/sections.ld.h"
if ERRORLEVEL 1 (
  call :error "Failed to create nvparam-sections.ld"
  exit /b 1
)

"%CROSS%gcc.exe" --specs=nano.specs --specs=nosys.specs -T "%DIR_OUT%/nvparam-sections.ld" -o "%DIR_OUT%/nvparam.elf" "%DIR_OUT%/nvparam-symbols.o"
if ERRORLEVEL 1 (
  call :error "Failed to create nvparam.elf"
  exit /b 1
)

"%CROSS%objcopy.exe" -O binary -j .nvparam "%DIR_OUT%/nvparam.elf" "%NVPARAM_BIN%"
if ERRORLEVEL 1 (
  call :error "Failed to create nvparam.bin"
  exit /b 1
)

echo "Successfully created."

exit /b 0

:error
@echo Error: %~1
@goto:eof

