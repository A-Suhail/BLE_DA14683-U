####################################################################################################
#
# @name router.py
# @brief
#
# Copyright (C) 2016 Dialog Semiconductor.
# This computer program includes Confidential, Proprietary Information
# of Dialog Semiconductor. All Rights Reserved.
#
####################################################################################################
import Queue

ENDPOINT_CHECK_LATENCY = 0.001


def message_router(inputs, outputs, pkt_ind, condition=True, log_callback=None):
    """ Read from input's queue and distributes packets to the output's queue. This function will
    be used by a Thread to continuously move packets from source device to destination devices.
    Message is delivered to the first device on a list which claims to support this particular
    packet type. If two devices claim to support the same packet type only the first one will
    receive it, as no packet cloning is done.

    :param inputs: list of input endpoints to get the messages from
    :param outputs: list of outputs to push the messages to
    :param pkt_ind: variable used as a packet indicator - set if there is some packet traffic
    :param condition: thread working condition - simple boolean can be used or synchronised
    threading event
    """
    while condition:
        timeout = ENDPOINT_CHECK_LATENCY if len(inputs) > 1 else None

        # Read from inputs in a round robin pattern and distribute packets.
        for i in inputs:
            try:
                pkt = i.message_get(block=True, timeout=timeout)

                # Do the message routing.
                for o in outputs:
                    if pkt.type in o.get_supported_output_channels():
                        o.message_put(pkt)

                        if log_callback is not None:
                            log_callback(i, o, pkt)

                        break

            except Queue.Empty:
                # Go to the next input endpoint.
                continue

            # Check the external condition if process termination is expected.
            if not condition:
                break

            pkt_ind.set()
