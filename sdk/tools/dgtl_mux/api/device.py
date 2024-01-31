####################################################################################################
#
# @name device.py
# @brief
#
# Copyright (C) 2016 Dialog Semiconductor.
# This computer program includes Confidential, Proprietary Information
# of Dialog Semiconductor. All Rights Reserved.
#
####################################################################################################

from Queue import Queue
from serial import serial_for_url


class DeviceDescriptor(object):
    """ This object represents the physical or virtual device and describe it's low level interface
    (COM port and it's parameters) as well as a list of supported message types which the device
    can send or receive. Additional filter lists allows for data processing upon send or receive.
    Those filter's can detect, decode or encode some packets if needed and are optional. """
    def __init__(self, device_str, input_channels=None, output_channels=None, input_filters=None,
                 output_filters=None, **opts):
        """ Initiates the Device descriptor.

        :param device_str: Device string used later to identify and open the low level device
        :param input_channels: List of packet channels which are expected on read operation
        :param output_channels: List of packet channels which are accepted on write operation
        :param input_filters: Filters applied just after the raw data is read from the device
        :param output_filters: Filters applied just before the packet is written to a device
        :param opts: Additional parameters required by the low level device creation facility
        """
        self.device_str = device_str
        self.input_channels = input_channels if input_channels else []
        self.output_channels = output_channels if output_channels else []
        self.input_filters = input_filters if input_filters else []
        self.output_filters = output_filters if output_filters else []
        self.opts = opts

    def __str__(self):
        """ String representation of the Device Descriptor. """
        return self.device_str

    def __repr__(self):
        """ More verbose representation of the descriptor internals. """
        return 'Device: %s, Supported Channels: %s, Active Filters: %s' % \
               (self.device_str, self.input_channels, self.input_filters)


class DeviceEndpoint(object):
    """ This class wraps the low level Serial device along with a buffer where all data is stored
    in the form of complete packets after it's read from the low level device or just before it's
    written to it. It's the main entity that the routing module interacts with. It also holds the
    device descriptor for the device it is connected to. Usually for each device there are two
    endpoint: the input endpoint which represents the packet source and the output endpoint
    representing the packet destination. Packets are always routed from the input to the output
    endpoints. If device is one-directional (it's descriptor has an empty input or output channel
    list) it will have just a single endpoint.
    """
    def __init__(self, descriptor, device):
        """ Initiates the endpoint object.

        :param descriptor: Device descriptor for which the endpoint is created
        :param device: Low level device with basic read and write API calls
        """
        self.device_descriptor = descriptor

        # low level device
        self.ll_device = device

        # main buffer to write to or read from
        self.buffer = Queue()

    def open(self):
        """ Opens the endpoint for reading or writing. """
        if not self.ll_device.isOpen():
            self.ll_device.open()

            print('Opening endpoint %s' % self.device_descriptor.device_str)

    def close(self):
        """ Closes the endpoint. """
        if self.ll_device.isOpen():
            self.ll_device.close()

    def read(self, size=1):
        return NotImplemented

    def write(self, data):
        return NotImplemented

    def message_put(self, msg, block=True, timeout=None):
        """ Adds a packet into the endpoints packet queue. This is usually called by the reading
        thread when packets are formed from the raw data read from the low level device.
        :param msg: packet message to put in a queue
        :param block: if call should block and wait in case of concurrent access
        :param timeout: timeout parameter for the block functionality
        """
        if msg:
            return self.buffer.put(msg, block=block, timeout=timeout)

    def message_get(self, block=False, timeout=None):
        """ Takes the message packet out of the buffer. This is usually called by the output
        endpoint while consuming the packets and pushing them into the low level device.
        :param block: if call should block and wait in case of concurrent access
        :param timeout: timeout parameter for the block functionality
        """
        return self.buffer.get(block=block, timeout=timeout)

    def get_supported_input_channels(self):
        """ Get the list of support input channels (packet type indicators) """
        return self.device_descriptor.input_channels

    def get_supported_output_channels(self):
        """ Get the list of support input channels (packet type indicators) """
        return self.device_descriptor.output_channels

    def get_input_filters(self):
        """ Get the list of input filters. """
        return self.device_descriptor.input_filters

    def get_output_filters(self):
        """ Get the list of output filters. """
        return self.device_descriptor.output_filters

    def __str__(self):
        """ String representing the endpoint object. Used for logging. """
        return str('%s' % self.device_descriptor)

    def __repr__(self):
        """ More verbose representation of endpoint's internals. """
        return str('%s: %s' % (self.__class__.__name__, repr(self.device_descriptor)))


class InputDeviceEndpoint(DeviceEndpoint):
    """ Extends the base class with read capability. """
    def read(self, size=1):
        """ Reads the requested amount of data from low level device object.

        :param size: The amount of data to read
        :return: The amount of data that has bean read
        """
        return self.ll_device.read(size)


class OutputDeviceEndpoint(DeviceEndpoint):
    """ Extends the base class with write capability. """
    def write(self, data):
        """ Writes data into the low level device.

        :param data: data buffer to be written
        """
        self.ll_device.write(data)
        self.ll_device.flush()


class SerialDeviceBuilder(object):
    """ Serial device endpoint builder. It creates a low level device object for the COM port
    (Real or Virtual/Pseudo-terminal). """

    @staticmethod
    def create_endpoints(descriptors):
        """ Creates device endpoints from the list of given device descriptors. Pair of endpoints
        is created for each device if it's bidirectional (non empty input and output channel list)
        or just one endpoint if one of the channel lists is empty.

        :param descriptors: List of device descriptors for which endpoints will be created.
        """
        for descriptor in descriptors:
            ll_device = create_ll_device(serial_for_url, descriptor.device_str, do_not_open=True,
                                         timeout=None, **descriptor.opts)

            i_desc = InputDeviceEndpoint(descriptor, ll_device) if descriptor.input_channels \
                else None
            o_desc = OutputDeviceEndpoint(descriptor, ll_device) if descriptor.output_channels \
                else None

            yield i_desc, o_desc


def create_ll_device(device_builder, *args, **kwargs):
    """ Helper function to call different device builders. """
    return device_builder(*args, **kwargs)
