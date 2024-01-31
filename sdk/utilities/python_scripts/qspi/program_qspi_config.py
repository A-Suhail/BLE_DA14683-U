####################################################################################################
#
# @name program_qspi_config.py
#
# Copyright (C) 2017 Dialog Semiconductor.
# This computer program includes Confidential, Proprietary Information
# of Dialog Semiconductor. All Rights Reserved.
#
####################################################################################################

#!/usr/bin/env python3
from configparser import ConfigParser, NoSectionError
import os
from string import Template
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

from api import ui


CONFIG_PATH = os.path.join(os.path.join(os.path.dirname(__file__), 'program_qspi.ini'))
PROGRAM_QSPI_CONFIG_SECTION = 'program_qspi_config'
PRODUCT_ID = 'product_id'
PRODUCT_IDS_DICT = {
    'DA14680/1-01': 'DA14681-01',
    'DA14682/3-00': 'DA14683-00',
}

CONFIGURATION_INFO = Template(
    'Existing Configuration\n'
    '----------------------\n'
    '"PRODUCT_ID: $product_id"\n'
    '----------------------\n'
    '\n'
    'Do you want to change this configuration?'
)


class ProgramQspiConfig(object):
    def __init__(self, config_path=None):
        if not config_path:
            config_path = CONFIG_PATH

        self.config_path = config_path
        self.config = ConfigParser()
        self.config.read(self.config_path)

        try:
            self.__product_id = self.config.get(PROGRAM_QSPI_CONFIG_SECTION, PRODUCT_ID)
        except NoSectionError:
            self.__product_id = None

    def __dump(self):
        if not self.config.has_section(PROGRAM_QSPI_CONFIG_SECTION):
            self.config.add_section(PROGRAM_QSPI_CONFIG_SECTION)

        self.config.set(PROGRAM_QSPI_CONFIG_SECTION, PRODUCT_ID,
                        self.__product_id if self.__product_id else '')

        with open(self.config_path, 'w') as configfile:
            self.config.write(configfile)

    def set_product_id(self, value):
        self.__product_id = value
        self.__dump()

    def get_product_id(self):
        return self.__product_id


def is_valid_product_id(product_id):
    return product_id in PRODUCT_IDS_DICT.values()


def confirm_product_change(prod_id):
    return ui.ask(text=CONFIGURATION_INFO.substitute(product_id=prod_id),
                  confirmation='Change', denial='Keep')


def select_product_id():
    item = ui.select_item(text='Select Product ID', item_list=list(PRODUCT_IDS_DICT.keys()))
    return PRODUCT_IDS_DICT.get(item, None)


def program_qspi_config():
    config = ProgramQspiConfig()

    if is_valid_product_id(config.get_product_id()) and not \
            confirm_product_change(config.get_product_id()):
        return

    product_id = select_product_id()
    if is_valid_product_id(product_id):
        config.set_product_id(product_id)

if __name__ == '__main__':
    ui.print_header('PROGRAM QSPI CONFIGURATOR')
    program_qspi_config()
    ui.print_footer('FINISHED')
