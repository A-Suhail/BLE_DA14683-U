#!/usr/bin/env python

#########################################################################################
# Copyright (C) 2016. Dialog Semiconductor, unpublished work. This computer
# program includes Confidential, Proprietary Information and is a Trade Secret of
# Dialog Semiconductor.  All use, disclosure, and/or reproduction is prohibited
# unless authorized in writing. All Rights Reserved.
#########################################################################################


import gdb
import re

class IgnoreErrorsCommand (gdb.Command):

        def __init__ (self):
                super (IgnoreErrorsCommand, self).__init__ ("ignore-errors",
                                                            gdb.COMMAND_OBSCURE,
                                                            # FIXME...
                                                            gdb.COMPLETE_COMMAND)
        def invoke (self, arg, from_tty):
                try:
                        gdb.execute (arg, from_tty)
                except:
                        pass
IgnoreErrorsCommand()

class IterateFreeRtosListCommand(gdb.Command):

        MAX_ITER = 40

        def __init__(self):
                super(IterateFreeRtosListCommand, self).__init__("iterate-freertos-list",
                                                                 gdb.COMMAND_DATA,
                                                                 gdb.COMPLETE_SYMBOL)

        def regs_stack_to_index(self, regname):
                regs_dict = {'xpcr':15,
                             'pc':14,
                             'lr':13,
                             'r12':12,
                             'r3':11,
                             'r2':10,
                             'r1':9,
                             'r0':8, # start of HW stacking see section 2.3.6 From ARM0 user guide
                             'r11':7,
                             'r10':6,
                             'r9':5,
                             'r8':4,
                             'r7':3,
                             'r6':2,
                             'r5':1,
                             'r4':0  # start of SW stacking see xPortPendSVHandler() implementation of FreeRTOS
                             }

                return regs_dict[regname]

        def invoke(self, argument, from_tty):
                args = gdb.string_to_argv(argument)
                expr = args[0]
                List_t = gdb.parse_and_eval(expr)
                #print List_t
                TCB_t_p = gdb.lookup_type("TCB_t").pointer() #TCB_t *
                uint32_p = gdb.lookup_type("uint32_t").pointer() #uint32_t *

                if len(args) == 2:
                        max_iter = int(args[1])
                else:
                        max_iter = self.MAX_ITER

                pxCurrentTCB = gdb.parse_and_eval("pxCurrentTCB")


                uxNumberOfItems = List_t["uxNumberOfItems"]

                #this is the our sentinel to iterate the list (marker called in FreeRTOS)
                xListEnd = List_t["xListEnd"]

                item = xListEnd["pxNext"]
                #print xListEnd.address
                #print xListEnd["pxNext"]

                i = 1

                # print "pxCurrentTCB %s" % (pxCurrentTCB.dereference())
                while xListEnd.address != item:
                        print "node@%s: %s #%d" % (item, item.dereference(), i)

                        if (uxNumberOfItems == 0):
                                print "List corruption: Iterated  %d times uxNumberOfItems %d" % (i, uxNumberOfItems)
                                break

                        if (i == max_iter):
                                print "Max iterations %d reached % (i)"
                                break

                        #print the owner of the list casted as TCB_t
                        tcb = item["pvOwner"].cast(TCB_t_p).dereference()
                        pxTopOfStack = tcb["pxTopOfStack"]
                        pc = int((pxTopOfStack + self.regs_stack_to_index('pc')).cast(uint32_p).dereference())
                        lr = int((pxTopOfStack + self.regs_stack_to_index('lr')).cast(uint32_p).dereference())
                        print "pvOwner@%s: %s" % (item["pvOwner"], tcb)
                        print "PC @ 0x%x ---> %s" % (pc, gdb.find_pc_line(pc))
                        print "LR @ 0x%x ---> %s" % (lr, gdb.find_pc_line(lr))
                        print "--------------------------------------------------------------------"
                        uxNumberOfItems -= 1
                        item = item["pxNext"]
                        i += 1

                #at this point the list has been iterated so there must be 0 items left
                if (uxNumberOfItems):
                        print "List corruption: Iterated  %d times uxNumberOfItems %d" % (i, uxNumberOfItems)

IterateFreeRtosListCommand()


class IterateFreeRtosHeapCommand(gdb.Command):

        def __init__(self):
                super(IterateFreeRtosHeapCommand, self).__init__("iterate-freertos-heap",
                                                                 gdb.COMMAND_DATA,
                                                                 gdb.COMPLETE_SYMBOL)
        def free_memblocks(self):
                xStart = gdb.parse_and_eval("xStart") #start of free block list

                pxNextFreeBlock = xStart["pxNextFreeBlock"]

                found = False
                while pxNextFreeBlock != 0:
                        print "pxNextFreeBlock@%s %s" % (pxNextFreeBlock, pxNextFreeBlock.dereference())
                        pxNextFreeBlock = pxNextFreeBlock["pxNextFreeBlock"]

        def print_memblock(self, memblock, b_size):
                #TODO merge it in one print
                print "memblock@%s size %s {" % (memblock.address, b_size)
                print "  pxNextFreeBlock = %s," % memblock["pxNextFreeBlock"]
                print "  xBlockSize = 0x%x" % int(memblock["xBlockSize"])
                print "}"

        def invoke(self, argument, from_tty):
                args = gdb.string_to_argv(argument)
                expr = args[0]
                ucHeap =  gdb.parse_and_eval(expr)
                xBlockAllocatedBit = gdb.parse_and_eval("xBlockAllocatedBit")
                BlockLink_t = gdb.lookup_type("BlockLink_t") #BlockLink_t

                used_heap = 0

                #allocated blocks should be found in a aligned location
                for b in range(0, ucHeap.type.sizeof, 4):
                        memblock = ucHeap[b].cast(BlockLink_t)
                        # self.free_memblocks()
                        is_alloc = bool(int(memblock["xBlockSize"]) & int(xBlockAllocatedBit))
                        is_alloc = is_alloc and bool(memblock["pxNextFreeBlock"] == 0x0)

                        if (is_alloc):
                                b_size =  int(memblock["xBlockSize"]) & ~int(xBlockAllocatedBit)
                                #does the block size look sane
                                # if (b * 4 + b_size < ucHeap.type.sizeof):
                                if (b_size < ucHeap.type.sizeof):
                                        used_heap = used_heap + b_size
                                        self.print_memblock(memblock, b_size)
                #TODO stats
                #print "used heap %d" % (used_heap)



IterateFreeRtosHeapCommand()

class PrintFreeRtosTaskStatusCommand(gdb.Command):

        def __init__(self):
                super(PrintFreeRtosTaskStatusCommand, self).__init__("print-freertos-task-status",
                                                                     gdb.COMMAND_DATA,
                                                                     gdb.COMPLETE_SYMBOL)
        def invoke(self, argument, from_tty):
                pxTaskStatusArray = gdb.parse_and_eval("pxTaskStatusArray")

                i = 0
                sum = 0
                print "Name   xTaskNumber    xHandle    eCurrentState  uxCurrentPriority uxBasePriority ulRunTimeCounter usStackHighWaterMark(words)  usStackHighWaterMark(bytes)\n"
                while pxTaskStatusArray[i]["pcTaskName"] != 0:
                        xHandle = pxTaskStatusArray[i]["xHandle"]
                        pcTaskName = str(pxTaskStatusArray[i]["pcTaskName"])
                        name = re.findall("(\".*\")", pcTaskName)
                        xTaskNumber = pxTaskStatusArray[i]["xTaskNumber"]
                        eCurrentState = pxTaskStatusArray[i]["eCurrentState"]
                        uxCurrentPriority = pxTaskStatusArray[i]["uxCurrentPriority"]
                        uxBasePriority =  pxTaskStatusArray[i]["uxBasePriority"]
                        ulRunTimeCounter = pxTaskStatusArray[i]["ulRunTimeCounter"]
                        usStackHighWaterMark = pxTaskStatusArray[i]["usStackHighWaterMark"]

                        print "%5s %5s %17s %14s %10s %15s %15s %20s %30s" % (name[0],
                                                                              xTaskNumber,
                                                                              xHandle,
                                                                              eCurrentState,
                                                                              uxCurrentPriority,
                                                                              uxBasePriority,
                                                                              ulRunTimeCounter,
                                                                              usStackHighWaterMark,
                                                                              usStackHighWaterMark * 4)

                        sum += usStackHighWaterMark
                        i += 1

                print ""
                print "                                                                                                  +                            +"
                print "                                                                                                  ---------------------------  ---------------------------\n"
                print "%110s %30s" % (sum, sum * 4)

PrintFreeRtosTaskStatusCommand()
