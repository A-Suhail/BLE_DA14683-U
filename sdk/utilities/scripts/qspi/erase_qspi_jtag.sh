#!/bin/bash

DEVICE_ID=
JLINK_PATH=
while true; do
  case $1 in
    --cfg)
      CFG=$(readlink -f $2)
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
JLINKCOMMANDER=$JLINK_PATH"JLinkExe"
JLINKGDB=$JLINK_PATH"JLinkGDBServer"

TEMPJSCRIPT=
GDBPID=

cleanup() {
        # cleanup temp script file
        [ ! -z "$TEMPJSCRIPT" ] && echo "Cleaning up..." && rm -f $TEMPJSCRIPT

        [ -r "$TMPCFG" ] && rm "$TMPCFG"

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

msg() {
        which zenity >/dev/null
        if [ $? -eq 0 ]; then
                zenity --info --title "$2" --text "$1"
        else
                echo $1
        fi
}


error() {
        msg "$1" "Erasing QSPI Failed"
}

interrupted() {
        echo "Interrupted...Cleaning up"

        finish 2
}

ask_erase_ui() {
        which zenity >/dev/null
        if [ $? -eq 0 ]; then
                zenity --question --title "Erase QSPI memory" --text="Are you sure you want to erase QSPI ?" --ok-label "Erase" --cancel-label "Cancel"
                if [ $? -ne 0 ] ; then
                        exit 0
                fi
        else
                ask_erase_cli
        fi
}

ask_erase_cli() {
        echo -n "Are you sure you want to completely erase QSPI (y/N or [ENTER] for n)? "
        read ans
        case $ans in
        Y) return
                ;;
        y) return
                ;;
        *) echo Cancelled
                exit 0
        esac
}


echo .......................................................................................................................
echo ..
echo .. ERASE QSPI via JTAG
echo ..
echo .......................................................................................................................
echo .

[ ! -f "$CONFIG_FILE" ] && ( "$CONFIG_SCRIPT" || exit 1 )
. "$CONFIG_FILE"

if [ ! -x "$CLI_PROGRAMMER" ] ; then
        error "cli_programmer not found. Please make sure it is built and installed in $(dirname "$CLI_PROGRAMMER")"
        finish 1
fi

if [ ! `which $JLINKCOMMANDER` ] ; then
        error "$JLINKCOMMANDER not found. Make sure it is installed, and in the system's PATH"
        finish 1
fi

if [ ! `which $JLINKGDB` ] ; then
        error "$JLINKGDB not found. Make sure it is installed, and in the system's PATH"
        finish 1
fi

trap interrupted SIGINT SIGTERM

ask_erase_ui

echo "Erasing flash of device $DEVICE_ID"

if [ -z "${CFG}" ] ; then
        TMPCFG="${CFG:=`mktemp`}"

        "$base_dir/prepare_local_ini_file.sh" --cfg "$CFG" ${DEVICE_ID:+--id ${DEVICE_ID}} ${JLINK_PATH:+--jlink_path ${JLINK_PATH}}
fi

echo "$CLI_PROGRAMMER --cfg $CFG gdbserver chip_erase_qspi"
"$CLI_PROGRAMMER" --cfg "$CFG" gdbserver chip_erase_qspi

[ $? -ne 0 ] && error "ERROR ERASING QSPI FLASH" && finish 1

msg "Successfully erased QSPI" "Erase QSPI"
finish 0
exit 0
