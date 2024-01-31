#!/bin/bash

#
# Usage:
# reboot_device [serial_number]
# if serial number not given one device will be rebooted
#

base_dir="`dirname "$0"`"
JLINKCOMMANDER="JLinkExe"

DEVICE_ID=
JLINK_PATH=

if [ $# -ne 0 ] ; then
    while true; do
      case $1 in
        --jlink_path)
          JLINK_PATH="$2/"
          shift
          shift
          ;;
        [0-9]*)
          DEVICE_ID=$1
          shift
          ;;
        *)
          break
          ;;
      esac
    done
fi

if [ -z $JLINK_PATH ] ; then
    JLINKCOMMANDER=`which $JLINKCOMMANDER`
else
    JLINKCOMMANDER=${JLINK_PATH:+${JLINK_PATH}/}$JLINKCOMMANDER
fi

if [ ! -x $JLINKCOMMANDER ] ; then
    echo "$JLINKCOMMANDER not found. Make sure it is installed or correct path is provided as a parameter."
    exit 1
fi

if [ -z $DEVICE_ID ] ; then
  DEVICE_ID=`$JLINKCOMMANDER -CommandFile "${base_dir}/jlink_showemulist.script" | sed -n 's/^.*Serial number: \([0-9]*\),.*$/\1/p' | tail -n 1`
fi

if [ ! -z $DEVICE_ID ] ; then
  $JLINKCOMMANDER -if SWD -device Cortex-M0 -speed auto -SelectEmuBySN $DEVICE_ID -CommandFile "$base_dir/reboot.script"
fi
