target remote :2331
set pagination off
set logging file memory_snapshot.log
set logging on
i r
dump ihex memory memory_snapshot.ihex 0x7fc0000 0x7fe0000
set logging off
quit
