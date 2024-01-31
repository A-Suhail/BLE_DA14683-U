####################################################################################################
#
# @name reboot_device.py
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
from api.jlink import JLinkExe, select_device


def reboot_device(device_id=None, jlink_path=None):
    jlink_exe = JLinkExe(jlink_path)

    if not device_id:
        device_id = select_device(jlink_path)

    if not device_id:
        return

    jlink_exe.reboot_device(device_id, silent=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('device_id', metavar='[serial_number]', type=str, nargs='?',
                        help='device serial number')
    parser.add_argument('--jlink_path', metavar='<jlink_path>', type=str, help='JLink path')
    args = parser.parse_args()

    reboot_device(args.device_id, args.jlink_path)
