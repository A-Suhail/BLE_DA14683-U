@echo Execute JLinkGDBServer.exe
START /b "Jlink boot qspi dbg" CALL "JLinkGDBServerCL.exe" -port 2331 -if SWD -singlerun
START /b "arm-none-eabi-gdb" CMD /c arm-none-eabi-gdb -s=PUT_YOUR_APP_ELF_HERE.elf --command=gdb_cmd_qspi_dbg




