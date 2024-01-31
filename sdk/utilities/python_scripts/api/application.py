####################################################################################################
#
# @name application.py
#
# Copyright (C) 2017 Dialog Semiconductor.
# This computer program includes Confidential, Proprietary Information
# of Dialog Semiconductor. All Rights Reserved.
#
####################################################################################################

import os
import sys
import subprocess

from api.utils import normpath


class Application(object):
    def __init__(self, path):
        if not os.path.exists(path):
            raise ValueError(self.__class__.__name__ + ': ' + str(path) + ' does not exists')
        if not os.path.isfile(path) or not os.access(path, os.X_OK):
            raise ValueError(
                self.__class__.__name__ + ': ' + str(path) + ' is not application file')

        self.__path = normpath(os.path.abspath(path))

    def get_path(self):
        return self.__path

    def get_basename(self):
        return os.path.basename(self.__path)

    def run(self, args=None, cwd=None, silent=False):
        call = [self.__path] + args if args else [self.__path]
        process_params = {
            'args': ' '.join(call),
            'shell': True,
            'cwd': cwd,
            'stdout': subprocess.PIPE,
            'stderr': subprocess.STDOUT,
        }

        sys.stdout.flush()
        pr = subprocess.Popen(**process_params)

        buf = b''
        for line in pr.stdout:
            if not silent:
                sys.stdout.buffer.write(line)
                sys.stdout.flush()
            buf += line

        pr.wait()

        if pr.returncode:
            raise RuntimeError('{} call has exited with code: {}'.format(' '.join(call),
                                                                         pr.returncode))
        return buf.decode('utf-8')
