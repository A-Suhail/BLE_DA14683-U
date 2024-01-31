#!/bin/bash

version="0.1"
JLinkGDBServer -port 2331 -if SWD -singlerun &
arm-none-eabi-gdb -s=PUT_YOUR_APP_ELF_HERE.elf --command=gdb_cmd_qspi_attach
