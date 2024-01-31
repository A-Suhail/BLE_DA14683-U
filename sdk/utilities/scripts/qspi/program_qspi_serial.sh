#!/bin/bash
base_dir="`dirname "$0"`"
sdkroot=${SDKROOT:=$(pushd "$base_dir/../../.." >/dev/null; pwd; popd >/dev/null)}
CONFIG_FILE="$base_dir/program_qspi.ini"
CONFIG_SCRIPT="$base_dir/program_qspi_config.sh"
CLI_PROGRAMMER="$sdkroot/binaries/cli_programmer"
IMAGE=$1

BAUD=57600
TX_PORT=
TX_PIN=
RX_PORT=
RX_PIN=
PRODUCT_ID=
ENABLE_UART=
RAM_SHUFFLING=

finish() {
echo .
echo .......................................................................................................................
echo ..
echo .. FINISHED!
echo ..
echo .......................................................................................................................
exit $1
}

# arg 1: the var to check
# arg 2: the max value allowed
check_number() {
        [ $1 -lt 0 -o $1 -gt $2 ] > /dev/null 2>&1 && return 1
        [ $? -ne 1 ] && return 1
        return 0
}

parse_pin() {
        read gpio
        if [ -z "$gpio" ] ; then
                echo "Default selected"
        else
                port=`echo $gpio | sed 's/[Pp]\([0-9]\)\([0-9]\)/\1 \2/' | cut -d' ' -f1`
                pin=`echo $gpio | sed 's/[Pp]\([0-9]\)\([0-9]\)/\1 \2/' | cut -d' ' -f2`

                check_number $port 9
                if [ $? -ne 0 ] ; then
                        echo ERROR: GPIO Port must be in [0, 9]
                        return 1
                fi
                check_number $pin 9
                if [ $? -ne 0 ] ; then
                        echo ERROR: GPIO Port must be in [0, 9]
                        return 1
                fi
                case $1 in
                1) TX_PORT=$port ; TX_PIN=$pin
                        ;;
                2) RX_PORT=$port ; RX_PIN=$pin
                        ;;
                esac
                return 0
        fi
}

echo .......................................................................................................................
echo ..
echo .. QSPI PROGRAMMING
echo ..
echo .......................................................................................................................
echo .

[ ! -f "$CONFIG_FILE" ] && ( "$CONFIG_SCRIPT" || exit 1 )
. "$CONFIG_FILE"

[ ! $# -eq 1 ] && echo "Usage $0 <image file to burn>" && exit 1

if [ ! -f "$1" ] ; then
        echo "$1 not found!"
        echo "Please select the folder which contains the binary you want to program and try again."
        finish 1
fi

if [ ! -x "$CLI_PROGRAMMER" ] ; then
        echo "cli_programmer not found. Please make sure it is built and installed in $(dirname "$CLI_PROGRAMMER")"
        finish 1
fi

while : ; do
        echo -n "Please enter GPIO to use for UART TX or enter for default > "

        parse_pin 1 && break
done

while : ; do
        echo -n "Please enter GPIO to use for UART RX or enter for default > "

        parse_pin 2 && break
done

while : ; do
        echo -n "Please enter BAUD rate to use (default: $BAUD) > "
        read BAUDRATE
        if [ -z "$BAUDRATE" ] ; then
                echo "Default selected"
                BAUDRATE=$BAUD
                break
        else
                check_number $BAUDRATE 115200 && break
        fi
done


while : ; do
        echo -n "Please enter your serial port ttyUSBX number (e.g. 0 for /dev/ttyUSB0) and press enter. (make sure your user is in the 'dialout' group) > "
        read TTYUSBNR
        check_number $TTYUSBNR 1000 && break
done

DEVNODE="/dev/ttyUSB$TTYUSBNR"
echo .

echo "Programming qspi cached image @ $DEVNODE"
if [ -z "$TX_PORT" ] ; then
        echo "  UART TX PORT: Default, TX PIN: Default"
else
        echo "  UART TX PORT: $TX_PORT, TX PIN: $TX_PIN"
        TX_PORT="--tx-port $TX_PORT"
        TX_PIN="--tx-pin $TX_PIN"
fi

if [ -z "$RX_PORT" ] ; then
        echo "  UART RX PORT: Default, RX PIN: Default"
else
        echo "  UART RX PORT: $RX_PORT, RX PIN: $RX_PIN"
        RX_PORT="--rx-port $RX_PORT"
        RX_PIN="--rx-pin $RX_PIN"
fi

if [ -n "$PRODUCT_ID" ] ; then
        PRODUCT_ID="--prod-id $PRODUCT_ID"
fi

if [ -n "$ENABLE_UART" ] ; then
        ENABLE_UART="--enable-uart $ENABLE_UART"
fi

if [ -n "$RAM_SHUFFLING" ] ; then
        RAM_SHUFFLING="--ram-shuffling $RAM_SHUFFLING"
fi

echo
#echo Programming qspi cached image...
echo "$CLI_PROGRAMMER $PRODUCT_ID $ENABLE_UART $RAM_SHUFFLING -i $BAUDRATE -s 1000000 $TX_PORT $TX_PIN $RX_PORT $RX_PIN $DEVNODE write_qspi_exec $IMAGE"
"$CLI_PROGRAMMER" ${PRODUCT_ID} ${ENABLE_UART} ${RAM_SHUFFLING} -i ${BAUDRATE} -s 1000000 ${TX_PORT} ${TX_PIN} ${RX_PORT} ${RX_PIN} ${DEVNODE} write_qspi_exec "$IMAGE"
[ $? -ne 0 ] && echo "ERROR PROGRAMMING FLASH" && finish 1

finish 0
