####################################################################################################
#
# @name secure_image_config.py
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
import xml.dom.minidom as xmldom
import xml.etree.ElementTree as ElemTree

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

from api.mkimage import EllipticCurve, HashMethod
from api import ui
from secure_image.generate_keys import generate_keys, ProductKeys, DEFAULT_ELLIPTIC_CURVE_IDX, \
    ALLOWED_ELLIPTIC_CURVES, DEFAULT_PRODUCT_KEYS_FILE


DEFAULT_CONFIGURATION_FILE = 'secure_img_cfg.xml'

ALLOWED_HASH_METHODS = [
    HashMethod.SHA224,
    HashMethod.SHA256,
    HashMethod.SHA384,
    HashMethod.SHA512,
]

DEFAULT_HASH_METHOD_IDX = ALLOWED_HASH_METHODS.index(HashMethod.SHA256)


class SecurityConfig:
    SECURE_IMG_CONFIG_TAG = 'secure_img_cfg'
    SECURITY_TAG = 'security'
    KEY_IDX_TAG = 'key_idx'
    PRIVATE_KEY_TAG = 'private_key'
    HASH_METHOD_TAG = 'hash_method'
    ELL_CRV_TAG = 'elliptic_curve'
    DEV_ADM_TAG = 'device_administration'
    MINIMAL_VERSION_TAG = 'minimal_version'
    KEY_REV_TAG = 'key_revocation'

    def is_valid(self):
        return self.security_key_idx is not None and \
               self.security_private_key is not None and \
               self.security_hash_method is not None and \
               self.security_elliptic_curve is not None

    def __init__(self, configuration_file):
        self.__file = configuration_file

        self.security_key_idx = None
        self.security_private_key = None
        self.security_hash_method = None
        self.security_elliptic_curve = None

        self.adm_minimal_version = None
        self.adm_key_revocations = {}

        try:
            root = ElemTree.parse(configuration_file).getroot()
        except (ElemTree.ParseError, FileNotFoundError):
            root = ElemTree.Element(SecurityConfig.SECURE_IMG_CONFIG_TAG)

        security = root.find(SecurityConfig.SECURITY_TAG)
        if security:
            key_idx = security.find(SecurityConfig.KEY_IDX_TAG)
            self.security_key_idx = int(key_idx.text) if key_idx is not None else None

            private_key = security.find(SecurityConfig.PRIVATE_KEY_TAG)
            self.security_private_key = private_key.text if private_key is not None else None

            hash_method = security.find(SecurityConfig.HASH_METHOD_TAG)
            self.security_hash_method = \
                HashMethod(hash_method.text) if hash_method is not None else None

            elliptic_curve = security.find(SecurityConfig.ELL_CRV_TAG)
            self.security_elliptic_curve = \
                EllipticCurve(elliptic_curve.text) if elliptic_curve is not None else None

        administration = root.find(SecurityConfig.DEV_ADM_TAG)
        if administration:
            min_version = administration.find(SecurityConfig.MINIMAL_VERSION_TAG)
            self.adm_minimal_version = min_version.text if min_version is not None else None
            self.adm_key_revocations = {
                k.text for k in administration.findall(SecurityConfig.KEY_REV_TAG)
            }

    def save(self):
        if not self.is_valid():
            raise ValueError('Configuration is incomplete')

        root = ElemTree.Element(SecurityConfig.SECURE_IMG_CONFIG_TAG)

        security = ElemTree.Element(SecurityConfig.SECURITY_TAG)

        key_idx = ElemTree.Element(SecurityConfig.KEY_IDX_TAG)
        key_idx.text = str(self.security_key_idx)
        security.append(key_idx)

        private_key = ElemTree.Element(SecurityConfig.PRIVATE_KEY_TAG)
        private_key.text = str(self.security_private_key)
        security.append(private_key)

        hash_method = ElemTree.Element(SecurityConfig.HASH_METHOD_TAG)
        hash_method.text = str(self.security_hash_method.value)
        security.append(hash_method)

        elliptic_curve = ElemTree.Element(SecurityConfig.ELL_CRV_TAG)
        elliptic_curve.text = str(self.security_elliptic_curve.value)
        security.append(elliptic_curve)

        root.append(security)

        administration = ElemTree.Element(SecurityConfig.DEV_ADM_TAG)

        if self.adm_minimal_version:
            min_ver = ElemTree.Element(SecurityConfig.MINIMAL_VERSION_TAG)
            min_ver.text = str(self.adm_minimal_version)
            administration.append(min_ver)

        for key in self.adm_key_revocations:
            elem = ElemTree.Element(SecurityConfig.KEY_REV_TAG)
            elem.text = str(key)
            administration.append(elem)

        root.append(administration)

        with open(self.__file, 'wb') as f:
            text = ElemTree.tostring(root)
            f.write(xmldom.parseString(text).toprettyxml(indent=' ' * 4, encoding='UTF-8'))


def secure_img_cfg(configuration_file=None, product_keys=None, key_idx=None, private_key=None,
                   elliptic_curve=None, hash_method=None, key_revocations=None, min_version=None):
    if configuration_file is None:
        configuration_file = DEFAULT_CONFIGURATION_FILE

    security_config = SecurityConfig(configuration_file)

    if os.path.exists(configuration_file) and security_config.is_valid():
        configuration_str = \
            'Security:\n' \
            '\tKey index: ' + str(security_config.security_key_idx) + '\n' \
            '\tPrivate key: ' + str(security_config.security_private_key) + '\n' \
            '\tElliptic curve: ' + str(security_config.security_elliptic_curve.value) + '\n' \
            '\tHash method: ' + str(security_config.security_hash_method.value) + '\n' \
            'Administration:\n' + \
            '\tMinimal version: ' + str(security_config.adm_minimal_version or '') + '\n' \
            '\tKey revocations: ' + str(security_config.adm_key_revocations or '')

        if not ui.ask(text='Would you like to change existing configuration?\n' + configuration_str,
                      confirmation='Change', denial='Keep'):
            return

    if not product_keys:
        product_keys = DEFAULT_PRODUCT_KEYS_FILE

    if ui.ask(text='Would you like to create new product keys file?'):
        generate_keys(product_keys)

    ui.print_message('Using product keys file: ' + os.path.normpath(product_keys))

    if os.path.exists(product_keys) and key_idx is not None:
        try:
            key = ProductKeys(product_keys).asymmetric_keys[int(key_idx)]
        except KeyError:
            raise RuntimeError('Invalid key index for product key file' +
                               os.path.normpath(product_keys))

        private_key = key.private if private_key is None else private_key

        elliptic_curve = \
            key.elliptic_curve if elliptic_curve is None else EllipticCurve(elliptic_curve)

    elif os.path.exists(product_keys) and ui.ask(text='Would you like to choose private key from '
                                                      'file: ' + os.path.normpath(product_keys)):
        items = ['{0: <15} | {1}'.format(key.elliptic_curve.value, key.private) for
                 key in ProductKeys(product_keys).asymmetric_keys]

        selected = None
        while not selected:
            selected = ui.select_item(item_list=items)

        key_idx = items.index(selected)
        elliptic_curve, private_key = (e.strip() for e in selected.split('|'))
        elliptic_curve = EllipticCurve(elliptic_curve)

    else:
        while not key_idx:
            key_idx = ui.ask_value(text='Insert key index or address in OTP',
                                   value_name='key index')

        while not private_key:
            private_key = ui.ask_value(text='Insert private key to be used',
                                       value_name='private key')

        while not elliptic_curve:
            elliptic_curve = ui.select_item(item_list=[e.value for e in ALLOWED_ELLIPTIC_CURVES],
                                            text='Select elliptic curve',
                                            default=DEFAULT_ELLIPTIC_CURVE_IDX)
        elliptic_curve = EllipticCurve(elliptic_curve)

    if elliptic_curve == EllipticCurve.EDWARDS25519:
        hash_method = HashMethod.SHA512

    while not hash_method:
        hash_method = ui.select_item(item_list=[e.value for e in ALLOWED_HASH_METHODS],
                                     text='Select hash method', default=DEFAULT_HASH_METHOD_IDX)
    hash_method = HashMethod(hash_method)

    if key_revocations is None and ui.ask(text='Would you like to add key revocations?'):
        key_revocations = ui.ask_value(value_name='key revocations',
                                       text='Insert values separated by spaces')

    key_revocations = set(key_revocations.split(' ')) if key_revocations else {}

    if min_version == '' and ui.ask(text='Would you like to add minimal version?'):
        min_version = ui.ask_value(value_name='minimal version')

    security_config.security_key_idx = key_idx
    security_config.security_private_key = private_key
    security_config.security_elliptic_curve = elliptic_curve
    security_config.security_hash_method = hash_method

    security_config.adm_key_revocations = key_revocations
    security_config.adm_minimal_version = min_version

    security_config.save()
    ui.print_message('Configuration saved to ' + configuration_file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', dest='verbose', action='store_true', help='set verbose')
    parser.add_argument('-cfg', metavar='<configuration_file>', dest='configuration_file',
                        help='configuration file')

    parser.add_argument('--product_keys', help='product keys file')

    parser.add_argument('--key_idx', help='index of key used im image signature')
    parser.add_argument('--private_key', help='private key')
    parser.add_argument('-ec', '--elliptic_curve',
                        choices=[e.value for e in ALLOWED_ELLIPTIC_CURVES],
                        dest='elliptic_curve', help='elliptic curve')
    parser.add_argument('-hm', '--hash_method', choices=[e.value for e in ALLOWED_HASH_METHODS],
                        dest='hash_method', help='hash method')

    parser.add_argument('--key_revocations', nargs='*', help='indexes of keys to revoke')
    parser.add_argument('--min_version', help='minimal version', nargs='?', default='')

    args = parser.parse_args()

    ui.set_verbose(args.verbose)
    ui.print_header('SECURE IMAGE CONFIGURATOR')
    secure_img_cfg(configuration_file=args.configuration_file, product_keys=args.product_keys,
                   key_idx=args.key_idx, private_key=args.private_key,
                   elliptic_curve=args.elliptic_curve, hash_method=args.hash_method,
                   key_revocations=args.key_revocations, min_version=args.min_version)
    ui.print_footer('FINISHED')
