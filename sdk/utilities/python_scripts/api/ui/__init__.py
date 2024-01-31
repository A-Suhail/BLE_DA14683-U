####################################################################################################
#
# @name __init__.py
#
# Copyright (C) 2017 Dialog Semiconductor.
# This computer program includes Confidential, Proprietary Information
# of Dialog Semiconductor. All Rights Reserved.
#
####################################################################################################

from .user_interface import UserInterface
from .cli import Cli

cli = Cli()

try:
    from .gui import Gui
    gui = Gui()
    active_interface = gui
except ImportError:
    Gui = None
    active_interface = cli

set_verbose = cli.set_verbose
print_title = cli.print_title
print_message = cli.print_message
print_header = cli.print_header
print_footer = cli.print_footer

info = active_interface.info
ask = active_interface.ask
ask_value = active_interface.ask_value
select_item = active_interface.select_item

__all__ = ['print_title', 'print_header', 'print_footer', 'print_message', 'set_verbose',
           'select_item', 'ask', 'ask_value', 'info']
