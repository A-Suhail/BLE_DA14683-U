General installation and debugging procedure {#install_and_debug_procedure}
===================================================

This guide presents the steps which should be followed in order to execute, flash and debug 
SDK projects.

## Importing a project

-# In `SmartSnippets Studio` select `File>Import` and then `General>Existing projects into Workspace`

-# Navigate to `\projects\dk_apps\` folder and select a project to import 

## Building for RAM
Build project using a *RAM build configuration (e.g DA14681-01-Release_RAM)


## FLASH programming
-# Import `scripts` project. A set of scripts will become visible under `External tools` 
  drop down list (this step need only be done once)
  
-# Select the chip revision and flash options by running `program_qspi_config_win` (Windows) or 
   `program_qspi_config_linux` (Linux) script from `External tools` drop down list
   (this step need only be done once)
     
-# Build the project using one of the flash build configurations (named *QSPI).
  \note Make sure that the build configuration matches chip revision 
  e.g DA14681-01-Release_QSPI or DA14681-00-Release_QSPI   

-# Select the project to be flashed by clicking on any folder of the project

-# Connect board (USB2 connector) to a PC using a USB cable.

-# Flash the image to qspi over serial port or jtag using the appropriate script from the `External tools`
   drop down list:
   - Flash over serial port: `program_qspi_serial_win`(Windows) or `program_qspi_serial_linux`(Linux)
   (the scripts prompt for the PC serial port where the board is attached)
   - Flash over jtag: `program_qspi_jtag_win`(Windows) or `program_qspi_jtag_linux`(Linux)

## Run and Debug a project
-# Connect board (USB2 connector) to a PC using a USB cable.
-# Click <b> `'Debug As...'` </b> drop-down list and select:

 - RAM - to launch and debug the project from RAM
 - QSPI - to launch and debug the project from QSPI
 - ATTACH - to attach to the currently running project

\note The launchers are visible only when the corresponding build configuration of the active project 
is available.

## Debug Logs

Open a serial terminal and connect to a proper serial port (e.g /dev/ttyUSB0 for Linux or COMx for
Windows environment), baudrate: 115200. It will be needed for printing debug logs for the user.

## Flashing tools

The flashing tools comprise the following projects:
 - `cli_programmer`: a command line application for issuing programming commands
 
 - `libprogrammer`: the (host-side) library which implements the programming functionality
 
 - `uartboot`: the (secondary) boot loader running on the target which executes libprogrammer
    commands       

 - `bin2image`: an application which prepends to the binary the appropriate header needed for the 
    rom boot loader to identify the execution mode (qspi cached, mirrored, etc)
 
 -  `scripts`: a collection of scripts which utilize flashing tools and implement `external tools` 
    functionality

The flashing tools have the following dependencies:
 - `cli_programmer` depends on `libprogrammer`
 - `bin2image` depends on `libprogrammer`

In order to re-build flashing tools used by the `external tools`, user has to import flashing tools 
projects and build them using the appropriate build configurations: 
### Linux
 - Build `bin2image` in \b `Release` mode.

 - Build `cli_programmer` in \b `Release_static` mode.

### Windows
 - Build `bin2image` in \b `Release_win32` mode.

 - Build `cli_programmer` in \b `Release_static_win32` mode.
