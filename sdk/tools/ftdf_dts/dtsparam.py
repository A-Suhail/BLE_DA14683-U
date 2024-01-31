####################################################################################################
#
# @file dtsparam.py
#
# @brief DTS helper Python script
#
# Copyright (C) 2015 Dialog Semiconductor.
# This computer program includes Confidential, Proprietary Information
# of Dialog Semiconductor. All Rights Reserved.
#
####################################################################################################

import logging, sys
import xml.etree.ElementTree as xml
from datetime import datetime
from os import rename

thismodule = sys.modules[__name__]

CONTINUE = 0
STOP = 1

class DTS_Param:
    cfg             = []
    params          = []
    script          = []
    logName         = 'log/dts.txt'
    logMode         = 'w'
    logTimeStr      = ''
    logLevel        = logging.DEBUG
    logLevelConsole = logging.WARNING
    logAddTime      = False
    atFail          = CONTINUE
    dut             = []

    expParams = {'logName'          : 'Name of the log file, default: log/dts.txt',
                 'logMode'          : '"w" for write, "a" for append',
                 'logLevel'         : 'Log level for log file. Values: DEBUG,INFO,WARNING,ERROR',
                 'logLevelConsole'  : 'Log level for console. Values: DEBUG,INFO,WARNING,ERROR',
                 'logAddTime'       : 'If "True", a timestamp will be added to logName',
                 'atFail'           : 'Whether to continue with the next script if a script fail. Values CONTINUE, STOP',
                }

    expLists = {'script': 'Script to be executed',
                'dut':    'DUT configurations, only in XML configuration file' }

    #############################################
    # Parameter check functions
    #############################################
    def logLevelCheck(self, val):
        num_lvl = getattr(logging, val.upper(), None)
        if not isinstance(num_lvl, int):
            raise ValueError('Invalid log level: %s' % val)
        self.logLevel = num_lvl

    def logLevelConsoleCheck(self, val):
        num_lvl = getattr(logging, val.upper(), None)
        if not isinstance(num_lvl, int):
            raise ValueError('Invalid log level console: %s' % val)
        self.logLevelConsole = num_lvl

    def logAddTimeCheck(self, val):
        if val.upper() == 'TRUE':
            self.logAddTime = True
            curTime = datetime.now()
            self.logTimeStr = '.' + str(curTime.year).zfill(4) + '-' + str(curTime.month).zfill(2) + '-' + str(curTime.day).zfill(2) + '_' + str(curTime.hour).zfill(2) + '.' + str(curTime.minute).zfill(2) + '.' + str(curTime.second).zfill(2)

    def atFailCheck(self, val):
        at_fail = getattr(thismodule, val.upper(), None)
        if not isinstance(at_fail, int):
            raise ValueError('Invalid atFail value: %s' % val)
        self.atFail = at_fail

    #############################################
    # init
    #############################################
    def __init__(self, cfg, params, scripts):
        self.cfg = cfg
        self.params = params
        self.script = scripts
        self.reInit()

    def reInit(self):
        self.dut = []
        if self.script and ('script' in self.expLists):
            self.expLists.pop('script')
        for f in self.cfg:
            self.parseCfg(f)
        for f in self.params:
            mark = f.find('=')
            self.parseParam(f[:mark],f[mark + 1:])
        if self.logTimeStr != '':
            self.logName = self.logName[:self.logName.find('.')] + self.logTimeStr + self.logName[self.logName.find('.'):]

    #############################################
    # Parse functions
    #############################################
    def parseParam(self, name, val):
        if name in self.expParams:
            # Check if there is a checker function for this parameter
            if hasattr(self, name + "Check"):
                eval("self." + name + "Check('" + val + "')")
            else:
                tmp = getattr(self, name)
                # In case of a list, extend the list
                if isinstance(tmp, list):
                    setattr(self, name, tmp + [val])
                else:
                    setattr(self, name, val)
        else:
            print('Invalid parameter:', name, val)
            quit()

    def parseCfg(self, cfg):
        # Create an XML tree object and search for tags
        tree        = xml.parse(cfg)
        treeInit    = tree.find('dts')

        for i in self.expParams:
            if treeInit.find(i) != None:
                self.parseParam(i, treeInit.find(i).text)

        for i in self.expLists:
            l = []
            for j in treeInit.findall(i):
                if j.text != None:
                    l += [ j.text ]
                else:
                    l.append( j.attrib )
            if (l):
                setattr(self, i, getattr(self, i) + l)

def initLogger(dtsParam, streamHandler, createHandlers):
    dtsLogger = logging.getLogger('dts')
    dtsLogger.setLevel(logging.DEBUG)

    # Backup previous log file if it exists
    if dtsParam.logAddTime == False:
        try:
            rename(dtsParam.logName, dtsParam.logName + '.bak')
        except:
            pass

    if createHandlers:
        # Create file handler for log file
        fh = logging.FileHandler(dtsParam.logName, mode=dtsParam.logMode)
        fh.setLevel(dtsParam.logLevel)

        # Create stream handler for console logging
        sh = streamHandler
        sh.setLevel(dtsParam.logLevelConsole)

        # Create formatters
        fhfrmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(fhfrmt)

        shfrmt = logging.Formatter('%(levelname)s - %(message)s')
        sh.setFormatter(shfrmt)

        # Add handlers
        dtsLogger.addHandler(fh)
        dtsLogger.addHandler(sh)

    return dtsLogger


########################################
# Help subjects
# name: help_<subject>
########################################
def help_USAGE():
    """\033[1mUSAGE\033[0m

    Usage:
        dts -?

    Extended help:
        dts -h [<section>]

    Normal usage:
        dts [-c <configfile>] [-ud] [parameter=value] [<script>] -o [<script parameters>]

    -c <configfile>
        With the -c option present, the file <configfile> is used as config file.
        Without the -c option the default "config/dts.xml" is used as config file.

    -u
        Enable UART debug tracing.

    -d
        Dump all parameters and stop.

    -o
        Parameters following this option are sent to the script as a list.
        The list is named "scriptparams".

    parameter=value
        The parameters are the same as found in the config file, see section parameters.
        Any parameter specified here overrides the parameter specified in the config file.

    <script>
        With script(s) supplied, only the script(s) specified here are executed.
        Without script(s) supplied, the scripts specified in the config file are executed.

    """

def help_CONFIG():
    """\033[1mCONFIG\033[0m

    The config file is formatted in XML style. The XML root must be "dts".
    The possible parameters are listed in the section parameters.

    """

def help_PARAMETERS():
    """\033[1mPARAMETERS\033[0m

    The parameters specified in the config file are processed first. Then any parameters
    on the command line are processed. This means that all parameters on the command line
    overwrite the corresponding parameter in the config file.

    For single field values, only the last value is used.
    For list field values, the current list is extended.
    """

    print("\033[1m    Single fields\n\033[0m")
    for i in sorted(DTS_Param.expParams):
        print("    %-16s %s\n" % (i, DTS_Param.expParams[i]))

    print("\033[1m    List fields\n\033[0m")
    for i in sorted(DTS_Param.expLists):
        print("    %-16s %s\n" % (i, DTS_Param.expLists[i]))

def help(subject):
    l = ['USAGE', 'CONFIG', 'PARAMETERS']

    if subject == '':
        for i in l:
            eval('print(help_' + i + '.__doc__)')
            eval('help_' + i + '()')
    elif subject in l:
        eval('print(help_' + subject + '.__doc__)')
        eval('help_' + subject + '()')
        quit()

    return l

