#!/bin/bash

readonly DUMP_FOLDER="register_dumps"
readonly CONFIG_PATH="../../../qspi/"
readonly LOCAL_CONFIG_FILE="program_qspi.ini"
readonly CONFIG_FILE="${CONFIG_PATH}/${LOCAL_CONFIG_FILE}"
readonly CONFIG_SCRIPT="${CONFIG_PATH}/program_qspi_config.sh"
readonly GDB_CMDS_FILE="gdb_cmds"
readonly GDB_OUT_FILE="gdb.txt"
readonly TRUE=0
readonly FALSE=1

function run_gdb
{
        arm-none-eabi-gdb --command=gdb_cmds
}

function store_dump_file
{
        Date=$(date +"%Y%m%d-%s")
        name="registers_${Date}.log"
        mkdir -p ${DUMP_FOLDER}
        if [ -e ${GDB_OUT_FILE} ]
        then
                mv ${GDB_OUT_FILE} register_dumps/${name}
                path=$(pwd)
                echo "Register dump file ${name} is found in ${path}/${DUMP_FOLDER}"
        fi
}

function generate_gdb_cmd_file
{
        if [ "${PRODUCT_ID}" = "DA14680-01" ] || [ "${PRODUCT_ID}" = "DA14681-01" ]
        then
                ./generate_gdb_cmds.py -f ../../../../../config/embsys/Dialog_Semiconductor/DA14681-01.xml -g
                return $?
        elif  [ "${PRODUCT_ID}" = "DA14682-00" ] || [ "${PRODUCT_ID}" = "DA14683-00" ]
        then
                ./generate_gdb_cmds.py -f ../../../../../config/embsys/Dialog_Semiconductor/DA14683-00.xml -g
                return $?
        else
                echo "Invalid chip revision"
                exit
        fi
}

function run_chip_selection
{
        if [ ! -e ${CONFIG_FILE} ]
        then
                ${CONFIG_SCRIPT}
                mv ${LOCAL_CONFIG_FILE} ${CONFIG_PATH}
        fi

        source ${CONFIG_FILE}
}

function check_for_gdb_cmds_file
{
        if [ -e ${GDB_CMDS_FILE} ]
        then
                return ${TRUE}
        fi
        return ${FALSE}
}

function run_main
{
        run_chip_selection
        if check_for_gdb_cmds_file
        then
                echo "Using the existing ${GDB_CMDS_FILE} file"
                # reconfig_chip
        else
                generate_gdb_cmd_file
        fi

        run_gdb
        store_dump_file
}

run_main
