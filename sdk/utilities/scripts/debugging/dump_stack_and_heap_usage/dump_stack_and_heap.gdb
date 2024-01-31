#
# arm-none-eabi-gdb --silent --command=dump_stack_and_heap.gdb -s <elf file>
#
# Projects need to be compiled with dg_configTRACK_OS_HEAP set to 1
#

target remote localhost:2331
set $i = 0
set $sum = 0
printf "******************************\n"
printf "* Process  HiMark (in Bytes) *\n"
printf "******************************\n"
while pxTaskStatusArray[$i].pcTaskName != 0
  printf "%9s   %5d   %5d\n", pxTaskStatusArray[$i].pcTaskName, pxTaskStatusArray[$i].usStackHighWaterMark, pxTaskStatusArray[$i].usStackHighWaterMark * 4
  set $sum = $sum + pxTaskStatusArray[$i].usStackHighWaterMark
  set $i = $i + 1
end
printf "******************************\n"
printf "* Total     %5d   %5d    *\n", $sum, $sum * 4
printf "******************************\n"
printf "\n"
printf "Lowest free heap %d\n", xMinimumEverFreeBytesRemaining
printf "\n"
disconnect
quit
