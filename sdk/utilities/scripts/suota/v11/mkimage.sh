#!/bin/bash

[ "${OSTYPE}" == "cygwin" ] && exe_ext=".exe"

version_file=sw_version.h

function msg()
{
  if [ -z $quiet ] ; then
    echo $*
  fi
}

function help()
{
  echo "Usage:"
  echo "$0 [-h] [-q] bin_file [image_file]"
  echo "   where:"
  echo "     -h - prints this help"
  echo "     -q - reduce number of prints"
  echo
  echo "     bin_file - file with application binary"
  echo "     image_file - output image file for SUOTA"
  echo ""
  echo "Run this script from folder containing sw_wersion.h file"
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
    -h | --help)
      help
      exit 0
      ;;
    *)
      break
      ;;
  esac
done

base_dir="`dirname "$0"`"
sdkroot=${SDKROOT:=$(pushd "$base_dir/../../../.." >/dev/null; pwd; popd >/dev/null)}

msg Using SDK from $sdkroot

MKIMAGEPATH=${sdkroot}/utilities/mkimage

mkimage=${sdkroot}/binaries/mkimage${exe_ext}

if ! [ -x "$mkimage" ] ; then
  echo mkimage not found, please build it
  exit 1
fi

bin_file=$1
if [ -z "$bin_file" ] ; then
  echo No binary file specified
  exit 2
fi
shift

if [ ! -r "$bin_file" ] ; then
  echo Binary file $1 does not exist
  exit 2
fi

if [ ! -z "$1" ] ; then
  image_file=$1
  shift
fi

# read version from version.h
if [ -e $version_file ] ; then
  read v1 v2 v3 build <<< `awk -F\" <sw_version.h '/BLACKORCA_SW_VERSION / {gsub("[.]"," "); print $2}'`
  if [ -z "$build" ] ; then
    mv $version_file sw_version.err;
    echo $version_file file does not contain version info, creating new
    v1=1
    v2=0
    v3=0
    build=1
  fi
else
  v1=1
  v2=0
  v3=0
  build=1
  msg Creating new $version_file file
fi

version_string=$v1.$v2.$v3.$build

# create version file if not exists
if [ ! -e $version_file ] ; then
  date=`date "+%G-%m-%d %H:%M"`
  cat >$version_file <<EOF
#define BLACKORCA_SW_VERSION "$version_string"
#define BLACKORCA_SW_VERSION_DATE "$date "
#define BLACKORCA_SW_VERSION_STATUS "REPOSITORY VERSION"
EOF
fi

if [ -z $image_file ] ; then
  image_file=${bin_file/.bin/.${version_string}.img}
  msg No image file specified creating ${image_file}
fi


# Run image creating tool
"$mkimage" single "$bin_file" "$version_file" "$image_file"

