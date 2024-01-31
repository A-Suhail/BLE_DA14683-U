#!/bin/bash

DEVICE_ID=
JLINK_PATH=
while true; do
  case $1 in
    --cfg)
      CFG=$2
      ;;
    --id)
      DEVICE_ID=$2
      ;;
    --jlink_path)
      JLINK_PATH="$2/"
      ;;
    *)
      break
      ;;
  esac
  shift
  shift
done

base_dir="`dirname "$0"`"
sdkroot=${SDKROOT:=$(pushd "$base_dir/../../.." >/dev/null; pwd; popd >/dev/null)}
CONFIG_FILE="$base_dir/program_qspi.ini"
CONFIG_SCRIPT="$base_dir/program_qspi_config.sh"
CLI_PROGRAMMER="$sdkroot/binaries/cli_programmer"
IMAGE=$1
JLINKCOMMANDER=$JLINK_PATH"JLinkExe"
JLINKGDB=$JLINK_PATH"JLinkGDBServer"


PRODUCT_ID=

TEMPJSCRIPT=
GDBPID=

cleanup() {
        [ -r "$TMPCFG" ] && rm "$TMPCFG"

        # kill gdb, if still alive
        grep "$JLINKGDB" /proc/$GDBPID/cmdline >/dev/null 2>&1
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
        echo "Interrupted...Cleaning up"
        finish 2
}


echo .......................................................................................................................
echo ..
echo .. QSPI PROGRAMMING via JTAG
echo ..
echo .......................................................................................................................
echo .

[ ! -f "$CONFIG_FILE" ] && ( "$CONFIG_SCRIPT" || exit 1 )
. "$CONFIG_FILE"

if [ $# -eq 1 ] ; then
        IMAGE=$1
else
        echo "Usage $0 [[--cfg config_file] | [[--id serial_number] [--jlink_path jlink_path]]] <image file to burn>"
        exit 1
fi

if [ ! -f "$IMAGE" ] ; then
        echo "$IMAGE not found!"
        error "Please select the folder which contains the binary you want to program and try again."
        finish 1
fi

if [ ! -x "$CLI_PROGRAMMER" ] ; then
        error "cli_programmer not found. Please make sure it is built and installed in $(dirname "$CLI_PROGRAMMER")"
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

trap interrupted SIGINT SIGTERM

if [ -z "${CFG}" ] ; then
        TMPCFG="${CFG:=`mktemp`}"

        "$base_dir/prepare_local_ini_file.sh" --cfg "${CFG}" ${DEVICE_ID:+--id ${DEVICE_ID}} ${JLINK_PATH:+--jlink_path ${JLINK_PATH}}
fi


if [ -n "$PRODUCT_ID" ] ; then
        PRODUCT_ID="--prod-id $PRODUCT_ID"
fi


echo "$CLI_PROGRAMMER --cfg $CFG $PRODUCT_ID gdbserver write_qspi_exec $IMAGE"
"$CLI_PROGRAMMER" --cfg "${CFG}" ${PRODUCT_ID} gdbserver write_qspi_exec "${IMAGE}"

[ $? -ne 0 ] && error "ERROR PROGRAMMING FLASH" && finish 1

finish 0
exit 0
