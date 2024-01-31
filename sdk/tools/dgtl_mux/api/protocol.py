####################################################################################################
#
# @name protocol.py
# @brief
#
# Copyright (C) 2016 Dialog Semiconductor.
# This computer program includes Confidential, Proprietary Information
# of Dialog Semiconductor. All Rights Reserved.
#
####################################################################################################
#
# Protocol message format:
#     0                7 8
#    |------------------|--------|
#    | packet_indicator | packet |
#    |------------------|--------|
#
# Packet's header needs to be read to determine packet's full size:
#  * Command packet (0x01):
#     0      15 16          23 24
#    |---------|--------------|--------------
#    | op-code | total_length | Param_0 ...
#    |---------|--------------|---------
#
#  * ACL packet (0x02):
#     0     11 12    13  14     15 16          31 32
#    |--------|---------|---------|--------------|-----------
#    | handle | pb_flag | bc_flag | total_length | Data ...
#    |--------|---------|---------|--------------|------
#
#  * SCO data (0x03):
#     0                11 12    13  14     15 16          23 24
#    |-------------------|--------|----------|--------------|-----------
#    | connection_handle | status | reserved | total_length | Data ...
#    |-------------------|--------|----------|--------------|------
#
#  * Event packet (0x03):
#     0          7 8           15 16
#    |------------|--------------|--------------
#    | event_code | total_length | Param 0 ...
#    |------------|--------------|---------
#
#  * GTL packet (0x05):
#     0         15 16 31 32 48 64    79 80
#    |------------|-----|-----|--------|-----------
#    | message_id | dst | src | length | Data ...
#    |------------|-----|-----|--------|------
#
#  * APP Host to Target packet (0x06):
#     0      15 16          31 32
#    |---------|--------------|--------------
#    | op-code | total_length | Param_0 ...
#    |---------|--------------|---------
#
#  * APP  Target to Host packet (0x07):
#     0      15 16          31 32
#    |---------|--------------|--------------
#    | op-code | total_length | Param_0 ...
#    |---------|--------------|---------
#
#  * LOG packet (0x08):
#     0      7 16
#    |--------|-------------
#    | length | params ...
#    |--------|--------
import struct


class Pkt(object):
    """ Wraps the raw data to easy the packet identification, routing process, etc. """

    def __init__(self, source, raw_data):
        self.source = source
        self.raw_data = raw_data
        self.decoded = None

    def set_decoder(self, decoder):
        """ Pulls in all decoder properties. When set - we can easily read all known fields of
         a particular packet type. Can be used for real-time logging. """
        self.decoded = decoder(self)

    @property
    def type(self):
        """ Access the packet indicator field - first byte. """
        return struct.unpack('<B', self.raw_data[0])[0]

    @property
    def payload(self):
        """ Access the raw data after the packet indicator field. """
        return self.raw_data[1:]

    @classmethod
    def packetize(cls, source, raw_data):
        """ Wraps the raw data within a Pkt class instance. Helper function. """
        pkt = cls(source, raw_data)

        if pkt.type not in DGTL.descriptors.keys():
            raise Warning('Unsupported packet type! (%s)' % pkt.type)

        pkt.set_decoder(DGTL.descriptors[pkt.type][2])

        return pkt

    def __repr__(self):
        return self.raw_data

    def __str__(self):
        """ High level string representation of the packet. It decodes directly just the packet
         type and the source of it. Packet's content decoding is left to the decoder. """
        return '\n%(source)s > %(type)s (0x%(type_d).2x)\n%(data)s' % \
               {'type': DGTL.pkt_type_str[self.type], 'type_d': self.type,
                'data': str(self.decoded) if self.decoded else 'Unknown raw data.',
                'source': self.source}


class DGTL_Decoder(object):
    """ A base class for all packet decoders """

    # raw data is sliced into chunks for print - number of bytes in a chunk
    __raw_data_chunk = 16

    def __init__(self, pkt):
        """ Initiates the decoder.
        :param pkt: packet on which all decoder properties are mapped
        """
        self.pkt = pkt

    def __str__(self):
        """ String representation of the decoded packet. """
        return '\tNo readable data representation.'

    @staticmethod
    def format_raw_data(data, indent=2*'\t'):
        """ Helper function for raw data formatting. """
        strings = [' '.join([('%.2x' % ord(x)) for x in data[i:i + DGTL_Decoder.__raw_data_chunk]])
                   for i in xrange(0, len(data), DGTL_Decoder.__raw_data_chunk)]
        return ('\n' + indent).join(strings)


class DGTL_HCICMD_Decoder(DGTL_Decoder):
    """ HCI command packet decoder """

    @property
    def opcode(self):
        """ Returns the opcode field """
        return struct.unpack('<H', self.pkt.payload[0:2])[0]

    @property
    def length(self):
        """ Returns the length field """
        return struct.unpack('<B', self.pkt.payload[2:3])[0]

    @property
    def parameters(self):
        """ Returns the parameters field """
        return self.pkt.payload[3:]

    def __str__(self):
        """ String representation of the decoded packet. """
        return '\tOpcode: %(opcode)d (0x%(opcode).2x)\n' \
               '\tLength: %(length)d (0x%(length).2x)\n' \
               '\tParameters:\n' \
               '\t\t%(data)s' % {'opcode': self.opcode, 'length': self.length,
                                 'data': self.format_raw_data(self.parameters)}


class DGTL_HCIACL_Decoder(DGTL_Decoder):
    @property
    def handle(self):
        """ Returns the handle field """
        return struct.unpack('<H', self.pkt.payload[0:2])[0]

    @property
    def length(self):
        """ Returns the length field """
        return struct.unpack('<H', self.pkt.payload[2:4])[0]

    @property
    def parameters(self):
        """ Returns the parameters field """
        return self.pkt.payload[3:]

    def __str__(self):
        """ String representation of the decoded packet. """
        return '\tHandle: %(handle)d (0x%(handle).2x)\n' \
               '\tLength: %(length)d (0x%(length).2x)\n' \
               '\tParameters:\n' \
               '\t\t%(data)s' % {'handle': self.handle, 'length': self.length,
                                 'data': self.format_raw_data(self.parameters)}

class DGTL_HCISCO_Decoder(DGTL_Decoder):
    @property
    def handle(self):
        """ Returns the handle field """
        return struct.unpack('<H', self.pkt.payload[0:2])[0]

    @property
    def length(self):
        """ Returns the length field """
        return struct.unpack('<B', self.pkt.payload[2:3])[0]

    @property
    def parameters(self):
        """ Returns the parameters field """
        return self.pkt.payload[3:]

    def __str__(self):
        """ String representation of the decoded packet. """
        return '\tHandle: %(handle)d (0x%(handle).2x)\n' \
               '\tLength: %(length)d (0x%(length).2x)\n' \
               '\tParameters:\n' \
               '\t\t%(data)s' % {'handle': self.handle, 'length': self.length,
                                 'data': self.format_raw_data(self.parameters)}


class DGTL_HCIEVT_Decoder(DGTL_Decoder):
    @property
    def code(self):
        """ Returns the code field """
        return struct.unpack('<B', self.pkt.payload[0:1])[0]

    @property
    def length(self):
        """ Returns the length field """
        return struct.unpack('<B', self.pkt.payload[1:2])[0]

    @property
    def parameters(self):
        """ Returns the parameters field """
        return self.pkt.payload[2:]

    def __str__(self):
        """ String representation of the decoded packet. """
        return '\tCode: %(code)d (0x%(code).2x)\n' \
               '\tLength: %(length)d (0x%(length).2x)\n' \
               '\tParameters:\n' \
               '\t\t%(data)s' % {'code': self.code, 'length': self.length,
                                 'data': self.format_raw_data(self.parameters)}


class DGTL_GTL_Decoder(DGTL_Decoder):
    @property
    def msg_id(self):
        """ Returns the Message ID field """
        return struct.unpack('<H', self.pkt.payload[0:2])[0]

    @property
    def dst_task_id(self):
        """ Returns the Destination Task ID field """
        return struct.unpack('<H', self.pkt.payload[2:4])[0]

    @property
    def src_task_id(self):
        """ Returns the Source Task ID field """
        return struct.unpack('<H', self.pkt.payload[4:6])[0]

    @property
    def length(self):
        """ Returns the length field """
        return struct.unpack('<H', self.pkt.payload[6:8])[0]

    @property
    def parameters(self):
        """ Returns the parameters field """
        return self.pkt.payload[8:]

    def __str__(self):
        """ String representation of the decoded packet. """
        return '\tMsg ID: %(msg_id)d (0x%(msg_id).4x)\n' \
               '\tSrc. task ID: %(src_task_id)d (0x%(src_task_id).4x)\n' \
               '\tDst. task ID: %(dst_task_id)d (0x%(dst_task_id).4x)\n' \
               '\tLength: %(length)d (0x%(length).4x)\n' \
               '\tParameters:\n' \
               '\t\t%(data)s' % {'msg_id': self.msg_id, 'length': self.length,
                                                'dst_task_id': self.dst_task_id,
                                                'src_task_id': self.src_task_id,
                                                'data': self.format_raw_data(self.parameters)}


class DGTL_APP_Decoder(DGTL_Decoder):
    # TODO: implement properties for this packet
    pass


class DGTL_LOG_Decoder(DGTL_Decoder):
    # TODO: implement properties for this packet
    pass


class DGTL(object):
    """ Set of defines needed for identifying and packetising the incoming data. """

    # Standard HCI packet indicators
    PKT_TYPE_HCICMD = 0x01
    PKT_TYPE_HCIACL = 0x02
    PKT_TYPE_HCISCO = 0x03
    PKT_TYPE_HCIEVT = 0x04

    # Custom packet indicators
    PKT_TYPE_GTL = 0x05
    PKT_TYPE_APP_H2T = 0x06
    PKT_TYPE_APP_T2H = 0x07
    PKT_TYPE_LOG = 0x08

    # Pretty names for packet types
    pkt_type_str = {
        PKT_TYPE_HCICMD:  'HCI Command',
        PKT_TYPE_HCIACL:  'HCI ACL',
        PKT_TYPE_HCISCO:  'HCI SCO',
        PKT_TYPE_HCIEVT:  'HCI Event',
        PKT_TYPE_GTL:     'GTL',
        PKT_TYPE_APP_H2T: 'APP Host to Target',
        PKT_TYPE_APP_T2H: 'APP Target to Host',
        PKT_TYPE_LOG:     'LOG',
    }

    # Packet header descriptors used for packet slicing purpose - encodes the position of length
    # field inside the raw data buffer and a recipe on how to extract it from a raw data buffer.
    # It also holds the decoder class used to decode the packet.
    descriptors = {
        PKT_TYPE_HCICMD:  (3, '<BHB', DGTL_HCICMD_Decoder),
        PKT_TYPE_HCIACL:  (4, '<BHH', DGTL_HCIACL_Decoder),
        PKT_TYPE_HCISCO:  (3, '<BHB', DGTL_HCISCO_Decoder),
        PKT_TYPE_HCIEVT:  (2, '<BBB', DGTL_HCIEVT_Decoder),
        PKT_TYPE_GTL:     (8, '<BHHHH', DGTL_GTL_Decoder),
        PKT_TYPE_APP_H2T: (4, '<BHH', DGTL_APP_Decoder),
        PKT_TYPE_APP_T2H: (4, '<BHH', DGTL_APP_Decoder),
        PKT_TYPE_LOG:     (1, '<BB', DGTL_LOG_Decoder),
    }
