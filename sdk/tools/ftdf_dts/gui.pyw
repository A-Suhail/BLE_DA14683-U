#!/usr/bin/env python3
import serial, logging, re, math, sys, webbrowser

# Block importing of the "_elementtree" module which imports a XMLParser version
# that cannot be customised.
sys.modules['_elementtree'] = None

import xml.etree.ElementTree as xml
from queue import Queue

# DTS imports
from dts import *
from scriptIncludes import *

# TKInter imports
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog



'''
    Golbals:
'''
guiTimeout = .5

#
style = ttk.Style()
style.configure('My.TFrame', background='white')

#
fontBold = ('TkDefaultFont', 8, 'bold')

# Customise XMLParser class so that it preserves comments
class CommentXMLParser ( xml.XMLParser ):
    def __init__ ( self, html = 0, target = None ):
        xml.XMLParser.__init__( self, html, target )
        self._parser.CommentHandler = self.handle_comment

    def handle_comment ( self, data ):
        self._target.start( xml.Comment, {} )
        self._target.data( data )
        self._target.end( xml.Comment )

class ToolTip:
    def __init__(self, master, text='Your text here', delay=1500, **opts):
        self.master = master
        self._opts = {'anchor':'center', 'bd':1, 'bg':'lightyellow', 'delay':delay, 'fg':'black',\
                      'follow_mouse':0, 'font':None, 'justify':'left', 'padx':4, 'pady':2,\
                      'relief':'solid', 'state':'normal', 'text':text, 'textvariable':None,\
                      'width':0, 'wraplength':150}
        self.configure(**opts)
        self._tipwindow = None
        self._id = None
        self._id1 = self.master.bind("<Enter>", self.enter, '+')
        self._id2 = self.master.bind("<Leave>", self.leave, '+')
        self._id3 = self.master.bind("<ButtonPress>", self.leave, '+')
        self._follow_mouse = 0
        if self._opts['follow_mouse']:
            self._id4 = self.master.bind("<Motion>", self.motion, '+')
            self._follow_mouse = 1

    def configure(self, **opts):
        for key in opts:
            if key in self._opts:
                self._opts[key] = opts[key]
            else:
                KeyError = 'KeyError: Unknown option: "%s"' %key
                raise KeyError

    ##----these methods handle the callbacks on "<Enter>", "<Leave>" and "<Motion>"---------------##
    ##----events on the parent widget; override them if you want to change the widget's behavior--##

    def enter(self, event=None):
        self._schedule()

    def leave(self, event=None):
        self._unschedule()
        self._hide()

    def motion(self, event=None):
        if self._tipwindow and self._follow_mouse:
            x, y = self.coords()
            self._tipwindow.wm_geometry("+%d+%d" % (x, y))

    ##------the methods that do the work:---------------------------------------------------------##

    def _schedule(self):
        self._unschedule()
        if self._opts['state'] == 'disabled':
            return
        self._id = self.master.after(self._opts['delay'], self._show)

    def _unschedule(self):
        id = self._id
        self._id = None
        if id:
            self.master.after_cancel(id)

    def _show(self):
        if self._opts['state'] == 'disabled':
            self._unschedule()
            return
        if not self._tipwindow:
            self._tipwindow = tw = tk.Toplevel(self.master)
            # hide the window until we know the geometry
            tw.withdraw()
            tw.wm_overrideredirect(1)

            if tw.tk.call("tk", "windowingsystem") == 'aqua':
                tw.tk.call("::tk::unsupported::MacWindowStyle", "style", tw._w, "help", "none")

            self.create_contents()
            tw.update_idletasks()
            x, y = self.coords()
            tw.wm_geometry("+%d+%d" % (x, y))
            tw.deiconify()

    def _hide(self):
        tw = self._tipwindow
        self._tipwindow = None
        if tw:
            tw.destroy()

    ##----these methods might be overridden in derived classes:----------------------------------##

    def coords(self):
        # The tip window must be completely outside the master widget;
        # otherwise when the mouse enters the tip window we get
        # a leave event and it disappears, and then we get an enter
        # event and it reappears, and so on forever :-(
        # or we take care that the mouse pointer is always outside the tipwindow :-)
        tw = self._tipwindow
        twx, twy = tw.winfo_reqwidth(), tw.winfo_reqheight()
        w, h = tw.winfo_screenwidth(), tw.winfo_screenheight()
        # calculate the y coordinate:
        if self._follow_mouse:
            y = tw.winfo_pointery() + 20
            # make sure the tipwindow is never outside the screen:
            if y + twy > h:
                y = y - twy - 30
        else:
            y = self.master.winfo_rooty() + self.master.winfo_height() + 3
            if y + twy > h:
                y = self.master.winfo_rooty() - twy - 3
        # we can use the same x coord in both cases:
        x = tw.winfo_pointerx() - twx / 2
        if x < 0:
            x = 0
        elif x + twx > w:
            x = w - twx
        return x, y

    def create_contents(self):
        opts = self._opts.copy()
        for opt in ('delay', 'follow_mouse', 'state'):
            del opts[opt]
        label = tk.Label(self._tipwindow, **opts)
        label.pack()

def xmlBeautify(elem, level=0):
    indent = "\n"
    for i in range(level):
        indent += "  "

    lastChild = None

    for child in elem.getchildren():
        if child.tag != xml.Comment:
            xmlBeautify(child, level + 1)
        lastChild = child

    if lastChild != None:
        lastChild.tail = indent

    elem.tail = indent

class Application(ttk.Frame):
    def __init__(self, master=None):

        ''' Class variables '''
        self.rootFrame = 0
        self.selectedFile = ''
        self.listOfScripts = []
        self.comPortList = []
        self.dtsConFilLoc = 'config/dts.xml'

        self.logLevelRef = 0
        self.logLevelConsoleRef = 0
        self.atFailRef = 0
        self.outputLogRef = 0
        self.selectButRef = 0
        self.startButRef = 0
        self.pathBarRef = 0

        self.testRunning = False
        self.scriptThr = 0

        # scrollbar content window
        self.canvasRef = 0

        self.configTabContent = {
            'nrOfDut': 0,
            'configDutPar': []
        }

        # Get number of DUT's in config file
        self.parser = CommentXMLParser()
        self.tree = xml.parse(self.dtsConFilLoc, parser=self.parser)
        root = self.tree.getroot()
        dts = root.find('dts')

        nrOfDut = 0
        for dut in dts.iter('dut'):
            self.configTabContent['configDutPar'].append( { 'port': '',
                                                            'idRef': 0,
                                                            'portRef': 0,
                                                            'addressRef': 0,
                                                            'umacVerRef': 0,
                                                            'lmacVerRef': 0,
                                                            'xmlConf': dut } )
            nrOfDut += 1

        self.configTabContent['nrOfDut'] = nrOfDut

        # Content Tab
        self.contentTabRef = 0
        self.contentTabFrameRef = 0

        ''' End of variables '''

        ttk.Frame.__init__(self, master)
        self.grid()

        # Make application rizesable
        self.grid(sticky=tk.N+tk.S+tk.E+tk.W)
        top=self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.rootFrame = ttk.Frame(self, name='top')
        self.rootFrame.pack(side=tk.TOP, fill=tk.BOTH, expan=tk.Y)

        notebook = ttk.Notebook(self.rootFrame, name='notebook')
        notebook.pack(fill=tk.BOTH, expand=tk.Y, padx=2, pady=3)

        self.configTab_getSerialPorts()

        self.mainTab_create(notebook,self.rootFrame)
        self.configTab_create(notebook)
        self.licenseTab_create(notebook)

        self.notebook = notebook

        try:
            top.iconbitmap("dialog.ico")
        except tk.TclError:
            img = tk.PhotoImage(file='dialog.gif')
            top.tk.call("wm", "iconphoto", top._w, img)


    '''
        Global functions:
    '''

    def updateConfFile(self):
        # XML output beautifying
        root = self.tree.getroot()
        xmlBeautify(root)
        self.tree.write(self.dtsConFilLoc, encoding="utf-8", xml_declaration = True)

    def handleTabChangedEvent(self,event):
        selectedTab = event.widget.tab(event.widget.index("current"))['text']
        if(selectedTab == 'Config'):
            idx = 0
            while( idx < self.configTabContent['nrOfDut'] ):
                self.configTab_getDutConfigValues(idx)
                idx+=1

    def displayPopup(self, popupText):
        w = 300
        h = 100
        
        # Calculate the popup geometry such that it is centered over the master window
        self.update_idletasks()
        masterGeometry = re.split('[x+]', self.master.winfo_geometry())
        popupGeometry = "+%d+%d" % (int(masterGeometry[2]) + int(masterGeometry[0])/2 - w/2,
                                    int(masterGeometry[3]) + int(masterGeometry[1])/2 - h/2)
        
        toplevel = tk.Toplevel(takefocus=True, background='white')
        toplevel.geometry(popupGeometry)
        toplevel.transient(self.rootFrame) # To center the popup above the main window
        toplevel.title('ERROR')
        toplevel.minsize(width=w, height=h)
        try:
            toplevel.grab_set() # To disable the main window under the popup
        except tk.TclError:
            pass
        frame = ttk.Frame(toplevel, style='My.TFrame')
        frame.pack(expand=tk.Y)

        lbl = ttk.Label(frame, text=popupText, background='white')
        lbl.grid(column=0, row=0, padx=10, pady=10)
        but = ttk.Button(frame, text='OK', command=toplevel.destroy)
        but.grid(column=0, row=1, padx=10, pady=10)


    '''
        Main Tab functions:
    '''
    def mainTab_create(self,notebook,rootFrame):
        # frames
        frame = ttk.Frame(notebook, name='main', style='My.TFrame')
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        frame1 = ttk.Frame(frame, style='My.TFrame')
        frame1.grid(column=0, row=0, pady=10, sticky=tk.N+tk.S+tk.E+tk.W)
        frame1.rowconfigure(0, weight=1)
        frame1.columnconfigure(0, weight=0)

        frame2 = ttk.Frame(frame, style='My.TFrame')
        frame2.rowconfigure(0, weight=1)
        frame2.columnconfigure(0, weight=1)
        frame2.grid(column=0, row=1,  padx=10, sticky=tk.N+tk.S+tk.E+tk.W)

        frame3 = ttk.Frame(frame, style='My.TFrame')
        frame3.rowconfigure(0, weight=1)
        frame3.columnconfigure(0, weight=1)
        frame3.grid(column=0, row=2, padx=10, pady=10, sticky=tk.N+tk.S+tk.E+tk.W)

        # dropdown: Console
        if dtsParam.logLevelConsole == logging.DEBUG:
            logLevelConsole = 0
        elif dtsParam.logLevelConsole == logging.INFO:
            logLevelConsole = 1
        elif dtsParam.logLevelConsole == logging.WARNING:
            logLevelConsole = 2
        else:
            logLevelConsole = 3

        tempFrame = ttk.Frame(frame1)
        tempFrame.grid(column=0, row=0, padx=10, sticky=tk.W)
        lbl = ttk.Label(tempFrame, text='Console:', background='white', font=fontBold)
        lbl.grid(column=0, row=0, ipadx=2, sticky=tk.N+tk.S)
        self.logLevelConsoleRef = ttk.Combobox(tempFrame, exportselection=0)
        self.logLevelConsoleRef['values'] = ('debug', 'info', 'warning', 'error')
        self.logLevelConsoleRef.current(logLevelConsole)
        self.logLevelConsoleRef.bind('<<ComboboxSelected>>', self.mainTab_setConfigFileValues)
        self.logLevelConsoleRef.grid(column=1, row=0)

        ToolTip(self.logLevelConsoleRef, follow_mouse=1, text='Defines the console output level.\nLevel "debug" gives the most output and level "error" the least')

        # dropdown: Logging
        if dtsParam.logLevel == logging.DEBUG:
            logLevel = 0
        elif dtsParam.logLevel == logging.INFO:
            logLevel = 1
        elif dtsParam.logLevel == logging.WARNING:
            logLevel = 2
        else:
            logLevel = 3

        tempFrame = ttk.Frame(frame1)
        tempFrame.grid(column=1, row=0, padx=10, sticky=tk.W)
        lbl = ttk.Label(tempFrame, text='Logging:', background='white', font=fontBold)
        lbl.grid(column=0, row=0, ipadx=2, sticky=tk.N+tk.S)
        self.logLevelRef = ttk.Combobox(tempFrame, exportselection=0)
        self.logLevelRef['values'] = ('debug', 'info', 'warning', 'error')
        self.logLevelRef.current(logLevel)
        self.logLevelRef.bind('<<ComboboxSelected>>', self.mainTab_setConfigFileValues)
        self.logLevelRef.grid(column=1, row=0)

        ToolTip(self.logLevelRef, follow_mouse=1, text='Defines the log file output level.\nLevel "debug" gives the most output and level "error" the least')

        # dropdown: At fail
        if dtsParam.atFail == dtsparam.CONTINUE:
            atFail = 0
        else:
            atFail = 1

        tempFrame = ttk.Frame(frame1)
        tempFrame.grid(column=2, row=0, padx=10, sticky=tk.W)
        lbl = ttk.Label(tempFrame, text='At fail:', background='white', font=fontBold)
        lbl.grid(column=0, row=0, ipadx=2, sticky=tk.N+tk.S)
        self.atFailRef = ttk.Combobox(tempFrame, exportselection=0)
        self.atFailRef['values'] = ('continue', 'stop')
        self.atFailRef.current(atFail)
        self.atFailRef.bind('<<ComboboxSelected>>', self.mainTab_setConfigFileValues)
        self.atFailRef.grid(column=1, row=0)

        ToolTip(self.atFailRef, follow_mouse=1, text='Indicates in case of a list of scripts whether DTS will continue with the next script or stops after the failed script')

        # Output text
        self.outputLogRef = tk.Text(frame2, background='white', borderwidth=1, relief=tk.RIDGE)
        self.outputLogRef.grid(column=0, row=0, sticky=tk.N+tk.S+tk.E+tk.W)
        self.outputLogRef.configure(state='normal')
        self.outputLogRef.tag_config('red', foreground="red")
        self.outputLogRef.tag_config('green', foreground="dark green")
        self.outputLogRef.tag_config('blue', foreground="midnight blue")
        self.outputLogRef.tag_config('black', foreground="black")

        scrollbar = tk.Scrollbar(frame2, orient="vertical")
        scrollbar.grid(column=1, row=0, sticky=tk.NS)
        self.outputLogRef.configure(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.outputLogRef.yview)

        self.outputLogRef.configure(state='disabled')

        # Select file
        self.pathBarRef = tk.Text(frame3, height=1, background='white', borderwidth=1, relief=tk.RIDGE)
        self.pathBarRef.grid(column=0, row=0, sticky=tk.EW)
        ToolTip(self.pathBarRef, follow_mouse=1, text='The script or script list to be run or is running. Use "Select" to select another script or script list')

        tempFr = ttk.Frame(frame3)
        tempFr.grid(column=1, row=0, padx=5)
        self.selectButRef = ttk.Button(tempFr, text='Select', command=lambda:self.mainTab_displayFileSelect())
        self.selectButRef.grid(column=0, row=0)
        ToolTip(self.selectButRef, follow_mouse=1, text='Select a script (file type *.py) or script list (file type *.list) to be run.')
        self.startButRef = ttk.Button(tempFr, text='Start', command=lambda:self.mainTab_startTest())
        self.startButRef.grid(column=1, row=0)
        ToolTip(self.startButRef, follow_mouse=1, text='Start a script or list of scripts.')
        but = ttk.Button(tempFr, text='Abort', command=lambda:self.mainTab_abortTest())
        but.grid(column=2, row=0)
        ToolTip(but, follow_mouse=1, text='Abort the running script')

        notebook.add(frame, text='Main', underline=0, padding=2, sticky=tk.N+tk.S+tk.E+tk.W)
        notebook.bind_all("<<NotebookTabChanged>>", self.handleTabChangedEvent) # Event generated when changing tab

        self.after(10,self.mainTab_updateText)


    def mainTab_displayFileSelect(self):
        selectedFile = filedialog.askopenfilename(title='Select a file', filetypes=[('Single script', '.py'), ('List of scripts', '.list')])

        if len(selectedFile) == 0:
            return

        self.pathBarRef.delete(1.0, tk.END) # Clear previous selection
        self.pathBarRef.insert(tk.INSERT, selectedFile)


    def mainTab_getSelectedFile(self):
        f = self.pathBarRef.get( 1.0, tk.END )

        if f == '\n':
            self.selectedFile = ''
            self.displayPopup('No file selected')
            return

        self.selectedFile = f[:f.find('\n')]

        if (self.selectedFile.find('.') == -1 or
            self.selectedFile.find('.') == len(self.selectedFile) - 1):
            self.selectedFile = ''
            self.displayPopup('Selected file has no extension')
            return

        try:
            tmpFile = open(self.selectedFile, 'r')
        except:
            self.selectedFile = ''
            self.displayPopup('Selected file not found')
            return

        tmpFile.close()

        extension = self.selectedFile.split('.', 1)

        if(extension[1] == 'list'):
            # Found list file read file paths from list file
            fileObject = open(self.selectedFile, 'r', 1)

            self.listOfScripts = []
            idx = 0
            for line in fileObject:
                if line == '\n':
                    idx+=1
                    continue
                elif line[ len(line) - 1 ] == '\n':
                    line = line[:len(line) - 1]
                self.listOfScripts.append(line)
                idx+=1

            fileObject.close()
        else:
            # Save single script selection
            self.listOfScripts = []
            self.listOfScripts.append(self.selectedFile)

    def mainTab_setConfigFileValues(self, event = None):
        root = self.tree.getroot()
        dts = root.find('dts')
        dts.find('logLevel').text = self.logLevelRef.get()
        dts.find('logLevelConsole').text = self.logLevelConsoleRef.get()
        dts.find('logAddTime').text = 'true'
        dts.find('atFail').text = self.atFailRef.get()

        # write to dts.xml to keep original config file intact
        self.updateConfFile()

    def mainTab_startTest(self):
        self.mainTab_getSelectedFile( )

        if(self.selectedFile):
            if self.testRunning == True:
                return

            self.outputLogRef.configure(state='normal')
            self.outputLogRef.delete(1.0, tk.END)
            self.outputLogRef.configure(state='disabled')

            # Re-initialize the logger so that a new logfile is created
            DTS_disableLogger( )
            DTS_enableLogger( )

            # diable main tab interface
            self.selectButRef.configure(state='disabled')
            self.startButRef.configure(state='disabled')
            self.pathBarRef.configure(state='disabled')

            # disable config tab
            for idx, item in enumerate(self.notebook.tabs()):
                if ('config' in item) or ('license' in item):
                    self.notebook.tab(item, state='disabled')

            self.testRunning = True

            self.scriptThr = DTS_startScripts( self.listOfScripts)

    def mainTab_abortTest(self):
        if self.testRunning:
            DTS_abortScripts( self.scriptThr )

    def mainTab_updateText(self):
        while True:
            qitem = 0
            try:
                qitem = DTS_consoleQueue.get( block=False )
            except:
                self.after(10,self.mainTab_updateText)
                return

            if self.testRunning == False:
                self.after(10,self.mainTab_updateText)
                return

            if type( qitem ) == dict:
                # this is queue item from log stream
                color = "black"

                if qitem['level'] == 'DEBUG':
                    color = "blue"
                elif qitem['level'] == 'INFO':
                    color = "green"
                elif qitem['level'] == 'WARNING':
                    color = "red"
                elif qitem['level'] == 'ERROR':
                    color = "red"
                elif qitem['level'] == 'CRITICAL':
                    color = "red"

                self.outputLogRef.configure(state='normal')
                self.outputLogRef.insert(tk.END, qitem['msg'] + '\n', color)
                self.outputLogRef.configure(state='disabled')
                self.outputLogRef.yview(tk.END)
            elif type( qitem ) == list:
                # this is test results
                self.outputLogRef.configure(state='normal')
                self.outputLogRef.insert(tk.END, '\n*******************************************************\n','blue')
                self.outputLogRef.insert(tk.END, '* TEST RESULTS\n','blue')
                self.outputLogRef.insert(tk.END, '*******************************************************\n','blue')

                for index, result in enumerate( qitem ):
                    logResult = ''
                    color     = ''

                    if result == 0:
                        logResult = 'PASSED'
                        color     = 'green'
                    else:
                        logResult = 'FAILED'
                        color     = 'red'

                    self.outputLogRef.insert(tk.END, 'SCRIPT: ' + str(self.listOfScripts[index]) + ' = ' + logResult + '\n',color)

                self.outputLogRef.configure(state='disabled')
                self.outputLogRef.yview(tk.END)

                # enable main tab interface
                self.selectButRef.configure(state='normal')
                self.startButRef.configure(state='normal')
                self.pathBarRef.configure(state='normal')

                # enable config tab
                for idx, item in enumerate(self.notebook.tabs()):
                    if ('config' in item) or ('license' in item):
                        self.notebook.tab(item, state='normal')

                # disable loggers
                DTS_disableLogger( )

                self.testRunning = False
            elif type( qitem ) == str:
                # this is script info
                self.outputLogRef.configure(state='normal')
                self.outputLogRef.insert(tk.END, qitem + '\n', 'black')
                self.outputLogRef.configure(state='disabled')
                self.outputLogRef.yview(tk.END)

            DTS_consoleQueue.task_done( )
            continue


    '''
        Config Tab functions:
    '''
    def AuxscrollFunction(self,event):
        self.canvasRef.configure(scrollregion=self.canvasRef.bbox("all"))

    def configTab_create(self,notebook):
        self.contentTabRef = ttk.Frame(notebook, name='config', style='My.TFrame', height=200)
        self.contentTabRef.grid(column=0, row=0, pady=10)
        notebook.add(self.contentTabRef, text='Config', underline=0, padding=2)

        # Content tab scrollbar
        scrollbarRef = ttk.Scrollbar(self.contentTabRef, orient=tk.VERTICAL)
        scrollbarRef.grid(column=1, row=0, sticky=tk.NS)

        self.canvasRef = tk.Canvas(self.contentTabRef, yscrollcommand = scrollbarRef.set, background='white')
        self.canvasRef.grid(column=0, row=0, sticky=tk.NSEW)

        scrollbarRef['command'] = self.canvasRef.yview

        self.contentTabRef.rowconfigure(0,weight=1)
        self.contentTabRef.columnconfigure(0,weight=1)

        self.canvasRef.yscrollcommand = scrollbarRef.set

        self.contentTabFrameRef = ttk.Frame(self.canvasRef,style='My.TFrame')
        self.contentTabFrameRef.bind("<Configure>", self.AuxscrollFunction)

        self.canvasRef.create_window(0, 0, window=self.contentTabFrameRef, anchor=tk.NW)

        self.configTab_setContent()

    def configTab_getSerialPorts(self):
        # Scan for available COM ports
        available = []
        for i in range(256):
            try:
                s = serial.Serial(i)
                available.append( (i, s.portstr))
                s.close()
            except:
                pass

        for i in range(256):
            try:
                s = serial.Serial('/dev/ttyUSB'+str(i))
                available.append( ('/dev/ttyUSB'+str(i), s.portstr))
                s.close()
            except:
                pass

        self.comPortList = ['']
        for n,s in available:
            self.comPortList.append(s)

    def configTab_setContent(self):
        for child in self.contentTabFrameRef.winfo_children():
            child.destroy()

        but = ttk.Button(self.contentTabFrameRef, text='Create', command=lambda:self.configTab_createDevice())
        but.grid(column=0, row=0, padx=10, sticky=tk.W)

        ToolTip(but, follow_mouse=1, text='Create a new DUT.')

        idx = 0
        while( idx < self.configTabContent['nrOfDut'] ):
            self.configTab_displayDutForm(idx)
            self.configTab_getDutConfigValues(idx)
            self.configTab_getDutPar(idx)
            idx += 1

    def configTab_createDevice(self):
        # New variables for DUT parameters
        configDutPar = { 'port': '',
                         'idRef': 0,
                         'portRef': 0,
                         'addressRef': 0,
                         'umacVerRef': 0,
                         'lmacVerRef': 0,
                         'xmlConf': None }

        nrOfDut = self.configTabContent['nrOfDut'] + 1
        self.configTabContent['nrOfDut'] = nrOfDut
        self.configTabContent['configDutPar'].append( configDutPar )

        # New DTS config file entry
        root = self.tree.getroot()
        dts = root.find('dts')

        insertIdx = 0
        idx = 0
        for elem in dts.getchildren():
            idx += 1
            if elem.tag == "atFail" or elem.tag == "dut":
                insertIdx = idx

        dut = dts.makeelement('dut', {})
        dts.insert(insertIdx, dut)

        dut.set('id','')
        dut.set('port','')
        dut.set('address','0000000000000000')

        configDutPar['xmlConf'] = dut

        self.updateConfFile()

        # Display the new DUT form on the interface
        self.configTab_displayDutForm(nrOfDut - 1)
        self.configTab_getDutConfigValues(nrOfDut - 1)
        self.configTab_getDutPar(nrOfDut - 1)

    def configTab_deleteDevice(self,dutNr):
        # Delete variables for DUT parameters
        # Delete GUI config file entry
        root = self.tree.getroot()
        dts = root.find('dts')

        dts.remove(self.configTabContent['configDutPar'][dutNr]['xmlConf'])

        self.configTabContent['nrOfDut'] -= 1
        self.configTabContent['configDutPar'].pop(dutNr)

        self.updateConfFile()

        # Reload config tab
        self.configTab_setContent()

    def configTab_displayDutForm(self,dutNr):
        columnNr = 0
        if(dutNr % 2):
            columnNr = 1
        rowNr = math.trunc(dutNr / 2) + 1

        frame = ttk.Frame(self.contentTabFrameRef, style='My.TFrame')
        frame.grid(column=columnNr, row=rowNr, padx=10, pady=10)

        formLabel = ''.join( map( str, ('DUT ', dutNr+1) ))
        lbl = ttk.Label(frame, text=formLabel, background='white', font=fontBold)
        lbl.grid(column=0, row=0, sticky=tk.W)

        lbl = ttk.Label(frame, text='Id:', background='white', font=fontBold)
        lbl.grid(column=0, row=1, sticky=tk.W)
        self.configTabContent['configDutPar'][dutNr]['idRef'] = tk.Entry(frame, width=10, background='white', borderwidth=1, relief=tk.RIDGE)
        self.configTabContent['configDutPar'][dutNr]['idRef'].grid(column=1, row=1, padx=10, pady=2, sticky=tk.W)

        ToolTip(self.configTabContent['configDutPar'][dutNr]['idRef'], follow_mouse=1, text='The numeric ID of this DUT. This ID is used in the test scrips to address a DUT.')

        lbl = ttk.Label(frame, text='Port:', background='white', font=fontBold)
        lbl.grid(column=0, row=2, sticky=tk.W)
        self.configTabContent['configDutPar'][dutNr]['portRef'] = ttk.Combobox(frame, exportselection=0)
        self.configTabContent['configDutPar'][dutNr]['portRef'].grid(column=1, row=2, padx=10, pady=2, sticky=tk.W)
        self.configTabContent['configDutPar'][dutNr]['portRef'].bind('<<ComboboxSelected>>', lambda event:self.configTab_setPortSelVal(event,dutNr))

        ToolTip(self.configTabContent['configDutPar'][dutNr]['portRef'], follow_mouse=1, text='The serial port used to comminicate with this DUT.')

        lbl = ttk.Label(frame, text='Address:', background='white', font=fontBold)
        lbl.grid(column=0, row=3, sticky=tk.W)
        self.configTabContent['configDutPar'][dutNr]['addressRef'] = tk.Entry(frame, width=20, background='white', borderwidth=1, relief=tk.RIDGE)
        self.configTabContent['configDutPar'][dutNr]['addressRef'].grid(column=1, row=3, padx=10, pady=2, sticky=tk.W)

        ToolTip(self.configTabContent['configDutPar'][dutNr]['addressRef'], follow_mouse=1, text='The extended address to be used for this DUT.')

        lbl = ttk.Label(frame, text='UMAC version:', background='white', font=fontBold)
        lbl.grid(column=0, row=4, sticky=tk.W+tk.N)
        self.configTabContent['configDutPar'][dutNr]['umacVerRef'] = ttk.Label(frame, text='', background='white')
        self.configTabContent['configDutPar'][dutNr]['umacVerRef'].grid(column=1, row=4, padx=10, pady=2, sticky=tk.W)

        ToolTip(self.configTabContent['configDutPar'][dutNr]['umacVerRef'], follow_mouse=1, text='The UMAC (SW driver) version of this DUT.')

        lbl = ttk.Label(frame, text='LMAC version:', background='white', font=fontBold)
        lbl.grid(column=0, row=5, sticky=tk.W+tk.N)
        self.configTabContent['configDutPar'][dutNr]['lmacVerRef'] = ttk.Label(frame, text='', background='white')
        self.configTabContent['configDutPar'][dutNr]['lmacVerRef'].grid(column=1, row=5, padx=10, pady=2, sticky=tk.W)

        ToolTip(self.configTabContent['configDutPar'][dutNr]['lmacVerRef'], follow_mouse=1, text='The LMAC (HW) version of this DUT.')

        butFrame = ttk.Frame(frame, style='My.TFrame')
        butFrame.grid(column=1, row=6, sticky=tk.E)
        but = ttk.Button(butFrame, text='Save', command=lambda:self.configTab_setDutConfigValues(dutNr))
        but.grid(column=0, row=0)

        ToolTip(but, follow_mouse=1, text='Save this DUT parameters to the config file.')

        but = ttk.Button(butFrame, text='Delete', command=lambda:self.configTab_deleteDevice(dutNr))
        but.grid(column=1, row=0)

        ToolTip(but, follow_mouse=1, text='Delete this DUT.')

    def configTab_getDutConfigValues(self,dutNr):
        xmlConf = self.configTabContent['configDutPar'][dutNr]['xmlConf']

        self.configTabContent['configDutPar'][dutNr]['idRef'].delete(0, tk.END)
        self.configTabContent['configDutPar'][dutNr]['idRef'].insert(0, xmlConf.get('id'))
        self.configTabContent['configDutPar'][dutNr]['addressRef'].delete(0, tk.END)
        self.configTabContent['configDutPar'][dutNr]['addressRef'].insert(0, xmlConf.get('address'))

        # Check if a COM port was previous selected if so select it in the port dropdown if its still available
        self.configTabContent['configDutPar'][dutNr]['portRef'].configure(values=self.comPortList)
        nrOfComPorts = len(self.configTabContent['configDutPar'][dutNr]['portRef']['values'])
        port = xmlConf.get('port')
        foundPort = False
        if(port != '' ):
            idx = 0
            while( idx < nrOfComPorts ):
                if( self.comPortList[idx] == port ):
                    self.configTabContent['configDutPar'][dutNr]['portRef'].current(idx)
                    foundPort = True
                idx += 1

        if( foundPort == False ):
            # Previous configured port not found take first port in list
            self.configTabContent['configDutPar'][dutNr]['portRef'].current(0)
            self.configTabContent['configDutPar'][dutNr]['port'] = self.configTabContent['configDutPar'][dutNr]['portRef'].get()


    def configTab_setDutConfigValues(self,dutNr):
        address = self.configTabContent['configDutPar'][dutNr]['addressRef'].get()

        reg = '[0-9A-Fa-f]'
        tmp = ''
        for i in range( 16 ):
            tmp = tmp + reg
        tmp += '$'

        reg = re.compile(tmp)
        if( reg.match(address) ):
            dutId = self.configTabContent['configDutPar'][dutNr]['idRef'].get()
            dutIdInt = 0
            try:
                dutIdInt = int(dutId)
            except:
                self.displayPopup('Define Id must be int value ')
                return

            if( dutIdInt < 0 or dutIdInt > 255 ):
                self.displayPopup('Define Id value 0 to 255')
                return

            errorStr = ''

            port = self.configTabContent['configDutPar'][dutNr]['portRef'].get()
            for idx in range(self.configTabContent['nrOfDut']):
                if( dutNr == idx ):
                    # Skip check on self
                    continue
                dut = self.configTabContent['configDutPar'][idx]['xmlConf']
                if( dut.get('id') == str(dutIdInt) ):
                    errorStr = 'Requested Id: ' + str(dutIdInt) + '\nThis Id is used by other DUT.\nThe DUT Id needs to be unique.\n'
                if( dut.get('port') == port and port != '' ):
                    # It is allowed to set Port to ''
                    errorStr += 'Requested Port: ' + self.configTabContent['configDutPar'][dutNr]['port'] + '\nThis Port is used by other DUT.\nFirst deselect Port on the DUT using ' + port

                if( errorStr != '' ):
                    self.displayPopup(errorStr)
                    return

            dut = self.configTabContent['configDutPar'][dutNr]['xmlConf']
            dut.set('id', str(dutIdInt))
            dut.set('port', port)
            dut.set('address', address)

            self.updateConfFile()

            self.configTabContent['configDutPar'][dutNr]['port'] = port
        else:
            self.displayPopup('Define the DUT address 16 hex wide')

    def configTab_getDutPar(self, dutNr):
        # Open COM port with parameters from GUI config file
        dut = self.configTabContent['configDutPar'][dutNr]['xmlConf']

        # Check if DUT has the needed configuration
        dutId = dut.get('id')
        dutPort = dut.get('port')

        if( dutId == '' or dutPort == '' ):
            self.configTabContent['configDutPar'][dutNr]['umacVerRef'].configure(text='-')
            self.configTabContent['configDutPar'][dutNr]['lmacVerRef'].configure(text='-')
            return
        dutId = int(dutId)
        dutAddress = int(dut.get('address'),16)

        DTS_closePort( dutId )
        DTS_openPort( dutId, dutPort, dutAddress )

        # Get umac and lmac version
        DTS_getReleaseInfo( dutId )

        res, ret = DTS_getMsg( dutId, guiTimeout )

        # Close the port
        DTS_closePort( dutId )

        if( res == False ):
            self.configTabContent['configDutPar'][dutNr]['umacVerRef'].configure(text='-')
            self.configTabContent['configDutPar'][dutNr]['lmacVerRef'].configure(text='-')
            errStr = 'No response received from DUT' + str(dutNr+1)
            self.displayPopup(errStr)
            return
        elif( ret['msgId'] != ftdf.DTS_MSG_ID_REL_INFO ):
            self.configTabContent['configDutPar'][dutNr]['umacVerRef'].configure(text='-')
            self.configTabContent['configDutPar'][dutNr]['lmacVerRef'].configure(text='-')
            errStr = 'Expected REL_INFO, instead received ' + msgNameStr[ ret['msgId'] -1 ]
            self.displayPopup(errStr)
            return
        else:
            tempStr = ret['umacRelName'] + '\n' + ret['umacBuildTime']
            self.configTabContent['configDutPar'][dutNr]['umacVerRef'].configure(text=tempStr)
            tempStr = ret['lmacRelName'] + '\n' + ret['lmacBuildTime']
            self.configTabContent['configDutPar'][dutNr]['lmacVerRef'].configure(text=tempStr)

    def configTab_setPortSelVal(self,event,dutNr):
        self.configTab_setDutConfigValues(dutNr)
        self.configTab_getDutPar(dutNr)

    '''
        License Tab functions:
    '''
    def licenseTab_openLink(self):
        root = self.tree.getroot()
        dts = root.find('dts')
        link = dts.find('license').text

        webbrowser.open_new(link)

    def licenseTab_create(self,notebook):
        # frames
        frame = ttk.Frame(notebook, name='license', style='My.TFrame')
        frame.grid(column=0, row=0, sticky=tk.W)

        text = tk.Label(frame, text="License for this application can be viewed online ", background='white', font=fontBold)
        text.grid(column=0, row=0, pady=10, padx=10, sticky=tk.W+tk.N)

        text = tk.Label(frame, text="Link", foreground="#0000ff", background='white')
        text.bind('<1>', lambda event:self.licenseTab_openLink())
        text.grid(column=1, row=0, pady=10, sticky=tk.W+tk.N)

        font = ('TkDefaultFont', 8, 'underline')
        text.configure(font=font)

        notebook.add(frame, text='License', underline=0, padding=2, sticky=tk.N+tk.S+tk.E+tk.W)
        notebook.bind_all("<<NotebookTabChanged>>", self.handleTabChangedEvent) # Event generated when changing tab


app = Application()
app.master.title('Dialog Test Suite')
app.master.protocol("WM_DELETE_WINDOW", DTS_quit)
app.mainloop()
