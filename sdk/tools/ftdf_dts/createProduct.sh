#!/bin/bash

rm -fr product
mkdir -p product
mkdir -p product/log
cp -pr install/external product/
cp -pr config product/
cp -pr scripts product/

# Remove CVS dirs
dirs1=`find product/scripts/ -type d -name CVS`
dirs2=`find product/config/ -type d -name CVS`
dirs3=`find product/external/ -type d -name CVS`
dirs="$dirs1 $dirs2 $dirs3"

for dir in $dirs
do
    rm -fr $dir
done

# Get DTS and the DTS GUI
cp -p dialog.gif dialog.ico dts dts.py dtsparam.py ftdf.py gui.pyw scriptIncludes.py product/

chmod ug+rw -R product/
