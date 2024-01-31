import ftdf

from inspect import currentframe

def lineNr():
    cf = currentframe()
    return cf.f_back.f_lineno

responseTimeout = 10
# Whether we test with FPGA/CC2420 platform or not
targetFPGA = 0

# FPPR entries 
fpprEntries = 24

maxExtAddresses = fpprEntries

maxShortAddresses = fpprEntries * 4

maxBuffers = maxShortAddresses

#Device Id's
devId1 = 1
devId2 = 2
devId3 = 3


# Messages
msgRESET = { 'msgId': ftdf.FTDF_RESET_REQUEST,
             'setDefaultPIB': True }

msgSet = { 'msgId': ftdf.FTDF_SET_REQUEST,
           'PIBAttribute': 1,
           'PIBAttributeValue': 0x0000 }

msgGet = { 'msgId': ftdf.FTDF_GET_REQUEST,
           'PIBAttribute': 0 }

msgSET_PANId = { 'msgId': ftdf.FTDF_SET_REQUEST,
                 'PIBAttribute': ftdf.FTDF_PIB_PAN_ID,
                 'PIBAttributeValue': 0x0001 }

msgSET_Dev1_ShortAddress = { 'msgId': ftdf.FTDF_SET_REQUEST,
                             'PIBAttribute': ftdf.FTDF_PIB_SHORT_ADDRESS,
                             'PIBAttributeValue': 0x0010 }

msgSET_Dev2_ShortAddress = { 'msgId': ftdf.FTDF_SET_REQUEST,
                             'PIBAttribute': ftdf.FTDF_PIB_SHORT_ADDRESS,
                             'PIBAttributeValue': 0x0020 }

msgSET_Dev3_ShortAddress = { 'msgId': ftdf.FTDF_SET_REQUEST,
                             'PIBAttribute': ftdf.FTDF_PIB_SHORT_ADDRESS,
                             'PIBAttributeValue': 0x0030 }

msgSET_Dev1_ExtendedAddress = { 'msgId': ftdf.FTDF_SET_REQUEST,
                                'PIBAttribute': ftdf.FTDF_PIB_EXTENDED_ADDRESS,
                                'PIBAttributeValue': 0x0000000000000010 }

msgSET_Dev2_ExtendedAddress = { 'msgId': ftdf.FTDF_SET_REQUEST,
                                'PIBAttribute': ftdf.FTDF_PIB_EXTENDED_ADDRESS,
                                'PIBAttributeValue': 0x0000000000000020 }

msgSET_Dev3_ExtendedAddress = { 'msgId': ftdf.FTDF_SET_REQUEST,
                                'PIBAttribute': ftdf.FTDF_PIB_EXTENDED_ADDRESS,
                                'PIBAttributeValue': 0x0000000000000030 }

msgSET_DSN = { 'msgId': ftdf.FTDF_SET_REQUEST,
               'PIBAttribute': ftdf.FTDF_PIB_DSN,
               'PIBAttributeValue': 119 }

msgSET_MAX_CSMA_BACKOFFS_0 = { 'msgId': ftdf.FTDF_SET_REQUEST,
               'PIBAttribute': ftdf.FTDF_PIB_MAX_CSMA_BACKOFFS,
               'PIBAttributeValue': 5 }

msgRxEnable_On = { 'msgId': ftdf.FTDF_RX_ENABLE_REQUEST,
                   'deferPermit': False,
                   'rxOnTime': 0,
                   'rxOnDuration':0xffffff }

msgRxEnable_Off = { 'msgId': ftdf.FTDF_RX_ENABLE_REQUEST,
                    'deferPermit': False,
                    'rxOnTime': 0,
                    'rxOnDuration':0x000000 }


# Defines as string
resultStr = [
    'SUCCESS',
    'CHANNEL_ACCESS_FAILURE',
    'NO_ACK',
    'NO_DATA',
    'COUNTER_ERROR',
    'FRAME_TOO_LONG',
    'IMPROPER_KEY_TYPE',
    'IMPROPER_SECURITY_LEVEL',
    'SECURITY_ERROR',
    'UNAVAILABLE_KEY',
    'UNAVAILABLE_DEVICE',
    'UNAVAILABLE_SECURITY_LEVEL',
    'UNSUPPORTED_LEGACY',
    'UNSUPPORTED_SECURITY',
    'INVALID_PARAMETER',
    'TRANSACTION_OVERFLOW',
    'TRANSACTION_EXPIRED',
    'ON_TIME_TOO_LONG',
    'LIMIT_REACHED',
    'NO_BEACON',
    'SCAN_IN_PROGRESS',
    'INVALID_INDEX',
    'NO_SHORT_ADDRESS',
    'SUPERFRAME_OVERLAP',
    'TRACKING_OFF',
    'SLOTFRAME_NOT_FOUND',
    'MAX_SLOTFRAMES_EXCEEDED',
    'UNKNOWN_LINK',
    'MAX_LINKS_EXCEEDED',
    'UNSUPPORTED_ATTRIBUTE',
    'READ_ONLY',
    'INVALID_HANDLE',
    'PAN_AT_CAPACITY',
    'PAN_ACCESS_DENIED',
    'HOPPING_SEQUENCE_OFFSET_DUPLICATION'
]

msgNameStr = [
    'DATA_REQUEST',
    'DATA_INDICATION',
    'DATA_CONFIRM',
    'PURGE_REQUEST',
    'PURGE_CONFIRM',
    'ASSOCIATE_REQUEST',
    'ASSOCIATE_INDICATION',
    'ASSOCIATE_RESPONSE',
    'ASSOCIATE_CONFIRM',
    'DISASSOCIATE_REQUEST',
    'DISASSOCIATE_INDICATION',
    'DISASSOCIATE_CONFIRM',
    'BEACON_NOTIFY_INDICATION',
    'COMM_STATUS_INDICATION',
    'GET_REQUEST',
    'GET_CONFIRM',
    'SET_REQUEST',
    'SET_CONFIRM',
    'GTS_REQUEST',
    'GTS_CONFIRM',
    'GTS_INDICATION',
    'ORPHAN_INDICATION',
    'ORPHAN_RESPONSE',
    'RESET_REQUEST',
    'RESET_CONFIRM',
    'RX_ENABLE_REQUEST',
    'RX_ENABLE_CONFIRM',
    'SCAN_REQUEST',
    'SCAN_CONFIRM',
    'START_REQUEST',
    'START_CONFIRM',
    'SYNC_REQUEST',
    'SYNC_LOSS_INDICATION',
    'POLL_REQUEST',
    'POLL_CONFIRM',
    'SET_SLOTFRAME_REQUEST',
    'SET_SLOTFRAME_CONFIRM',
    'SET_LINK_REQUEST',
    'SET_LINK_CONFIRM',
    'TSCH_MODE_REQUEST',
    'TSCH_MODE_CONFIRM',
    'KEEP_ALIVE_REQUEST',
    'KEEP_ALIVE_CONFIRM',
    'BEACON_REQUEST',
    'BEACON_CONFIRM',
    'BEACON_REQUEST_INDICATION',
    'TRANSPARENT_CONFIRM',
    'TRANSPARENT_INDICATION',
    'TRANSPARENT_REQUEST',
    'REMOTE_REQUEST'
]

pibAttributeStr = [
    'EXTENDED_ADDRESS',
    'ACK_WAIT_DURATION',
    'ASSOCIATION_PAN_COORD',
    'ASSOCIATION_PERMIT',
    'AUTO_REQUEST',
    'BATT_LIFE_EXT',
    'BATT_LIFE_EXT_PERIODS',
    'BEACON_PAYLOAD',
    'BEACON_PAYLOAD_LENGTH',
    'BEACON_ORDER',
    'BEACON_TX_TIME',
    'BSN',
    'COORD_EXTENDED_ADDRESS',
    'COORD_SHORT_ADDRESS',
    'DSN',
    'GTS_PERMIT',
    'MAX_BE',
    'MAX_CSMA_BACKOFFS',
    'MAX_FRAME_TOTAL_WAIT_TIME',
    'MAX_FRAME_RETRIES',
    'MIN_BE',
    'LIFS_PERIOD',
    'SIFS_PERIOD',
    'PAN_ID',
    'PROMISCUOUS_MODE',
    'RESPONSE_WAIT_TIME',
    'RX_ON_WHEN_IDLE',
    'SECURITY_ENABLED',
    'SHORT_ADDRESS',
    'SUPERFRAME_ORDER',
    'SYNC_SYMBOL_OFFSET',
    'TIMESTAMP_SUPPORTED',
    'TRANSACTION_PERSISTENCE_TIME',
    'TX_CONTROL_ACTIVE_DURATION',
    'TX_CONTROL_PAUSE_DURATION',
    'ENH_ACK_WAIT_DURATION',
    'IMPLICIT_BROADCAST',
    'SIMPLE_ADDRESS',
    'DISCONNECT_TIME',
    'JOIN_PRIORITY',
    'ASN',
    'NO_HL_BUFFERS',
    'SLOTFRAME_TABLE ',
    'LINK_TABLE',
    'TIMESLOT_TEMPLATE',
    'HOPPINGSEQUENCE_ID',
    'CHANNEL_PAGE',
    'NUMBER_OF_CHANNELS',
    'PHY_CONFIGURATION',
    'EXTENTED_BITMAP',
    'HOPPING_SEQUENCE_LENGTH',
    'HOPPING_SEQUENCE_LIST',
    'CURRENT_HOP',
    'DWELL_TIME',
    'CSL_PERIOD',
    'CSL_MAX_PERIOD',
    'CSL_CHANNEL_MASK',
    'CSL_FRAME_PENDING_WAIT_T',
    'LOW_ENERGY_SUPERFRAME_SUPPORTED',
    'LOW_ENERGY_SUPERFRAME_SYNC_INTERVAL',
    'PERFORMANCE_METRICS',
    'USE_ENHANCED_BEACON',
    'EB_IE_LIST',
    'EB_FILTERING_ENABLED',
    'EBSN',
    'EB_AUTO_SA',
    'EACK_IE_LIST',
    'KEY_TABLE',
    'DEVICE_TABLE',
    'SECURITY_LEVEL_TABLE',
    'FRAME_COUNTER',
    'MT_DATA_SECURITY_LEVEL',
    'MT_DATA_KEY_ID_MODE',
    'MT_DATA_KEY_SOURCE',
    'MT_DATA_KEY_INDEX',
    'DEFAULT_KEY_SOURCE',
    'PAN_COORD_EXTENDED_ADDRESS',
    'PAN_COORD_SHORT_ADDRESS',
    'FRAME_COUNTER_MODE',
    'CSL_SYNC_TX_MARGIN',
    'CSL_MAX_AGE_REMOTE_INFO',
    'TSCH_ENABLED',
    'LE_ENABLED',
    'CURRENT_CHANNEL',
    'CHANNELS_SUPPORTED',
    'TX_POWER_TOLERANCE',
    'TX_POWER',
    'CCA_MODE',
    'CURRENT_PAGE',
    'MAX_FRAME_DURATION',
    'SHR_DURATION',
    'TRAFFIC_COUNTERS',
    'LE_CAPABLE',
    'LL_CAPABLE',
    'DSME_CAPABLE',
    'RFID_CAPABLE',
    'AMCA_CAPABLE',
    'METRICS_CAPABLE',
    'RANGING_SUPPORTED',
    'KEEP_PHY_ENABLED',
    'METRICS_ENABLED',
    'BEACON_AUTO_RESPOND',
    'TSCH_CAPABLE',
    'TS_SYNC_CORRECT_THRESHOLD'
    'BO_IRQ_THRESHOLD'
    'PTI_CONFIG'
]
