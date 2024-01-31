#! /usr/bin/env python
####################################################################################################
#
# @name dgtl_demux.py
# @brief
#
# Copyright (C) 2016 Dialog Semiconductor.
# This computer program includes Confidential, Proprietary Information
# of Dialog Semiconductor. All Rights Reserved.
#
####################################################################################################
import argparse
import datetime
import itertools
import logging
import logging.handlers
import platform
import signal
import sys
from threading import Thread, Event
from time import sleep

from api.device import DeviceDescriptor, SerialDeviceBuilder as Builder
from api.router import *
from api.worker import *


class ThreadTerminator(object):
    """ This class checked by threads if they should stop their loops. """
    def __init__(self):
        self.__terminate_evt = Event()

    def trigger(self):
        """ Set the conditional variable to trigger thread's loop break. """
        self.__terminate_evt.set()

    def __nonzero__(self):
        """ Checks the termination condition. """
        return not self.__terminate_evt.is_set()


class MuxThreadRunner(object):
    """ Helper class which allow for spawning mux threads. It creates the endpoint threads and the
    routing thread. Single call to start() function will spawn a routing thread that moves packets
    from inputs to the outputs. There are usually two instances of this class to route messages
    bidirectionally."""
    THREAD_TERMINATE_TIMEOUT = 0.5

    def __init__(self, input_group, output_group, pkt_ind, condition=True, log_callback=None):
        """ Initiate the thread runner instance with the list of input and output endpoints.
        :param input_group: list of input endpoints from which packets are taken from
        :param output_group: lists of output endpoint to which packets are pushed to
        :param pkt_ind: variable used as a packet indicator - set if there is some packet traffic
        :param condition: stop condition
        """
        self.all_threads = []
        self.inputs = input_group
        self.outputs = output_group
        self.condition = condition

        self.pkt_ind = pkt_ind
        self.log_callback = log_callback

    def start(self):
        """ Start the input reader, output writer and routing threads. """
        for endpoint in self.inputs + self.outputs:
            endpoint.open()

        input_threads = [Thread(target=endpoint_read_worker, name='INPUT: %s' % endpoint,
                                args=[endpoint, self.condition])
                         for endpoint in self.inputs if endpoint is not None]

        output_threads = [Thread(target=endpoint_write_worker, name='OUTPUT: %s' % endpoint,
                                 args=[endpoint, self.condition])
                          for endpoint in self.outputs if endpoint is not None]

        router_threads = [Thread(target=message_router, name='Pkt Router: %d --> %d' %
                                                             (len(self.inputs), len(self.outputs)),
                                 args=[self.inputs, self.outputs, self.pkt_ind, self.condition,
                                       self.log_callback])]

        # Launch output threads and input thread after that
        self.all_threads = output_threads + input_threads + router_threads
        for t in self.all_threads:
            # Mark thread as daemon to force killing it if it stuck on a Queue or dev operation
            t.setDaemon(True)
            t.start()

    def join(self):
        """ Join back all threads in a reverse order. Some threads can be unresponsive if blocked
         on a synchronised Queue access or low level device read or write. If thread is not joined
         on time it should die when parent thread is done executing as child threads are set as
         daemon threads. """
        for t in reversed(self.all_threads):
            print('\tTerminating %s' % t)
            t.join(self.THREAD_TERMINATE_TIMEOUT)

        self.all_threads = []

        for endpoint in self.inputs + self.outputs:
            endpoint.close()

    @classmethod
    def execute_duplex_router(cls, group1, group2, log=None):
        """ Creates two MuxThreadRunner instances for the bidirectional packet routing. All packets
         are routed from inputs to the outputs in a single MuxThreadRunner instance. If a single
         device is bidirectional device then two endpoints are created for it - input and output
         endpoint. Usually it's input endpoint is used in one of the MuxThreadRunner instances and
         it's output endpoint in the second one. It can be considered as two separated groups in
         which messages from inputs are sent to the outputs. This way of grouping ensures that
         packets from one device will not be routed to the same device (as it often accepts the
         same set of packet types types it is sending).

         If more complicated groupings or mutual exclusions are needed, more complex router with
         more than 2 groups can be created. It's even possible to have one device in multiple groups
         and it should work fine for the output endpoints but two routing threads consuming a
         single queue from the input endpoint will race for available packets and this will lead to
         communication errors.
         """

        terminator = ThreadTerminator()
        pkt_sync = Event()

        # Create device endpoints - list of (in, out) tuples - one for each device
        group1_endpoints = list(Builder.create_endpoints(group1))
        group2_endpoints = list(Builder.create_endpoints(group2))

        # Extract input and output endpoints
        demux_inputs, mux_outputs = zip(*group1_endpoints)
        mux_inputs, demux_outputs = zip(*group2_endpoints)

        print('Launching DGTL Multiplexer.')

        bar_size = 70

        # noinspection PyUnusedLocal
        def log_callback(i, o, pkt):
            log.debug(('/{:-^%d}\\' % (bar_size - 3)).format('| ' + str(datetime.datetime.utcnow()) + ' |'))
            log.debug(pkt)
            log.debug('\t' + 30 * '-')
            log.debug('\t Destination > %s' % o)
            log.debug('\\' + '-' * (bar_size - 3) + '/')

        # De-multiplexing part
        demux = cls(demux_inputs, demux_outputs, pkt_sync, terminator,
                    log_callback if log else None)
        demux.start()

        # Multiplexing part
        mux = cls(mux_inputs, mux_outputs, pkt_sync, terminator,
                  log_callback if log else None)
        mux.start()

        # noinspection PyUnusedLocal
        # User interrupt handler
        def stop_handler(sig, frame):
            """ Signal handler which initiates the threads stopping sequence. """
            print('\nPlease wait while DGTL Demultiplexer terminates...')
            terminator.trigger()

            mux.join()
            demux.join()

            print('Done.')
            sys.exit(0)

        signal.signal(signal.SIGINT, stop_handler)
        signal.signal(signal.SIGCONT, stop_handler)

        # Display the work indicator spinner when logs are disabled.
        if not log:
            cursor = itertools.cycle(['|', '/', '-', '\\'])

            # Check for user interrupts and show work status indicator
            while True:
                # Update the spinner state if packet traffic was detected.
                if pkt_sync.wait(0.5):
                    sys.stdout.write('\r')
                    sys.stdout.write(cursor.next())
                    sys.stdout.flush()
                    pkt_sync.clear()
                    # Don't update it often than twice a second.
                    sleep(0.5)
        else:
            while True:
                sleep(0.5)


def parse_cli_arguments():
    try:
        default_phy_port = {'Windows': "'COM'", 'Linux': "'/dev/ttyUSB0'"}[platform.system()]
        default_virt_port = {'Windows': "'NULL Modem emulator'", 'Linux': "'/dev/pts/0'"}[
            platform.system()]
    except KeyError:
        raise OSError("Unsupported OS platform: %s" % platform.system())

    parser = argparse.ArgumentParser(description='DGTL Mux')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                        help='log verbosity')
    parser.add_argument('--phy', required=True,
                        help=' '.join(['physical interface like', default_phy_port, 'etc']))
    parser.add_argument('--app_ch',
                        help=' '.join(['virtual interface for application channel like',
                                       default_virt_port, 'etc']))
    parser.add_argument('--hci_ch', help=' '.join(['virtual interface for HCI/GTL channel like',
                                                   default_virt_port, 'etc']))
    parser.add_argument('--log_ch', help=' '.join(['virtual interface for logging channel like',
                                                   default_virt_port, 'etc']))
    parser.add_argument('--baudrate', default=115200)

    # Parse logging setup
    log_group = parser.add_argument_group('logging file parameters')
    log_group.add_argument('--log', dest='logfile', help='log data to file')
    log_group.add_argument('--size', default=100, help='size of created logfile in KB')
    log_group.add_argument('--number', default=1000, help='number of rotating logfiles to create')

    arg = parser.parse_args()

    # Check for any virtual port
    if not (arg.app_ch or arg.hci_ch or arg.log_ch):
        parser.print_help()
        sleep(0.3)
        raise EnvironmentError("No virtual ports are given!")

    return arg


def prepare_logger(arg):
    # Create packet logging
    pkt_log = logging.getLogger('Packet log')
    pkt_log.setLevel(logging.DEBUG)

    # Create packet logging format (message)
    log_pkt_format = logging.Formatter('%(message)s')

    # Create console handler and set level (if verbose is selected)
    if arg.verbose:
        ch_pkt = logging.StreamHandler()
        ch_pkt.setLevel(logging.DEBUG)

        ch_pkt.setFormatter(log_pkt_format)

        # Add ch_pkt to pkt_log
        pkt_log.addHandler(ch_pkt)

    if arg.logfile:
        max_bytes = 1024 * args.size
        backup_count = args.number
        file_handler_pkt = logging.handlers.RotatingFileHandler(args.logfile,
                                                                maxBytes=max_bytes,
                                                                backupCount=backup_count)

        file_handler_pkt.setFormatter(log_pkt_format)
        pkt_log.addHandler(file_handler_pkt)

    return pkt_log


if __name__ == '__main__':
    # This example show how devices can configured and used by the router instances for a
    # bidirectional packet routing. In this example there is just one real hardware platform
    # connected on one of the COM ports. The second Virtual COM port is used by the host app
    # (e.g 3VT). The communication between the hardware platform and the host app is routed through
    # the running router instances and can be monitored.
    #
    # On Linux user can create a pair of virtual ports with:
    # $ socat -d -d pty,raw,echo=0,b115200,crtscts=0, pty,raw,echo=0,b115200
    # One is used by the router and the second one is acting like the other end of the pipe and
    # should be used by host system application.
    #
    # On Windows, an external application (null modem emulator) should be used.
    args = parse_cli_arguments()

    default_phy_device_channels = [DGTL.PKT_TYPE_HCICMD,
                                   DGTL.PKT_TYPE_HCIACL,
                                   DGTL.PKT_TYPE_HCISCO,
                                   DGTL.PKT_TYPE_HCIEVT,
                                   DGTL.PKT_TYPE_GTL,
                                   DGTL.PKT_TYPE_APP_H2T,
                                   DGTL.PKT_TYPE_APP_T2H,
                                   DGTL.PKT_TYPE_LOG]
    physical_devices = []
    virtual_devices = []

    # Physical device interface descriptor working on all packet type (application/ HCI/GTL, logging)
    if args.phy:
        physical_devices.append(DeviceDescriptor(device_str=args.phy,
                                                 input_channels=default_phy_device_channels,
                                                 output_channels=default_phy_device_channels,
                                                 baudrate=args.baudrate))

    # Virtual device interface descriptor for application packet type
    if args.app_ch:
        virtual_devices.append(DeviceDescriptor(device_str=args.app_ch,
                                                input_channels=[DGTL.PKT_TYPE_APP_H2T,
                                                                DGTL.PKT_TYPE_APP_T2H],
                                                output_channels=[DGTL.PKT_TYPE_APP_H2T,
                                                                 DGTL.PKT_TYPE_APP_T2H],
                                                rtscts=True,
                                                dsrdtr=True,
                                                baudrate=args.baudrate))

    # Virtual device interface descriptor for HCI/GTL packet type
    if args.hci_ch:
        virtual_devices.append(DeviceDescriptor(device_str=args.hci_ch,
                                                input_channels=[DGTL.PKT_TYPE_HCICMD,
                                                                DGTL.PKT_TYPE_HCIACL,
                                                                DGTL.PKT_TYPE_HCISCO,
                                                                DGTL.PKT_TYPE_HCIEVT,
                                                                DGTL.PKT_TYPE_GTL],
                                                output_channels=[DGTL.PKT_TYPE_HCICMD,
                                                                 DGTL.PKT_TYPE_HCIACL,
                                                                 DGTL.PKT_TYPE_HCISCO,
                                                                 DGTL.PKT_TYPE_HCIEVT,
                                                                 DGTL.PKT_TYPE_GTL],
                                                rtscts=True,
                                                dsrdtr=True,
                                                baudrate=args.baudrate))

    # Virtual device interface descriptor logging packet type
    if args.log_ch:
        virtual_devices.append(DeviceDescriptor(device_str=args.log_ch,
                                                input_channels=[DGTL.PKT_TYPE_LOG],
                                                output_channels=[DGTL.PKT_TYPE_LOG],
                                                rtscts=True,
                                                dsrdtr=True,
                                                baudrate=args.baudrate))

    logger = prepare_logger(args)

    MuxThreadRunner.execute_duplex_router(physical_devices, virtual_devices, logger)
