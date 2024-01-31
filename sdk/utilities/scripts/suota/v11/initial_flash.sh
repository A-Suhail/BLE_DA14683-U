#!/bin/bash

base_dir="`dirname "$0"`"
CONFIG_FILE="$base_dir/../../qspi/program_qspi.ini"
CONFIG_SCRIPT_PATH="$base_dir/../../qspi/"
CONFIG_SCRIPT="./program_qspi_config.sh"
JLINK_PATH=

function msg()
{
        if [ -z $quiet ] ; then
            echo $*
        fi
}

function title()
{
        if [ -z $quiet ] ; then
            echo .......................................................................................................................
            echo ..
            echo .. $*
            echo ..
            echo .......................................................................................................................
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

function help()
{
        echo "Usage:"
        echo "$0 [-h] [-q] [[--nobootloader] | [-b bootloader]] [[--cfg config_path] | [[--id serial_number] [--jlink_path jlink_path]]] <app_binary>"
        echo "   where:"
        echo "     -h - prints this help"
        echo "     --nobootloader - do not flash bootloader"
        echo "     -q - reduce number of prints"
        echo "     --cfg - configuration file"
        echo "     -b or --bootloader - bloot_loader_bin - path to bootloader, if not specified default will be used"
        echo "     --id serial_number - serial number of jlink to connect to"
        echo "     --jlink_path - path to JLink, if not specified default will be used"
        echo
        echo "     app_binary - path to binary to flash"
}

function cleanup() {
        # cleanup temp script file
        [ -r "$TMPCFG" ] && echo "Remove temporary gdbserver config file" && rm "$TMPCFG"
}

function interrupted() {
        echo "Interrupted...Cleaning up"
        finish 2
}

while true; do
  case $1 in
    [-/]v)
      verbose=1
      shift
      ;;
    [-/]q)
      quiet=1
      shift
      ;;
    --nobootloader)
      nobootloader=1
      shift
      ;;
    --id)
      DEVICE_ID=$2
      shift
      shift
      ;;
    --cfg)
      CFG=$(readlink -f $2)
      shift
      shift
      ;;
    -b | --bootloader)
      boot_loader_bin=$(readlink -f $2)
      shift
      shift
      ;;
    --jlink_path)
      JLINK_PATH="$2/"
      shift
      shift
      ;;
    -h | --help)
      help
      exit 0
      ;;
    *)
      break
      ;;
  esac
done

sdkroot=${SDKROOT:=$(pushd "$base_dir/../../../.." >/dev/null; pwd; popd >/dev/null)}

SUOTA_LOADER_PATH="$sdkroot/sdk/bsp/system/loaders/ble_suota_loader"

CLI="$sdkroot/binaries/cli_programmer"
QSCR="$sdkroot/utilities/scripts/qspi"

if [ ! -f "$CONFIG_FILE" ] ; then
        CWD=`pwd`
        cd "$CONFIG_SCRIPT_PATH"
        "$CONFIG_SCRIPT"
        cd "$CWD"
fi

eval $(cat "$CONFIG_FILE")


if [ x"$PRODUCT_ID" == x"DA14680-01" -o x"$PRODUCT_ID" == x"DA14681-01" ] ; then
        SUOTA_BUILD_CONFIG="DA14681-01-Release_QSPI"
else
        SUOTA_BUILD_CONFIG="DA14683-00-Release_QSPI"
fi


msg Using SDK from $sdkroot
msg cli_programmer from $CLI

if [ -z "$1" ] ; then
        echo No binary file specified
        exit 2
fi

if [ ! -r "$1" ] ; then
        echo Binary file $1 does not exist
        exit 2
fi
bin_file=$(readlink -f "$1")

if [ -z "$boot_loader_bin" ] ; then
        boot_loader_bin="$SUOTA_LOADER_PATH/$SUOTA_BUILD_CONFIG/ble_suota_loader.bin"
fi

image_file=application_image.img
msg image file "$bin_file"
msg boot loader "$boot_loader_bin"
msg Preparing image file "$image_file"
"$sdkroot/utilities/scripts/suota/v11/mkimage.sh" "$bin_file" "$image_file" || exit 2

trap interrupted SIGINT SIGTERM

if [ -z "${CFG}" ] ; then
        TMPCFG="${CFG:=`mktemp`}"

        "$sdkroot/utilities/scripts/qspi/prepare_local_ini_file.sh" --cfg "${CFG}" ${DEVICE_ID:+--id ${DEVICE_ID}} ${JLINK_PATH:+--jlink_path ${JLINK_PATH}} || exit 2
fi

if [ -z $nobootloader ] ; then
        # Erase bootloader and partition table
        title "Erasing bootloader area"
        "$CLI" ${CFG:+--cfg ${CFG}} gdbserver erase_qspi 0 4096
fi
title "Erasing partition table"
"$CLI" ${CFG:+--cfg ${CFG}} gdbserver erase_qspi 0x7F000 4096

# Flash application image to update partition. It will be moved to image partition by bootloader
title "Writing application image $bin_file"
"$CLI" ${CFG:+--cfg ${CFG}} gdbserver write_qspi 0x20000 "$bin_file"
title "Writing image header $image_file"
"$CLI" ${CFG:+--cfg ${CFG}} gdbserver write_qspi 0x1F000 "$image_file" 36
rm "$image_file" 2>/dev/null

if [ -z $nobootloader ] ; then
        # Flash bootloader
        title "Writing bootloader"
        pushd "$QSCR"
        ./program_qspi_jtag.sh ${CFG:+--cfg ${CFG}} ${DEVICE_ID:+--id ${DEVICE_ID}} ${JLINK_PATH:+--jlink_path ${JLINK_PATH}} "$boot_loader_bin" || exit 2
        popd
fi

cleanup

"$sdkroot/utilities/scripts/qspi/reboot_device.sh" ${JLINK_PATH:+--jlink_path ${JLINK_PATH}} ${DEVICE_ID}

