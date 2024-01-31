####################################################################################################
#
# @name mkimage.py
#
# Copyright (C) 2017 Dialog Semiconductor.
# This computer program includes Confidential, Proprietary Information
# of Dialog Semiconductor. All Rights Reserved.
#
####################################################################################################

#!/usr/bin/env python3
import argparse
import os
import re
import string
import sys
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(PROJECT_ROOT)

from api import ui
from api.mkimage import Mkimage, MKIMAGE_BIN
from api.utils import SDK_ROOT
from secure_image.secure_image_config import SecurityConfig


DEFAULT_VERSION_FILE = 'sw_version.h'
DEFAULT_VERSION = '1.0.0.1'
SW_VERSION_PATTERN = re.compile(r'#define BLACKORCA_SW_VERSION ["]((?:\d+\.){3}\d+)["]')


def make_sw_version_file(version_file=DEFAULT_VERSION_FILE, version=DEFAULT_VERSION,
                         date=time.strftime('%Y-%m-%d %H:%M')):

    sw_version_template = string.Template(
        '#define BLACKORCA_SW_VERSION "$version"\n'
        '#define BLACKORCA_SW_VERSION_DATE "$date"\n'
        '#define BLACKORCA_SW_VERSION_STATUS "REPOSITORY VERSION"\n'
    )

    with open(version_file, 'w') as f:
        f.write(sw_version_template.substitute(version=version, date=date))


def mkimage(binary_file, image_file=None, version_file=None, security_config=None):
    if not os.path.isfile(MKIMAGE_BIN):
        raise RuntimeError('{} not found, please build it'.format(os.path.basename(MKIMAGE_BIN)))

    if not os.path.exists(binary_file):
        raise RuntimeError('Binary file {} does not exist'.format(binary_file))

    if not version_file:
        version_file = DEFAULT_VERSION_FILE

    ui.print_message('Using SDK from {}'.format(SDK_ROOT))

    version = DEFAULT_VERSION
    if os.path.isfile(version_file):
        with open(version_file, 'r') as f:
            try:
                version = SW_VERSION_PATTERN.findall(f.read())[0]
            except IndexError:
                os.rename(f.name, f.name + '.err')

    if not os.path.exists(version_file):
        if security_config:
            raise RuntimeError('Invalid version file: {}'.format(version_file))
        else:
            make_sw_version_file(version_file)

    if not image_file:
        image_file = '.'.join([binary_file, version, 'img'])
        ui.print_message('No image file specified creating {}'.format(image_file))

    if security_config:
        cfg = SecurityConfig(security_config)
        return Mkimage().secure(binary_file, version_file, image_file,
                                ec=cfg.security_elliptic_curve,
                                hash_type=cfg.security_hash_method,
                                key=cfg.security_private_key,
                                key_id=cfg.security_key_idx,
                                rev_list=cfg.adm_key_revocations,
                                min_ver=True if cfg.adm_minimal_version else False,
                                ver=cfg.adm_minimal_version)
    else:
        return Mkimage().single(binary_file, version_file, image_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', '--quiet', dest='quiet', action='store_true',
                        help='reduce number of prints')
    parser.add_argument('binary', metavar='bin_file', type=str,
                        help='file with application binary')
    parser.add_argument('image', metavar='image_file', type=str, nargs='?',
                        help='output file with image for SUOTA')
    parser.add_argument('--sw_version', metavar='sw_version_file', dest='sw_version_file',
                        type=str, help='version file used for binary')
    parser.add_argument('-s', '--sec_cfg', metavar='security_config', dest='security_config',
                        type=str, help='configuration for secure image (forces secure image)')
    args = parser.parse_args()

    ui.set_verbose(not args.quiet)
    mkimage(args.binary, image_file=args.image, version_file=args.sw_version_file,
            security_config=args.security_config)
