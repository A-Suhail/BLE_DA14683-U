#!/bin/bash

# parameters:
#   $1   = output path
#   $2.. = paths to look for nvparam config files

if [ $# -lt 2 ]; then
	echo "Usage: $0 <output path> <include path 1> [<include path N> ...]"
	exit 1
fi

if [ -x "${ARM_TOOLCHAIN}/bin/arm-none-eabi-gcc" ]; then
	CROSS="${ARM_TOOLCHAIN}/bin/arm-none-eabi-"
elif [ -x "${ARM_TOOLCHAIN}/arm-none-eabi-gcc" ]; then
	CROSS="${ARM_TOOLCHAIN}/arm-none-eabi-"
elif [ -x "$(which arm-none-eabi-gcc)" ]; then
	CROSS="$(dirname $(which arm-none-eabi-gcc))/arm-none-eabi-"
else
	echo "Cannot find arm-none-eabi-gcc, check you PATH or ARM_TOOLCHAIN settings!"
	exit 1
fi

DIR_OUT="$1"
DIR_NVPARAM="`dirname "$0"`"
NVPARAM_BIN="${DIR_OUT}/nvparam.bin"

include=()
while [ $# -gt 1 ]; do
	shift
	include+=("${1}")
done

# FIXME: need some better error messages

echo "Creating ${NVPARAM_BIN}"

"${CROSS}gcc" -c "${include[@]/#/-I}" -o "${DIR_OUT}/nvparam-symbols.o" "${DIR_NVPARAM}/symbols.c"
if [ $? -ne 0 ]; then
	echo "Failed to create nvparam-symbols.o"
	exit 1
fi

"${CROSS}gcc" -E -P -c "${include[@]/#/-I}" -o "${DIR_OUT}/nvparam-sections.ld" "${DIR_NVPARAM}/sections.ld.h"
if [ $? -ne 0 ]; then
	echo "Failed to create nvparam-sections.ld"
	exit 1
fi

"${CROSS}gcc" --specs=nano.specs --specs=nosys.specs -T "${DIR_OUT}/nvparam-sections.ld" -o "${DIR_OUT}/nvparam.elf" "${DIR_OUT}/nvparam-symbols.o"
if [ $? -ne 0 ]; then
	echo "Failed to create nvparam.elf"
	exit 1
fi

"${CROSS}objcopy" -O binary -j .nvparam "${DIR_OUT}/nvparam.elf" "${NVPARAM_BIN}"
if [ $? -ne 0 ]; then
	echo "Failed to create nvparam.bin"
	exit 1
fi

echo "Successfully created."

