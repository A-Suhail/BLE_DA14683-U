#!/bin/bash

PORT=2331
DEVICE_ID=
CFG=cli_programmer.ini
JLINKLOG=jlink.log
TARGET_RESET_CMD=
JLINK_PATH=

while true; do
  case $1 in
    --cfg)
      CFG=$(readlink -f $2)
      shift
      shift
      ;;
    --id)
      DEVICE_ID=$2
      shift
      shift
      ;;
    --port)
      PORT=$2
      shift
      shift
      ;;
    --log)
      JLINKLOG=$2
      shift
      shift
      ;;
    --trc)
      TARGET_RESET_CMD=$2
      shift
      shift
      ;;
    --jlink_path)
      JLINK_PATH="$2/"
      shift
      shift
      ;;
    *)
      break
      ;;
  esac
done

cleanup() {
        [ ! -z "$TEMPJSCRIPT" ] && rm -f $TEMPJSCRIPT
}

select_device() {
        DEVICE_ARR=$1

        idx=1
        echo
        echo "Multiple JLink devices exist:"
        echo
        for devid in ${DEVICE_ARR[@]} ; do
                echo "$idx: $devid"
                idx=$(($idx+1))
        done

        which zenity >/dev/null
        if [ $? -eq 0 ]; then
                DEVICE_ID=$(zenity --separator=':' --list --column "Devices" --title="Select JLink Device" ${DEVICE_ARR[@]} | cut -d ':' -f1)
                return
        fi

        max=$(($idx-1))
        while : ; do
                echo
                echo -n "Choose one (1-$max): "
                read ans
                [ -z "$ans" ] && continue
                if echo $ans | egrep -q '^[0-9]+$'; then
                        if [ $ans -lt 1 -o $ans -gt $max ] ; then
                                echo "  * Choice out of range. Try again..."
                        else
                                ch=$(($ans-1))
                                DEVICE_ID=${DEVICE_ARR[$ch]}
                                return
                        fi
                else
                        echo "  * Choice must be a number. Try again..."
                fi
        done
}

get_device_id() {

        trap cleanup SIGINT SIGTERM

        TEMPJSCRIPT=`mktemp`
        echo showemulist >> $TEMPJSCRIPT
        echo exit >> $TEMPJSCRIPT
        idx=0
        declare -a DEVICE_ARR
        while read devid; do
                [ -z "$devid" ] && break
                DEVICE_ARR[$idx]=$devid
                idx=$(($idx+1))
        done << EOF
$($JLINKCOMMANDER -CommandFile $TEMPJSCRIPT | sed -n 's/^.*Serial number: \([0-9]*\),.*$/\1/p')
EOF
        case ${#DEVICE_ARR[@]} in
        0)
                echo "No JLink found. Connect a board with a JLink and retry. Aborting..."
                exit 1
                ;;
        1)
                DEVICE_ID=${DEVICE_ARR[0]}
                echo "Using device with id $DEVICE_ID"
                ;;
        *)
                select_device $DEVICE_ARR
                ;;
        esac

        # cleanup temp script file
        cleanup
}

# For compatibility with old syntax with just device id on command line
if [ -z $DEVICE_ID ] ; then DEVICE_ID=$1; fi

base_dir="`dirname "$0"`"
sdkroot=${SDKROOT:=$(pushd "$base_dir/../../.." >/dev/null; pwd; popd >/dev/null)}
QSCR=$sdkroot/utilities/scripts/qspi
CLI_PROGRAMMER=$sdkroot/binaries/cli_programmer
JLINKGDB=$JLINK_PATH"JLinkGDBServer"
JLINKCOMMANDER=$JLINK_PATH"JLinkExe"

if [ ! -x "$CLI_PROGRAMMER" ] ; then
        echo "cli_programmer not found. Please make sure it is built and installed in $(dirname "$CLI_PROGRAMMER")"
        exit 1
fi

if [ -z $DEVICE_ID ] ; then
        # get device id (from user, if more than two connected)
        get_device_id
fi

# If local ini file does not exits make cli_programmer do one
if [ ! -r "${CFG}" -o ! -s "${CFG}" ] ; then
        "$CLI_PROGRAMMER" --save "${CFG}" >/dev/null 2>&1
fi

# Set telnet and swo ports
SWOPORT=$((PORT + 1))
TELNETPORT=$((PORT + 2))

# Add device selection to ini file
awk <"${CFG}" >"${CFG}.new" -F= -v id=$DEVICE_ID -v gdb="$JLINKGDB" -v port=$PORT -v swoport=$SWOPORT -v telnetport=$TELNETPORT -v jlinklog=$JLINKLOG -v trc="$TARGET_RESET_CMD" '
   /^target_reset_cmd/ {
    if (length($0) < 20) {
      sub("=.*", "= " trc)
    }
    if (length(id) == 0 && length(trc) > 0) {
      sub("-selectemubysn [0-9]*", "")
    } else if (length(trc) > 0) {
      i = index($0, "-selectemubysn")
      if (i == 0) {
        sub("[ ]*$", " -selectemubysn " id)
      } else {
        sub("[ ]*-selectemubysn [0-9]*", " -selectemubysn " id)
      }
    }
   }
  /^port *=/ { print "port = " port; next }
  /^gdb_server_path/ {
    if (length($2) < 2) {
      sub("=.*", "= " gdb " -if swd -device Cortex-M0 -endian little -speed 4000 -singlerun -log " jlinklog)
    }
    if (length(id) == 0) {
      sub("-select usb=[0-9]*", "")
    } else {
      i = index($0, "-select usb=")
      if (i == 0) {
        sub("[ ]*$", " -select usb=" id)
      } else {
        sub("[ ]*-select usb=[0-9]*", " -select usb=" id)
      }
    }
    i = index($0, "-port ")
    if (i == 0) {
      sub("[ ]*$", " -port " port)
    } else {
      sub("[ ]*-port [0-9]*", " -port " port)
    }
    i = index($0, "-swoport ")
    if (i == 0) {
      sub("[ ]*$", " -swoport " swoport)
    } else {
      sub("[ ]*-swoport [0-9]*", "")
    }
    i = index($0, "-telnetport ")
    if (i == 0) {
      sub("[ ]*$", " -telnetport " telnetport)
    } else {
      sub("[ ]*-telnetport [0-9]*", "")
    }
    i = index($0, "-log ")
    if (i == 0) {
      sub("[ ]*$", " -log " jlinklog)
    } else {
      sub("[ ]*-log [^ ]*", " -log " jlinklog)
    }
  }
  { print }
'
mv "${CFG}.new" "${CFG}"

