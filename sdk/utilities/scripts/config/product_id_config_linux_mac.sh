#!/bin/sh
base_dir="`dirname "$0"`"
CONFIG_FILE="$base_dir/../qspi/program_qspi.ini"

if [ "${1}" = "DA14680-01" ] || [ "${1}" = "DA14681-01" ]
then
		echo "export PRODUCT_ID=\"DA14681-01\"" > "$CONFIG_FILE"
else
		echo "export PRODUCT_ID=\"DA14683-00\"" > "$CONFIG_FILE"
fi
