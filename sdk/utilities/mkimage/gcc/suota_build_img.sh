#!/bin/bash

echo
echo
echo "Welcome to Dialog suota image builder!"
echo
echo

if [[ $# -lt 1 ]]; then
	echo "usage suota_build_img.sh <file1> <file2>"
	echo
fi


if [ -f "../sw_version.h" ]; then
	echo "sw_version.h: OK"
else
	echo "sw_version.h: NOK"
	exit 1
fi

shift $(($OPTIND-1))

f1=$1
f1_b=`basename $f1`

f2=$2
f2_b=`basename $f2`

file_1=${f1_b%.bin}
file_2=${f2_b%.bin}

echo
echo "files used in build:"
echo
echo "$file_1, $file_2"
echo

timestamp=`date +%d%m%y%H%M`

image=suota_image_$timestamp.img

echo "build image"
./mkimage single $file_1.bin ../sw_version.h $file_1.img
./mkimage single $file_2.bin ../sw_version.h $file_2.img

#image_size=`stat --printf=%s $file_1.img`
image_size=`du -b $file_1.img | cut -f1`
# Calculate offest for the second image.
# This offset must be aligned to 64.
# 0x1040 is size of the image and product header.
let image_size=($image_size/64+1)*64+0x1040
printf -v offset "0x%x" "$image_size"
#echo "top($image_size.0/64.0)" | bc
echo "Image size: $image_size"

./mkimage multi spi $file_1.img 0x1000 $file_2.img $offset 0x00000 suota.bin
./mkimage single suota.bin ../sw_version.h $image


#Remove some binaries we create during the process
rm $file_1.img 2>/dev/null
rm $file_2.img 2>/dev/null
rm suota.bin 2>/dev/null

echo
echo
if [ -f $image ]; then
	echo "Multi image done: $image"
else
	echo "Multi image NOT created"
	exit 1
fi
echo
echo
