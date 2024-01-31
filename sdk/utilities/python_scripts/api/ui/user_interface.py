####################################################################################################
#
# @name user_interface.py
#
# Copyright (C) 2017 Dialog Semiconductor.
# This computer program includes Confidential, Proprietary Information
# of Dialog Semiconductor. All Rights Reserved.
#
####################################################################################################

class UserInterface:
    def info(self, text):
        raise NotImplementedError

    def ask(self, text, confirmation='Yes', denial='No'):
        raise NotImplementedError

    def select_item(self, item_list, text='Select item', default=None):
        raise NotImplementedError

    def ask_value(self, value_name, text='Insert value', default=None):
        raise NotImplementedError
