#!/usr/bin/env python

#########################################################################################
# Copyright (C) 2016. Dialog Semiconductor, unpublished work. This computer
# program includes Confidential, Proprietary Information and is a Trade Secret of
# Dialog Semiconductor.  All use, disclosure, and/or reproduction is prohibited
# unless authorized in writing. All Rights Reserved.
#########################################################################################


import re
import sys, getopt
import os
import subprocess
import shlex
import datetime
import xml.etree.ElementTree as ET
import xml.dom.minidom as MD
import mimetypes
import re
import shutil

portable_epoch = (datetime.datetime.now() - datetime.datetime(1970,1,1)).total_seconds()
timestamp = datetime.datetime.now().strftime("%Y%m%d-") + (str(portable_epoch)).split('.')[0]
run_folder_sum = "run_sum/run_" + timestamp
symbol_list_file = run_folder_sum + "/" + "symbols_" + timestamp + ".list"
gdb_cmds_file = run_folder_sum + "/" + "gdb_cmds_globals_" + timestamp + ".gdb"
gdb_cmds_log_file = run_folder_sum + "/" + "gdb_cmds_" + timestamp + ".log"
on_mem_snapshot_file = run_folder_sum + "/" + "online_memory_snapshot_" + timestamp + ".ihex"
ram_start = 0x7fc0000
ram_stop  = 0x7fe0000
ram_size_in_words = (ram_stop - ram_start) / 4

def header_cmd(elf_file):
        cmd = "target remote :2331\n"
        cmd += "symbol-file " + elf_file + "\n"
        cmd += "set pagination off\n"
        cmd += "set print pretty\n"
        cmd += "source gdb_custom_cmds.py\n"
        cmd += "set logging file " + gdb_cmds_log_file + "\n"
        cmd += "set logging on\n"
        return cmd

def expand_free_rtos_lists_cmd():
        expand_symbols = [ "pxReadyTasksLists",
                           "xDelayedTaskList1",
                           "xDelayedTaskList2",
                           "pxDelayedTaskList",
                           "pxOverflowDelayedTaskList",
                           "xPendingReadyList",
                           "xSuspendedTaskList"
                         ]

        cmd = "echo __EXPAND_FREE_RTOS_LIST_START__ " + "\\n" + "\n"
        for symbol in expand_symbols:
                cmd += "echo __LIST_SYMBOL__ " + symbol + " " + "\\n" + "\n"
                cmd += "ignore-errors iterate-freertos-list " + symbol + "\n"

        cmd += "echo __EXPAND_FREE_RTOS_LIST_STOP__ " + "\\n" + "\n"
        return cmd

def arm_registers_cmd():
        cmd = "echo __ARM_REGISTERS_START__ " + "\\n" + "\n"
        cmd += "i r \n"
        cmd += "echo __ARM_REGISTERS_END__ " + "\\n" + "\n"
        return cmd

def hex_dump_cmd():
        cmd = "echo __HEX_DUMP_START__ " + "\\n" + "\n"
        cmd += "x/" + str(ram_size_in_words) + "x " + str(ram_start)  + "\n"
        cmd += "echo __HEX_DUMP_END__ " + "\\n" + "\n"
        return cmd

def ihex_dump_cmd(ihex_file):
        cmd = "dump ihex memory " + ihex_file + " 0x7fc0000 0x7fe0000 \n"
        return cmd

def load_no_bin_dump_cmd(no_bin_file):
        cmd = "restore " + no_bin_file + "\n"
        return cmd

def load_bin_dump_cmd(bin_file):
        cmd = "restore " + bin_file + " binary " + str(hex(ram_start)) + "\n"
        return cmd

def footer_cmd():
        cmd = "set logging off\n"
        cmd += "quit\n"
        return cmd

def expand_free_rtos_heap_cmd():
        cmd = "echo __EXPAND_FREE_RTOS_HEAP_START__ " + "\\n" + "\n"
        cmd += "ignore-errors iterate-freertos-heap ucHeap" + "\n"
        cmd += "echo __EXPAND_FREE_RTOS_HEAP_STOP__ " + "\\n" + "\n"
        return cmd

def bt_cmd():
        cmd = "echo __CURRENT_TASK_BACKTRACE_START__ " + "\\n" + "\n"
        cmd += "bt" + "\n"
        cmd += "echo __CURRENT_TASK_BACKTRACE_STOP__ " + "\\n" + "\n"
        return cmd

def show_free_rtos_current_task_cmd():
        cmd = "echo __CURRENT_FREE_RTOS_TASK_START__ " + "\\n" + "\n"
        cmd += "ignore-errors p pxCurrentTCB->pcTaskName" + "\n"
        cmd += "echo __CURRENT_FREE_RTOS_TASK_STOP__ " + "\\n" + "\n"
        return cmd

def symbols_cmd(file_handle_symbol_list, file_handle_gdb_cmds):
        cmd = "echo __SYMBOLS_START__ " + "\\n" + "\n"
        for line in file_handle_symbol_list:
                addr = "0x" + line.split()[0]
                size = str(int("0x" + line.split()[1], 16))
                name = line.split()[3]
                if int(addr, 16) >= ram_start:
                        #list is sorted, stop if we exceed RAM range
                        if int(addr, 16) > ram_stop:
                                break
                        cmd += "echo __SYMBOL__ " + addr + " " + size + " " + name + " " + "\\n" + "\n"
                        cmd += "ignore-errors p " + name  + "\n"

        cmd += "echo __SYMBOLS_STOP__ " + "\\n" + "\n"
        return cmd

def peripheral_registers_cmd(xml_reg_file):
        cmd = "echo __PERIPHERAL_REGISTERS_START__ " + "\\n" + "\n"
        if (xml_reg_file is not None):

                tree = ET.parse(xml_reg_file)
                root = tree.getroot()

                for peripheral in root.iter('peripheral'):
                        p_name = peripheral.find('name').text
                        p_base = peripheral.find('baseAddress').text
                        cmd += "echo __PERIPHERAL__: " + p_name + "\\n" + "\n"
                        base = int(p_base, 16)
                        for register in peripheral.find('registers').iter('register'):
                                r_name = register.find('name').text
                                r_offset = register.find('addressOffset').text
                                r_size = register.find('size').text
                                offset = int(r_offset, 16)
                                address = hex(base + offset)
                                cmd += "echo __REG__: " + r_name  + " \ " + "\n"
                                cmd += "monitor memU" + r_size + " " + address + "\n"

        cmd += "echo __PERIPHERAL_REGISTERS_STOP__ " + "\\n" + "\n"
        return cmd

def show_freertos_task_status_cmd():
        # The project must have its vApplicationIdleHook() modified accordingly in order to collect
        # task information. Then dg_configTRACK_OS_HEAP must be set to 1 in the custom header file.
        cmd = "echo __FREE_RTOS_TASK_STATUS_START__ " + "\\n" + "\n"
        cmd += "ignore-errors print-freertos-task-status" + "\n"
        cmd += "echo __FREE_RTOS_TASK_STATUS_STOP__ " + "\\n" + "\n"
        return cmd

def create_gdb_cmd_file(elf_file, off_mem_snapshot_file, xml_reg_file):
        file_handle_symbol_list = open(symbol_list_file, "r")
        file_handle_gdb_cmds = open(gdb_cmds_file, "w")
        is_on_line_debugging = True

        file_handle_gdb_cmds.write(header_cmd(elf_file))

        if (off_mem_snapshot_file is not None):
                print "Loading RAM based on %s" % (off_mem_snapshot_file)
                if (is_bin_file(off_mem_snapshot_file)):
                        file_handle_gdb_cmds.write(load_bin_dump_cmd(off_mem_snapshot_file))
                        is_on_line_debugging = False
                else:
                        file_handle_gdb_cmds.write(load_no_bin_dump_cmd(off_mem_snapshot_file))
                        is_on_line_debugging = False


        if (is_on_line_debugging):
                file_handle_gdb_cmds.write(arm_registers_cmd() +
                                           bt_cmd() +
                                           ihex_dump_cmd(on_mem_snapshot_file) +
                                           symbols_cmd(file_handle_symbol_list, file_handle_gdb_cmds) +
                                           peripheral_registers_cmd(xml_reg_file) +
                                           show_free_rtos_current_task_cmd() +
                                           expand_free_rtos_lists_cmd() +
                                           expand_free_rtos_heap_cmd() +
                                           show_freertos_task_status_cmd() +
                                           hex_dump_cmd() +
                                           footer_cmd())

        else:   # Only RAM related commands should be executed
                file_handle_gdb_cmds.write(symbols_cmd(file_handle_symbol_list, file_handle_gdb_cmds) +
                                           show_free_rtos_current_task_cmd() +
                                           expand_free_rtos_lists_cmd() +
                                           expand_free_rtos_heap_cmd() +
                                           show_freertos_task_status_cmd() +
                                           hex_dump_cmd() +
                                           footer_cmd())



def usage(argv):
        print "usage: " + argv[0] + " -f <elf_file> -b <mem_snapshot_file> -g <gdb> -x <registers_xml_file>"
        print ""
        print "e.g 1 " + argv[0] + " -g arm-none-eabi-gdb-py -f ../../../../../projects/dk_apps/demos/pxp_reporter/DA14681-01-Debug_QSPI/pxp_reporter.elf"
        print "Dumps RAM contents, symbols are provided by the elf file. GDB path is provided by the -g argument."
        print ""
        print "e.g 2 " + argv[0] + " -g arm-none-eabi-gdb-py -f ../../../../../projects/dk_apps/demos/pxp_reporter/DA14681-01-Debug_QSPI/pxp_reporter.elf -b dump_memory.ihex"
        print "Dumps RAM contents, symbols are provided by the elf file, memory contents will be read using the provided ihex file."
        print "GDB path is provided by the -g argument."
        print ""
        print "e.g 3 " + argv[0] + " -g arm-none-eabi-gdb-py -f ../../../../../projects/dk_apps/demos/pxp_reporter/DA14681-01-Debug_QSPI/pxp_reporter.elf -b dump_memory.bin"
        print "Dumps RAM contents, symbols are provided by the elf file, memory contents will be read using the provided raw bin file restored at address 0x%x." % (ram_start)
        print "GDB path is provided by the -g argument."
        print ""
        print "e.g 4 " + argv[0] + " -g arm-none-eabi-gdb-py -f ../../../../../projects/dk_apps/demos/pxp_reporter/DA14681-01-Debug_QSPI/pxp_reporter.elf -x ../../../../../doc/DA14681-01.xml"
        print "Dumps RAM contents, symbols are provided by the elf file, peripheral registers, GDB path is provided by the -g argument."
        print "GDB path is provided by the -g argument."


# +------------------------------------------------ OS dependency if any -----------------------------------------------+

def create_symbol_list(elf_file):
        shell_cmd =  "arm-none-eabi-nm --print-size --numeric-sort " + elf_file
        args = shlex.split(shell_cmd)
        p = subprocess.Popen(args, stdout=subprocess.PIPE)
        output =  p.communicate()[0]
        filter_regex = "^[0-f]+\s+[0-f]+\s+.\s+.[\w\d]+"
        symbol_list_file_handle = open(symbol_list_file, 'w')
        lines = output.splitlines()
        for l in lines:
                if re.search(filter_regex, l):
                        symbol_type = l.split()[2]
                        if ((symbol_type != 't') and
                            (symbol_type != 'T') and
                            (symbol_type != 'w') and
                            (symbol_type != 'W') and
                            (symbol_type != 'N')):
                                symbol_list_file_handle.write(l + '\n')

        symbol_list_file_handle.close()

def run_debugger(gdb):
        shell_cmd = gdb + " -q --command=" + gdb_cmds_file
        if (os.system(shell_cmd)):
                print "Invalid gdb path"
                sys.exit(1)

def is_bin_file(file_name):
        # not bullet proof but hopefully it will do the job
        mime = mimetypes.guess_type(file_name)
        if (mime[0] == "application/octet-stream"):
                return True
        else:
                return False

def copy_elf_to_run_folder(elf_file):
        shutil.copy(elf_file, run_folder_sum)


def copy_map_to_run_folder(elf_file):
        l = len(elf_file)
        map_file = elf_file[ : l - 3] + "map"
        shutil.copy(map_file, run_folder_sum)

def create_folders():
        if not os.path.exists(run_folder_sum):
                os.makedirs(run_folder_sum)

def main(argv):
        elf_file = None
        off_mem_snapshot_file = None
        xml_reg_file = None
        gdb = None

        try:
                opts, args = getopt.getopt(argv[1:],"hf:b:g:x:")
        except getopt.GetoptError:
                usage(argv)
                sys.exit(2)
        if len(argv[1:]) < 1:
                usage(argv)
                sys.exit(1)
        for opt, arg in opts:
                if opt == '-h':
                        usage(argv)
                        sys.exit(0)
                elif opt == '-f':
                        # support win paths if any
                        elf_file = arg.replace('\\', '/')
                elif opt == '-b':
                        off_mem_snapshot_file = arg
                elif opt == '-g':
                        gdb = arg
                elif opt == '-x':
                        xml_reg_file = arg

        if (elf_file is None):
                print "Missing elf file"
                usage(argv)
                sys.exit(2)
        if (gdb is None):
                print "Missing gdb path"
                usage(argv)
                sys.exit(2)

        create_folders()
        copy_elf_to_run_folder(elf_file)
        copy_map_to_run_folder(elf_file)
        create_symbol_list(elf_file)
        create_gdb_cmd_file(elf_file, off_mem_snapshot_file, xml_reg_file)
        run_debugger(gdb)
        print "Output in " + gdb_cmds_log_file

if __name__ == "__main__":
        main(sys.argv[0:])
