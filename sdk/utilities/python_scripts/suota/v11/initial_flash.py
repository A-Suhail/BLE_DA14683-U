####################################################################################################
#
# @name initial_flash.py
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

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(PROJECT_ROOT)

from api import ui
from api.cli_programmer import CliProgrammer
from api.jlink import select_device
from api.utils import SDK_ROOT
from qspi.prepare_local_ini_file import prepare_local_ini_file
from qspi.program_qspi_config import ProgramQspiConfig
from qspi.program_qspi_jtag import program_qspi_jtag
from qspi.reboot_device import reboot_device
from secure_image.generate_keys import ProductKeys
from suota.v11.mkimage import mkimage


SUOTA_LOADER_PATH = os.path.join(SDK_ROOT, 'sdk/bsp/system/loaders/ble_suota_loader')
QSPI_SCRIPTS_PATH = os.path.join(SDK_ROOT, 'utilities/python_scripts/qspi')
CONFIG_FILE = os.path.join(QSPI_SCRIPTS_PATH, 'program_qspi.ini')
IMAGE_FILE = 'application_image.img'
VERSION_FILE = 'sw_version.h'

NVMS_PARTITION_TABLE = 0x07F000
NVMS_IMAGE_HEADER_PART = 0x01F000
NVMS_FW_EXEC_PART = 0x020000

PRODUCT_READY_ADDR = 0x7F8E9D0
SECURE_DEVICE_ADDR = 0x7F8EA68


def initial_flash(binary, bootloader=None, nobootloader=None, cfg=None, device_id=None,
                  jlink_path=None, secure_config=None, keys=None):
    if not device_id:
        device_id = select_device(jlink_path)

    qspi_config = ProgramQspiConfig()
    if not qspi_config.get_product_id():
        qspi_config.set_product_id('DA14683-00')

    cli = CliProgrammer(cfg_path=cfg, prod_id=qspi_config.get_product_id())
    if not cfg:
        prepare_local_ini_file(cfg=cli.get_cfg(), device_id=device_id, jlink_path=jlink_path)

    if not os.path.exists(binary):
        raise RuntimeError('Binary file {} does not exist'.format(binary))

    if secure_config is not None and not os.path.exists(secure_config):
        raise RuntimeError('Configuration file {} does not exist.\n'
                           'Run secure_img_cfg.py to create one'.format(secure_config))

    ui.print_message('Using SDK from {}'.format(SDK_ROOT))
    ui.print_message('cli_programmer from {}'.format(cli.get_path()))
    ui.print_message('image file {}'.format(binary))

    if not (bootloader or nobootloader):
        bootloader_bin = 'ble_suota_loader.bin'
        suota_build_config = \
            qspi_config.get_product_id() + '-Release_' + ('OTP_Secure' if secure_config else 'QSPI')
        bootloader = os.path.join(SUOTA_LOADER_PATH, suota_build_config, bootloader_bin)
        ui.print_message('boot loader {}'.format(bootloader))

    ui.print_title('Preparing image file {}'.format(IMAGE_FILE))

    if secure_config:
        mkimage(binary, IMAGE_FILE, VERSION_FILE, security_config=secure_config)
    else:
        mkimage(binary, IMAGE_FILE)

    if not nobootloader:
        ui.print_title('Erasing bootloader area')
        cli.erase_qspi(0, 4096)

    ui.print_title('Erasing partition table')
    cli.erase_qspi(NVMS_PARTITION_TABLE, 4096)

    ui.print_title('Writing application image {}'.format(binary))
    cli.write_qspi(NVMS_FW_EXEC_PART, binary)

    ui.print_title('Writing image header {}'.format(IMAGE_FILE))
    cli.write_qspi(NVMS_IMAGE_HEADER_PART, IMAGE_FILE, 1024)
    os.remove(IMAGE_FILE)

    if not nobootloader:
        ui.print_title('Writing bootloader')
        if secure_config:
            cli.write_otp_exec(bootloader)
        else:
            program_qspi_jtag(bootloader, cfg, device_id, jlink_path)

    if secure_config:
        if keys:
            prod_keys = ProductKeys(keys)

            ui.print_title("Writing symmetric keys")
            for index, key in enumerate(prod_keys.symmetric_keys):
                cli.write_key_sym(index, key)

            ui.print_title("Writing asymmetric keys")
            for index, key in enumerate(prod_keys.asymmetric_keys):
                cli.write_key_asym(index, key.public)

        # Write 0xAA to the product ready and the secure device field in OTP header
        cli.write_otp(PRODUCT_READY_ADDR, 1, 0xAA)
        cli.write_otp(SECURE_DEVICE_ADDR, 1, 0xAA)

    reboot_device(device_id, jlink_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', '--quiet', dest='quiet', action='store_true',
                        help='reduce number of prints')

    bootloader_group = parser.add_argument_group('bootloader options')
    bootloader_group = bootloader_group.add_mutually_exclusive_group()
    bootloader_group.add_argument('-b', '--bootloader', metavar='<bootloader>', type=str,
                                  help='path to bootloader')
    bootloader_group.add_argument('--nobootloader', action='store_true',
                                  help='do not flash bootloader')

    config_group = parser.add_argument_group('configuration options')
    config_group.add_argument('--cfg', metavar='<config_path>', type=str, help='configuration file')
    config_group.add_argument('--id', metavar='<serial_number>', type=str, dest='device_id',
                              help='device serial number')
    config_group.add_argument('--jlink_path', metavar='<jlink_path>', type=str,
                              help='path to jlink')

    security_group = parser.add_argument_group('security options')
    security_group.add_argument('--secure_config', metavar='<security_cfg_path>',
                                dest='secure_config', help='path to secure config')
    security_group.add_argument('--keys', metavar='<keys_path>', dest='keys',
                                help='path to keys to be written to OTP')

    parser.add_argument('binary', metavar='<app_binary>', type=str, help='path to binary to flash')
    args = parser.parse_args()

    ui.set_verbose(not args.quiet)
    ui.print_header('INITIAL FLASH')
    initial_flash(binary=args.binary, bootloader=args.bootloader, nobootloader=args.nobootloader,
                  cfg=args.cfg, device_id=args.device_id, jlink_path=args.jlink_path,
                  secure_config=args.secure_config, keys=args.keys)
    ui.print_footer("FINISHED")
