#!/bin/bash

function print_help()
{
        echo "Usage:"
        echo "`basename $0` [-h] [--cfg config_path] [--id serial_number] <project output path>"
        echo "  where:"
        echo "    -h                  - prints this help"
        echo "    --cfg               - path to configuration file to be used"
        echo "    --id serial_number  - serial number of jlink to connect to"
        echo
        echo "    project output path - folder which contains the binary you want to program"
        exit 1
}

DEVICE_ID=
CFG=
while true; do
  case $1 in
    --cfg)
      CFG=$2
      ;;
    --id)
      DEVICE_ID=$2
      ;;
     -h)
      print_help
      ;;
    *)
      break
      ;;
  esac
  shift
  shift
done

base_dir="`dirname "$0"`"
SDK_ROOT=$base_dir/../../..
OUTPUT_ROOT=$1
PROJECT_ROOT=$OUTPUT_ROOT/..
NVPARAM_BIN=$OUTPUT_ROOT/nvparam.bin

CLI_PROGRAMMER="$SDK_ROOT/binaries/cli_programmer"
JLINKCOMMANDER="JLinkExe"
JLINKGDB="JLinkGDBServer"

TMPCFG=
TEMPJSCRIPT=
GDBPID=

cleanup() {
        echo "Cleaning up..."

        # cleanup temp script file
        [ ! -z "$TEMPJSCRIPT" ] && rm -f "$TEMPJSCRIPT"

        # cleanup temp config file
        [ ! -z "$TMPCFG" ] && rm -f "$TMPCFG"

        # kill gdb, if still alive
        grep $JLINKGDB /proc/$GDBPID/cmdline >/dev/null 2>&1
        if [ $? -eq 0 ] ; then
                kill $GDBPID
        fi
}

finish() {
cleanup
echo .
echo .......................................................................................................................
echo ..
echo .. FINISHED!
echo ..
echo .......................................................................................................................
exit $1
}

error() {
        which zenity >/dev/null
        if [ $? -eq 0 ]; then
                zenity --info --title "Programming QSPI Failed" --text "$1"
        else
                echo $1
        fi
}

interrupted() {
        echo "Interrupted..."
        finish 2
}

# print help and exit if path to binary not specified
[ ! $# -eq 1 ] && print_help

echo .......................................................................................................................
echo ..
echo .. NV-Parameters PROGRAMMING via JTAG
echo ..
echo .......................................................................................................................
echo .

if [ ! -d "$1" ] ; then
        echo "$1 not found!"
        error "Please select the folder which contains the binary you want to program and try again."
        finish 1
fi

if [ ! -x "$CLI_PROGRAMMER" ] ; then
        error "cli_programmer not found. Please make sure it is build (Release_static configuration) in sdk/utilities/cli_programmer/cli/Release_static"
        finish 1
fi

if [ ! -x `which $JLINKCOMMANDER` ] ; then
        error "$JLINKCOMMANDER not found. Make sure it is installed, and in the system's PATH"
        finish 1
fi

if [ ! -x `which $JLINKGDB` ] ; then
        error "$JLINKGDB not found. Make sure it is installed, and in the system's PATH"
        finish 1
fi

if [ ! -x "$(which arm-none-eabi-gcc)" ]; then
        while [[ ! -x "${ARM_TOOLCHAIN}/arm-none-eabi-gcc" && ! -x "${ARM_TOOLCHAIN}/bin/arm-none-eabi-gcc" ]]; do
                echo -n "Please enter GNU ARM Toolchain path > "
                read  ARM_TOOLCHAIN
        done
fi

"$SDK_ROOT/utilities/nvparam/create_nvparam.sh" "$OUTPUT_ROOT" "$PROJECT_ROOT/config" "$SDK_ROOT/sdk/bsp/adapters/include"
if [ $? -ne 0 ]; then
        error "Could not create nvparam.bin"
        exit 1
fi

trap interrupted SIGINT SIGTERM

if [ -z "${CFG}" ] ; then
        TMPCFG="${CFG:=`mktemp`}"

        "$base_dir/prepare_local_ini_file.sh" --cfg "${CFG}" ${DEVICE_ID:+--id ${DEVICE_ID}} ${JLINK_PATH:+--jlink_path ${JLINK_PATH}}
fi

echo "Programming flash of device $DEVICE_ID"
echo "$CLI_PROGRAMMER --cfg $CFG gdbserver write_qspi 0x80000 $NVPARAM_BIN"
"$CLI_PROGRAMMER" --cfg "${CFG}" gdbserver write_qspi 0x80000 "$NVPARAM_BIN"

[ $? -ne 0 ] && error "ERROR PROGRAMMING FLASH" && finish 1

finish 0
exit 0
