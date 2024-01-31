####################################################################################################
#
# @name gui.py
#
# Copyright (C) 2017 Dialog Semiconductor.
# This computer program includes Confidential, Proprietary Information
# of Dialog Semiconductor. All Rights Reserved.
#
####################################################################################################

import tkinter as tk

from .user_interface import UserInterface


class Gui(UserInterface):

    MIN_WIDTH = 200
    MIN_HEIGHT = 0

    def info(self, text):
        root = tk.Tk()
        root.title('INFO')
        root.minsize(width=Gui.MIN_WIDTH, height=Gui.MIN_HEIGHT)
        root.resizable(False, False)
        tk.Label(root, text=text, justify=tk.LEFT).pack(padx=10, pady=10)
        tk.Button(text="OK", command=lambda: root.destroy()).pack(side=tk.BOTTOM, padx=10, pady=10)
        tk.mainloop()

    def ask(self, text, confirmation='Yes', denial='No'):
        root = tk.Tk()
        root.title('Answer question')
        root.minsize(width=Gui.MIN_WIDTH, height=Gui.MIN_HEIGHT)
        root.resizable(False, False)
        ret_val = tk.BooleanVar(False)
        tk.Label(root, text=text, justify=tk.LEFT).pack(padx=10, pady=10)

        def ok():
            ret_val.set(True)
            root.destroy()

        def cancel():
            root.destroy()

        tk.Button(text=confirmation, command=ok).pack(side=tk.RIGHT, padx=5, pady=5)
        tk.Button(text=denial, command=cancel).pack(side=tk.RIGHT, padx=5, pady=5)

        tk.mainloop()
        return bool(ret_val.get())

    def ask_value(self, value_name, text='Insert value', default=None):
        root = tk.Tk()
        root.title('Input value')
        root.minsize(width=Gui.MIN_WIDTH, height=Gui.MIN_HEIGHT)
        root.resizable(False, False)
        ret_val = tk.StringVar()
        tk.Label(root, text=text, justify=tk.LEFT).pack(padx=10, pady=10)

        value_frame = tk.Frame()
        tk.Label(value_frame, text=value_name + ': ', justify=tk.CENTER).pack(side=tk.LEFT)
        text = tk.Entry(value_frame, justify=tk.LEFT)
        text.pack(side=tk.RIGHT)
        value_frame.pack(padx=10, pady=10)

        def ok():
            ret_val.set(text.get())
            root.destroy()

        def cancel():
            root.destroy()

        tk.Button(text='OK', command=ok).pack(side=tk.RIGHT, padx=5, pady=5)
        tk.Button(text='Cancel', command=cancel).pack(side=tk.RIGHT, padx=5, pady=5)

        tk.mainloop()
        return ret_val.get()

    def select_item(self, item_list, text='Select item', default=None):
        root = tk.Tk()
        root.title('Select item')
        root.minsize(width=Gui.MIN_WIDTH, height=Gui.MIN_HEIGHT)
        root.resizable(False, False)
        ret_val = tk.StringVar()
        tk.Label(root, text=text, justify=tk.LEFT).pack(padx=10, pady=10)

        listbox = tk.Listbox(root)
        listbox.pack(padx=10, pady=10, expand=1, fill=tk.BOTH)
        listbox.config(width=max([len(str(e)) for e in item_list]))

        for item in item_list:
            listbox.insert(tk.END, item)

        def ok():
            ret_val.set(item_list[listbox.curselection()[0]])
            root.destroy()

        def cancel():
            root.destroy()

        ok_button = tk.Button(text='OK', command=ok)
        ok_button.pack(side=tk.RIGHT, padx=5, pady=5)
        tk.Button(text='Cancel', command=cancel).pack(side=tk.RIGHT, padx=5, pady=5)

        if default is not None:
            listbox.selection_set(default)
        else:
            listbox.selection_set(0)

        listbox.bind('<Double-1>', lambda x: ok_button.invoke())
        tk.mainloop()

        return ret_val.get()
