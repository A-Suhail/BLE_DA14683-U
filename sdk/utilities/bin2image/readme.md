bin2image {#bin2image}
================================

## Overview
`bin2image` is a command line tool for creating images that can be executed from FLASH/OTP.
The tool modifies the input binary accordingly (e.g adds a header needed by the ROM booter for executing the image).

## Build instructions (Win/Linux)
Make sure that libprogrammer is imported in your workspace

### Windows
For a pure win32 executable, you can build with cygwin's mingw-gcc:
	make CC=i686-pc-mingw32-gcc
