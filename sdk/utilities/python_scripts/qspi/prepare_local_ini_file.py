####################################################################################################
#
# @name prepare_local_ini_file.py
#
# Copyright (C) 2017 Dialog Semiconductor.
# This computer program includes Confidential, Proprietary Information
# of Dialog Semiconductor. All Rights Reserved.
#
####################################################################################################

#!/usr/bin/env python3
import argparse
from configparser import ConfigParser
import os
import re
from string import Template
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

from api import ui
from api import utils
from api.cli_programmer import CliProgrammer
from api.jlink import get_jlink_gdb, select_device


DEFAULT_GDB_PORT = 2331

DEFAULT_CFG = 'cli_programmer.ini'
DEFAULT_JLINK_LOG = 'jlink.log'

GDB_SERVER_SECTION = 'gdb server'
TRC_SECTION = 'target reset'


def get_gdb_server_path(jlink_path, device_id, port, swoport, telnetport, log):
    gdb_server_path_template = Template(
        '$gdb -if swd -device Cortex-M0 -endian little -speed 4000 -singlerun -select '
        'usb=$device_id -port $port -swoport $swoport -telnetport $telnetport -log $log'
    )

    substitutes = {
        'gdb': utils.normpath(get_jlink_gdb(jlink_path)),
        'device_id': device_id,
        'port': str(port),
        'swoport': str(swoport),
        'telnetport': str(telnetport),
        'log': utils.normpath(log)
    }

    gdb_server_path = gdb_server_path_template.substitute(substitutes)

    if not device_id:
        gdb_server_path = re.sub('-select usb=None *', '', gdb_server_path)

    return gdb_server_path


def prepare_local_ini_file(cfg=None, device_id=None, port=None, log=None, target_reset_cmd=None,
                           jlink_path=None):
    if not device_id:
        device_id = select_device(jlink_path)

    ui.print_message("Using device with id {}".format(device_id))

    if cfg is None:
        cfg = DEFAULT_CFG

    if not port:
        port = DEFAULT_GDB_PORT

    if not log:
        log = DEFAULT_JLINK_LOG

    if not target_reset_cmd:
        target_reset_cmd = ''

    # Initialize cli_programmer.ini if doesn't exist
    CliProgrammer(cfg_path=cfg)

    config = ConfigParser()
    config.read(cfg)

    config.set(GDB_SERVER_SECTION, 'gdb_server_path',
               get_gdb_server_path(jlink_path=jlink_path, device_id=device_id, port=port,
                                   swoport=port + 1, telnetport=port + 2, log=log))
    config.set(GDB_SERVER_SECTION, 'port', str(port))

    trc_cmd = config.get(TRC_SECTION, 'target_reset_cmd')
    if len(trc_cmd) < 20:
        trc_cmd = target_reset_cmd
    if target_reset_cmd:
        if device_id:
            if '-selectemubysn' in trc_cmd:
                trc_cmd = re.sub(
                    '[ ]*-selectemubysn [0-9]*', ' -selectemubysn ' + device_id, trc_cmd)
            else:
                trc_cmd += ' -selectemubysn ' + device_id
        else:
            trc_cmd = re.sub("[ ]*-selectemubysn [0-9]*", "", trc_cmd)

    config.set(TRC_SECTION, 'target_reset_cmd', trc_cmd)

    with open(cfg, 'w+') as out_file:
        config.write(out_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cfg', metavar='<cfg_path>', type=str, help='config path')
    parser.add_argument('--id', metavar='<serial_number>', type=str, help='device serial number')
    parser.add_argument('--port', metavar='<port>', type=int, help='GDB port')
    parser.add_argument('--log', metavar='<log>', type=str, help='JLink log')
    parser.add_argument('--trc', metavar='<target_reset_cmd>', type=str,
                        help='target reset command')
    parser.add_argument('--jlink_path', metavar='<jlink_path>', type=str, help='JLink path')
    args = parser.parse_args()

    prepare_local_ini_file(cfg=args.cfg, device_id=args.id, port=args.port, log=args.log,
                           target_reset_cmd=args.trc, jlink_path=args.jlink_path)
