#!/bin/bash
grep "#define" ../../drv/include/ftdf.h | sed 's/#define //' | grep -v "FTDF_H_\|__private" | awk '{printf "%s = %s %s %s %s %s\n",$1,$2,$3,$4,$5,$6}' > ftdf.py
grep "#define" ../target/include/dts.h | sed 's/#define //' | grep -v "DTS_H_" | awk '{printf "%s = %s\n",$1,$2}' >> ftdf.py

