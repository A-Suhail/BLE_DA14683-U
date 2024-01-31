####################################################################################################
#
# @name utils.py
#
# Copyright (C) 2017 Dialog Semiconductor.
# This computer program includes Confidential, Proprietary Information
# of Dialog Semiconductor. All Rights Reserved.
#
####################################################################################################

import os
import sys

SDK_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))


def is_win():
    return 'win' in sys.platform


def is_linux():
    return 'linux' in sys.platform


def normpath(path):
    os.path.normpath(path)

    if is_win():
        if not path.startswith('\"'):
            path = '\"' + path

        if not path.endswith('\"'):
            path += '\"'

    return path

