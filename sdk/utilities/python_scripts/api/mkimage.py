####################################################################################################
#
# @name mkimage.py
#
# Copyright (C) 2017 Dialog Semiconductor.
# This computer program includes Confidential, Proprietary Information
# of Dialog Semiconductor. All Rights Reserved.
#
####################################################################################################

import os
import enum

from api.application import Application
from api.utils import is_linux, is_win, SDK_ROOT, normpath

if is_win():
    MKIMAGE_BIN = os.path.join(SDK_ROOT, 'binaries/mkimage.exe')
elif is_linux():
    MKIMAGE_BIN = os.path.join(SDK_ROOT, 'binaries/mkimage')
else:
    MKIMAGE_BIN = ''


@enum.unique
class EllipticCurve(enum.Enum):
    SECP192R1 = 'SECP192R1'
    SECP224R1 = 'SECP224R1'
    SECP256R1 = 'SECP256R1'
    SECP384R1 = 'SECP384R1'
    BP256R1 = 'BP256R1'
    BP384R1 = 'BP384R1'
    BP512R1 = 'BP512R1'
    SECP192K1 = 'SECP192K1'
    SECP224K1 = 'SECP224K1'
    SECP256K1 = 'SECP256K1'
    CURVE25519 = 'CURVE25519'
    EDWARDS25519 = 'EDWARDS25519'


@enum.unique
class HashMethod(enum.Enum):
    SHA224 = 'SHA-224'
    SHA256 = 'SHA-256'
    SHA384 = 'SHA-384'
    SHA512 = 'SHA-512'


class Mkimage(Application):
    def __init__(self, path=MKIMAGE_BIN):
        super().__init__(path)

    def single(self, in_file, version_file, out_file, enc=None, key=None, iv=None, **kwargs):
        cmd = ['single', normpath(in_file), normpath(version_file), normpath(out_file)]
        if enc:
            cmd.append(enc)
        if key:
            cmd.append(key)
        if iv:
            cmd.append(iv)
        return self.run(args=cmd, **kwargs)

    def gen_sym_key(self, num=None, key_len=None, **kwargs):
        cmd = ['gen_sym_key']
        if num:
            cmd.append(str(num))
        if key_len:
            cmd.append(str(key_len))
        return self.run(args=cmd, **kwargs)

    def gen_asym_key(self, ec, num=None, **kwargs):
        cmd = ['gen_asym_key', ec.value]
        if num:
            cmd.append(str(num))
        return self.run(args=cmd, **kwargs)

    def secure(self, in_file, ver_file, out_file, ec, hash_type, key, key_id, rev_list=None,
               min_ver=False, ver=None, **kwargs):
        cmd = ['secure', normpath(in_file), normpath(ver_file), normpath(out_file), ec.value,
               hash_type.value, key, str(key_id)]
        if rev_list:
            cmd.extend(['rev', "{}".format(' '.join(map(str, rev_list)))])
        if min_ver:
            cmd.append('min_ver')
            if ver:
                cmd.append(ver)
        return self.run(args=cmd, **kwargs)
