####################################################################################################
#
# @name endpoint.py
# @brief
#
# Copyright (C) 2016 Dialog Semiconductor.
# This computer program includes Confidential, Proprietary Information
# of Dialog Semiconductor. All Rights Reserved.
#
####################################################################################################
import struct

from api import protocol
from filter import apply_filters
from protocol import DGTL


def endpoint_read_worker(endpoint, condition=True):
    """ Function run by a Thread for the input device endpoint. It just reads the raw data, forms
     packets and pushes them on it's packet queue. The external routing entity should take care of
     the packet queue and consume it. It can be considered as one of the producers thread.

    :param endpoint: Input device endpoint to read the raw data from
    :param condition: External condition. Function will not return till it's met.
    :return:
    """

    def __synchronise():
        """ Simple function to match the first whole packet and synchronise. It just drops each byte
         if it's not a packet indicator. It's really primitive at this stage. """
        # FIXME: We should match some pattern rather than single byte
        ch = endpoint.read()
        while not ch or ord(ch) not in DGTL.descriptors.keys():
            ch = endpoint.read()

        return ch

    # Read packet indicator
    msg = __synchronise()

    # Assemble data slices into non-fragmented packets
    while condition:
        # Read the minimum amount of data to get packet length
        try:
            hdr_size, fmt, _ = DGTL.descriptors[struct.unpack('<B', msg)[0]]
            msg += endpoint.read(hdr_size)

            # Extract packet length from the header
            pkt_len = struct.unpack(fmt, msg)[-1]

            # Read the whole message and queue it for the router to handle
            msg += endpoint.read(pkt_len)
            endpoint.message_put(
                protocol.Pkt.packetize(endpoint, apply_filters(msg, *endpoint.get_input_filters())))

            # Read next packet indicator
            msg = endpoint.read()
        except KeyError:
            print("Synchronisation error.")
            msg = __synchronise()


def endpoint_write_worker(endpoint, condition):
    """ Function run by a Thread for the output device endpoint. It consumes the packet queue and
     writes raw data to the low level device. The external routing entity will take care of the
     packet queue and fill it with packets routed from other devices. It can be considered as one
     of the consumers thread.

    :param endpoint: Output device endpoint to write to
    :param condition: External condition. Function will not return till it's met.
    """
    while condition:
        msg = endpoint.message_get(block=True)
        endpoint.write(apply_filters(msg.raw_data, *endpoint.get_output_filters()))
