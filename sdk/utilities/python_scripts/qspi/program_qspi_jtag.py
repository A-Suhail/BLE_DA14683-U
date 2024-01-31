####################################################################################################
#
# @name program_qspi_jtag.py
#
# Copyright (C) 2017 Dialog Semiconductor.
# This computer program includes Confidential, Proprietary Information
# of Dialog Semiconductor. All Rights Reserved.
#
####################################################################################################

#!/usr/bin/env python3
import argparse
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

from api import ui
from api.cli_programmer import CliProgrammer
from qspi.prepare_local_ini_file import prepare_local_ini_file
from qspi.program_qspi_config import ProgramQspiConfig, is_valid_product_id, select_product_id


def program_qspi_jtag(image_file, cfg=None, device_id=None, jlink_path=None):
    config = ProgramQspiConfig()
    while not is_valid_product_id(config.get_product_id()):
        config.set_product_id(select_product_id())

    cli_programmer = CliProgrammer(cfg_path=cfg, prod_id=config.get_product_id(),
                                   jlink_path=jlink_path, jlink_id=device_id)

    if not cfg:
        prepare_local_ini_file(cfg=cli_programmer.get_cfg(), device_id=device_id,
                               jlink_path=jlink_path)

    try:
        cli_programmer.write_qspi_exec(image_file=image_file, silent=False)
    except RuntimeError:
        ui.info(text="ERROR PROGRAMMING FLASH")
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cfg', metavar='<cfg_path>', type=str, help='config path')
    parser.add_argument('--id', metavar='<serial_number>', type=str, help='device serial number')
    parser.add_argument('--jlink_path', metavar='<jlink_path>', type=str, help='JLink path')
    parser.add_argument('image', metavar='<image_path>', type=str, help='Image path')
    args = parser.parse_args()

    ui.print_header('PROGRAM QSPI via JTAG')
    program_qspi_jtag(args.image, cfg=args.cfg, device_id=args.id, jlink_path=args.jlink_path)
    ui.print_footer('FINISHED')
