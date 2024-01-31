####################################################################################################
#
# @name generate_keys.py
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
import sys
import xml.dom.minidom as xmldom
import xml.etree.ElementTree as ElemTree

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

from api.mkimage import Mkimage, EllipticCurve, MKIMAGE_BIN
from api import ui


DEFAULT_PRODUCT_KEYS_FILE = 'product_keys.xml'

SYMMETRIC_KEYS_NUM = 8
SYMMETRIC_KEYS_LEN = 32

ASYMMETRIC_KEYS_NUM = 4

ALLOWED_ELLIPTIC_CURVES = [
    EllipticCurve.SECP256R1,
    EllipticCurve.SECP224R1,
    EllipticCurve.SECP192R1,
    EllipticCurve.EDWARDS25519
]

DEFAULT_ELLIPTIC_CURVE_IDX = ALLOWED_ELLIPTIC_CURVES.index(EllipticCurve.SECP256R1)


class ProductKeys:
    KEYS_TAG = 'keys'
    SYMMETRIC_TAG = 'symmetric'
    ASYMMETRIC_TAG = 'asymmetric'

    class AsymmetricKey:
        def __init__(self, private, public, elliptic_curve):
            self.private = private
            self.public = public
            self.elliptic_curve = elliptic_curve

    def clear_symmetric_keys(self):
        self.symmetric_keys = []

    def add_symmetric_key(self, key):
        self.symmetric_keys.append(key)

    def clear_asymmetric_keys(self):
        self.asymmetric_keys = []

    def add_asymmetric_key(self, private, public, elliptic_curve):
        self.asymmetric_keys.append(ProductKeys.AsymmetricKey(private, public, elliptic_curve))

    def __init__(self, config_file):
        self.__file = config_file
        self.symmetric_keys = []
        self.asymmetric_keys = []

        try:
            root = ElemTree.parse(config_file).getroot()
        except (ElemTree.ParseError, FileNotFoundError):
            root = ElemTree.Element(ProductKeys.KEYS_TAG)

        for key in root.find(ProductKeys.SYMMETRIC_TAG) or []:
            self.add_symmetric_key(key.text)

        for key in root.find(ProductKeys.ASYMMETRIC_TAG) or []:
            self.add_asymmetric_key(key.find('private').text, key.find('public').text,
                                    EllipticCurve(key.find('elliptic_curve').text))

    def save(self):
        root = ElemTree.Element(ProductKeys.KEYS_TAG)

        symmetric = ElemTree.Element(ProductKeys.SYMMETRIC_TAG)
        for key in self.symmetric_keys:
            elem = ElemTree.Element('symmetric_key')
            elem.text = key
            symmetric.append(elem)
        root.append(symmetric)

        asymmetric = ElemTree.Element(ProductKeys.ASYMMETRIC_TAG)
        for key in self.asymmetric_keys:
            elem = ElemTree.Element('asymmetric_keys')

            private = ElemTree.Element('private')
            private.text = key.private
            elem.append(private)

            public = ElemTree.Element('public')
            public.text = key.public
            elem.append(public)

            elliptic_curve = ElemTree.Element('elliptic_curve')
            elliptic_curve.text = key.elliptic_curve.value
            elem.append(elliptic_curve)

            asymmetric.append(elem)
        root.append(asymmetric)

        with open(self.__file, 'wb') as f:
            text = ElemTree.tostring(root, short_empty_elements=False)
            f.write(xmldom.parseString(text).toprettyxml(indent=' ' * 4, encoding='UTF-8'))


def generate_symmetric_keys(key_number, length):
    sym_key_pat = re.compile(r'[ ]+#\d+: ([0-9A-F]+)')
    return sym_key_pat.findall(Mkimage().gen_sym_key(key_number, length))


def generate_asymmetric_keys(key_number, elliptic_curve):
    asym_key_pat = re.compile(r'[ ]+PRIVATE KEY:[ ]+([0-9A-F]+)\r*?\n[ ]+PUBLIC KEY:[ ]+([0-9A-F]+)',
                              re.MULTILINE)
    return asym_key_pat.findall(Mkimage().gen_asym_key(elliptic_curve, key_number))


def generate_keys(output_file=None, elliptic_curve=None):
    if not output_file:
        output_file = DEFAULT_PRODUCT_KEYS_FILE

    if not os.path.exists(MKIMAGE_BIN):
        raise RuntimeError('Can not find mkimage. Please install it and run this script again.')

    if os.path.exists(output_file):
        if ui.ask(text='Product keys file already exists.\n'
                       'Would you like to move it to "' + output_file + '.old" and make new file?'):
            os.replace(output_file, output_file + '.old')
        else:
            ui.print_message('Aborting key generation')
            return

    product_keys = ProductKeys(output_file)
    ui.print_message('Writing keys to {}'.format(output_file))

    if not elliptic_curve:
        elliptic_curve = \
            EllipticCurve(ui.select_item(text='Select elliptic curve used for asymmetric keys',
                                         item_list=[c.value for c in ALLOWED_ELLIPTIC_CURVES]))

    for key in generate_symmetric_keys(SYMMETRIC_KEYS_NUM, SYMMETRIC_KEYS_LEN):
        product_keys.add_symmetric_key(key=key)

    for private, public in generate_asymmetric_keys(ASYMMETRIC_KEYS_NUM, elliptic_curve):
        product_keys.add_asymmetric_key(private=private, public=public,
                                        elliptic_curve=elliptic_curve)

    product_keys.save()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', dest='verbose', action='store_true', help='set verbose')
    parser.add_argument('-o', metavar='<file>', dest='output_file', help='output file')
    parser.add_argument('-ec', '--elliptic_curve', dest='elliptic_curve', help='elliptic curve',
                        choices=[e.value for e in ALLOWED_ELLIPTIC_CURVES])
    args = parser.parse_args()

    ui.set_verbose(args.verbose)
    ui.print_header('GENERATING PRODUCT KEYS')
    generate_keys(output_file=args.output_file, elliptic_curve=args.elliptic_curve)
    ui.print_footer('FINISHED')
