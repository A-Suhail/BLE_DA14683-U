####################################################################################################
#
# @name jlink.py
#
# Copyright (C) 2017 Dialog Semiconductor.
# This computer program includes Confidential, Proprietary Information
# of Dialog Semiconductor. All Rights Reserved.
#
####################################################################################################

import os
import re

from api import ui
from api.application import Application
from api.utils import is_linux, is_win

SCRIPTS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
JLINK_SCRIPTS_PATH = os.path.join(SCRIPTS_ROOT, 'api/jlink_scripts')
JLINK_SHOWEMULIST = os.path.join(JLINK_SCRIPTS_PATH, 'jlink_showemulist.script')
JLINK_REBOOT = os.path.join(JLINK_SCRIPTS_PATH, 'reboot.script')

if is_win():
    JLINK_EXE = "JLink.exe"
    JLINK_GDB = "JLinkGDBServerCL.exe"
elif is_linux():
    JLINK_EXE = "JLinkExe"
    JLINK_GDB = "JLinkGDBServer"
else:
    JLINK_EXE = ''
    JLINK_GDB = ''


def get_default_jlink_path():
    if is_win():
        from winreg import OpenKey, QueryValueEx, EnumKey, KEY_READ, HKEY_CURRENT_USER

        def enumerate_keys(key):
            i = 0
            while True:
                try:
                    yield EnumKey(key, i)
                    i += 1
                except WindowsError:
                    break

        jlink_root_path = 'Software\SEGGER\J-Link'
        jlink_install_path = ''
        with OpenKey(HKEY_CURRENT_USER, jlink_root_path, 0, KEY_READ) as registry:
            for subdir in enumerate_keys(registry):
                with OpenKey(registry, subdir) as install_path:
                    jlink_install_path, _ = QueryValueEx(install_path, "InstallPath")
        return jlink_install_path
    elif is_linux():
        for path in os.environ["PATH"].split(os.pathsep):
            binary_path = '/'.join([path.strip('"'), "JLinkExe"])
            if os.path.isfile(binary_path) and os.access(binary_path, os.X_OK):
                return path
        return ''
    else:
        return ''


def get_jlink_exe(jlink_path=None):
    return os.path.join(jlink_path if jlink_path else get_default_jlink_path(), JLINK_EXE)


def get_jlink_gdb(jlink_path=None):
    return os.path.join(jlink_path if jlink_path else get_default_jlink_path(), JLINK_GDB)


class JLinkExe(Application):
    def __init__(self, path=None):
        super().__init__(get_jlink_exe(path))

    def find_jlink_numbers(self, **kwargs):
        cmd = ["-ExitOnError", "-CommandFile", JLINK_SHOWEMULIST]
        kwargs['silent'] = True
        out = self.run(args=cmd, **kwargs)
        return re.findall('Serial number: (\d+)', str(out))

    def reboot_device(self, device_id, **kwargs):
        cmd = ['-if', 'SWD', '-device', 'Cortex-M0', '-speed', 'auto', '-SelectEmuBySN', device_id,
               '-CommandFile', JLINK_REBOOT]
        return self.run(args=cmd, **kwargs)


class JLinkGDB(Application):
    def __init__(self, path=None):
        super().__init__(get_jlink_gdb(path))


def select_device(jlink_path):
    devices = JLinkExe(jlink_path).find_jlink_numbers()

    if not devices:
        raise RuntimeError('No devices found. Please connect at least one and retry.')

    return devices[0] if len(devices) == 1 else ui.select_item(item_list=devices,
                                                               text='Select jlink serial')
