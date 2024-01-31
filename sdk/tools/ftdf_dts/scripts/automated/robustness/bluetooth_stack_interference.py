import sys  #cli arguments
import time  #sleep

from scriptIncludes import *

PANId     = 0x0001
channel   = 11
secLvl    = 1
keyIdMode = 3
keyIndex  = 5
keySource = [0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f]

# SCRIPT Settings:
msgSET_responseWaitTime = {'msgId': ftdf.FTDF_SET_REQUEST,
                           'PIBAttribute': ftdf.FTDF_PIB_RESPONSE_WAIT_TIME,
                           'PIBAttributeValue': 64 }

msgSET_ASSOC_PERMIT = {'msgId': ftdf.FTDF_SET_REQUEST,
                       'PIBAttribute': ftdf.FTDF_PIB_ASSOCIATION_PERMIT,
                       'PIBAttributeValue': True }

msgASSOC_REQ = {
    'msgId': ftdf.FTDF_ASSOCIATE_REQUEST,
    'channelNumber': channel,
    'channelPage': 0,
    'coordAddrMode': ftdf.FTDF_EXTENDED_ADDRESS,
    'coordPANId': PANId,
    'coordAddr': 0x0010,
    'capabilityInformation': 0xc0, #non-fast
    'securityLevel': secLvl,
    'keyIdMode': keyIdMode,
    'keySource': keySource,
    'keyIndex': keyIndex,
    'channelOffset': 0,
    'hoppingSequenceId': 0
}

msgASSOC_RESP = {
    'msgId': ftdf.FTDF_ASSOCIATE_RESPONSE,
    'deviceAddress': 0x0000000000000020,
    'assocShortAddress': 0x0020,
    'status': ftdf.FTDF_ASSOCIATION_SUCCESSFUL,
    'fastA': False,
    'securityLevel':secLvl,
    'keyIdMode': keyIdMode,
    'keySource': keySource,
    'keyIndex': keyIndex,
    'channelOffset': 0,
    'hoppingSequenceLength': 0
}

msgPOLL_REQ = {
    'msgId': ftdf.FTDF_POLL_REQUEST,
    'coordAddrMode': ftdf.FTDF_SHORT_ADDRESS,
    'coordPANId': PANId,
    'coordAddr': 0x0010,
    'securityLevel': secLvl,
    'keyIdMode': keyIdMode,
    'keySource': keySource,
    'keyIndex': keyIndex}

msgRxOnWhenIdle_ena = {'msgId': ftdf.FTDF_SET_REQUEST,
                       'PIBAttribute': ftdf.FTDF_PIB_RX_ON_WHEN_IDLE,
                       'PIBAttributeValue': True}

msgRxOnWhenIdle_dis = {'msgId': ftdf.FTDF_SET_REQUEST,
                       'PIBAttribute': ftdf.FTDF_PIB_RX_ON_WHEN_IDLE,
                       'PIBAttributeValue': False}

set_csl_period_msg =         { 'msgId': ftdf.FTDF_SET_REQUEST,
                               'PIBAttribute': ftdf.FTDF_PIB_CSL_PERIOD,
                               'PIBAttributeValue': 1250 }

set_csl_period_max_msg =     { 'msgId': ftdf.FTDF_SET_REQUEST,
                               'PIBAttribute': ftdf.FTDF_PIB_CSL_MAX_PERIOD,
                               'PIBAttributeValue': 1250 }

set_csl_sync_tx_margin_msg = { 'msgId': ftdf.FTDF_SET_REQUEST,
                               'PIBAttribute': ftdf.FTDF_PIB_CSL_SYNC_TX_MARGIN,
                               'PIBAttributeValue': 11 }

set_csl_max_age_msg =        { 'msgId': ftdf.FTDF_SET_REQUEST,
                               'PIBAttribute': ftdf.FTDF_PIB_CSL_MAX_AGE_REMOTE_INFO,
                               'PIBAttributeValue': 62500 }

set_le_ena_msg =             { 'msgId': ftdf.FTDF_SET_REQUEST,
                               'PIBAttribute': ftdf.FTDF_PIB_LE_ENABLED,
                               'PIBAttributeValue': True }

set_le_dis_msg =             { 'msgId': ftdf.FTDF_SET_REQUEST,
                               'PIBAttribute': ftdf.FTDF_PIB_LE_ENABLED,
                               'PIBAttributeValue': False }

msgSTART_REQ = {
    'msgId': ftdf.FTDF_START_REQUEST,
    'PANId': PANId,
    'channelNumber': channel,
    'channelPage': 0,
    'startTime': 0,
    'beaconOrder': 15,
    'superframeOrder': 0,
    'PANCoordinator': True,
    'batteryLifeExtension': 0,
    'coordRealignment': 0,
    'coordRealignSecurityLevel': 0,
    'coordRealignKeyIdMode': 0,
    'coordRealignKeySource': [0,0,0,0,0,0,0,0],
    'coordRealignKeyIndex': 0,
    'beaconSecurityLevel': 0,
    'beaconKeyIdMode': 0,
    'beaconKeySource': [0,0,0,0,0,0,0,0],
    'beaconKeyIndex': 0 }

msgTSCH_MODE_REQ = {
    'msgId': ftdf.FTDF_TSCH_MODE_REQUEST,
    'tschMode': ftdf.FTDF_TSCH_ON,
    'timeslotStartTime': 0 }

msgTSCH_MODE_OFF = {
    'msgId': ftdf.FTDF_TSCH_MODE_REQUEST,
    'tschMode': ftdf.FTDF_TSCH_OFF,
    'timeslotStartTime': 0 }

msgSCAN_REQ = {
    'msgId': ftdf.FTDF_SCAN_REQUEST,
    'scanType': ftdf.FTDF_PASSIVE_SCAN,
    'scanChannels': 0x00001800,
    'channelPage': 0,
    'scanDuration': 9,
    'securityLevel': 0,
    'keyIdMode': 0,
    'keySource': [],
    'keyIndex': 0}

msgENHANCED_BEACON = {
    'msgId': ftdf.FTDF_BEACON_REQUEST,
    'beaconType': ftdf.FTDF_ENHANCED_BEACON,
    'channel': channel,
    'channelPage': 0,
    'superframeOrder': 0,
    'beaconSecurityLevel': 0,
    'beaconKeyIdMode': 0,
    'beaconKeySource': [],
    'beaconKeyIndex': 0,
    'dstAddrMode': ftdf.FTDF_SHORT_ADDRESS,
    'dstAddr': 0xFFFF,
    'BSNSuppression': 0, }


# Security definitions:
# Key Table
keyTable_dev1 = {
  'nrOfKeyDescriptors': 1,
  'keyDescriptors': [
    {
      # Key Id Lookup Descriptors (one of the descriptors need to match)
      'nrOfKeyIdLookupDescriptors': 1,
      'keyIdLookupDescriptors': [
        {
        'keyIdMode': keyIdMode, # Determens whitch of these fields shoud be used
        'keySource': keySource,
        'keyIndex': keyIndex,
        'deviceAddrMode': ftdf.FTDF_SHORT_ADDRESS,
        'devicePANId': PANId,
        'deviceAddress': 0x0020
        }
      ],

      # Device Descriptor Handles (Device Table entrys that this key is for)
      'nrOfDeviceDescriptorHandles': 1,
      'deviceDescriptorHandles': [0],

      # Key Usage Descriptors (Frame types this key may be used on)
      'nrOfKeyUsageDescriptors': 7,
      'keyUsageDescriptors': [
        {
        'frameType': ftdf.FTDF_ACKNOWLEDGEMENT_FRAME,
        'commandFrameId': 0
        },
        {
        'frameType': ftdf.FTDF_DATA_FRAME,
        'commandFrameId': 0
        },
        {
        'frameType': ftdf.FTDF_MAC_COMMAND_FRAME,
        'commandFrameId': 1
        },
        {
        'frameType': ftdf.FTDF_MAC_COMMAND_FRAME,
        'commandFrameId': 2
        },
        {
        'frameType': ftdf.FTDF_MAC_COMMAND_FRAME,
        'commandFrameId': 4
        },
        {
        'frameType': ftdf.FTDF_MULTIPURPOSE_FRAME,
        'commandFrameId': 0
        },
        {
        'frameType': ftdf.FTDF_BEACON_FRAME,
        'commandFrameId': 0
        }
      ],

      # Key
      'key': [ 0xC0, 0xC1, 0xC2, 0xC3, 0xC4, 0xC5, 0xC6, 0xC7,
           0xC8, 0xC9, 0xCA, 0xCB, 0xCC, 0xCD, 0xCE, 0xCF ]
    }
  ]
}

keyTable_dev2 = {
  'nrOfKeyDescriptors': 1,
  'keyDescriptors': [
    {
      # Key Id Lookup Descriptors (one of the descriptors need to match)
      'nrOfKeyIdLookupDescriptors': 2,
      'keyIdLookupDescriptors': [
        {
        'keyIdMode': keyIdMode, # Determens whitch of these fields shoud be used
        'keySource': keySource,
        'keyIndex': keyIndex,
        'deviceAddrMode': ftdf.FTDF_SHORT_ADDRESS,
        'devicePANId': PANId,
        'deviceAddress': 0x0010
        },
        {
        'keyIdMode': 0, # Determens whitch of these fields shoud be used
        'keySource': keySource,
        'keyIndex': keyIndex,
        'deviceAddrMode': ftdf.FTDF_SHORT_ADDRESS,
        'devicePANId': PANId,
        'deviceAddress': 0x0010
        }
      ],

      # Device Descriptor Handles (Device Table entrys that this key is for)
      'nrOfDeviceDescriptorHandles': 1,
      'deviceDescriptorHandles': [0],

      # Key Usage Descriptors (Frame types this key may be used on)
      'nrOfKeyUsageDescriptors': 7,
      'keyUsageDescriptors': [
        {
        'frameType': ftdf.FTDF_ACKNOWLEDGEMENT_FRAME,
        'commandFrameId': 0
        },
        {
        'frameType': ftdf.FTDF_DATA_FRAME,
        'commandFrameId': 0
        },
        {
        'frameType': ftdf.FTDF_MAC_COMMAND_FRAME,
        'commandFrameId': 1
        },
        {
        'frameType': ftdf.FTDF_MAC_COMMAND_FRAME,
        'commandFrameId': 2
        },
        {
        'frameType': ftdf.FTDF_MAC_COMMAND_FRAME,
        'commandFrameId': 4
        },
        {
        'frameType': ftdf.FTDF_MULTIPURPOSE_FRAME,
        'commandFrameId': 0
        },
        {
        'frameType': ftdf.FTDF_BEACON_FRAME,
        'commandFrameId': 0
        }
      ],

      # Key
      'key': [ 0xC0, 0xC1, 0xC2, 0xC3, 0xC4, 0xC5, 0xC6, 0xC7,
           0xC8, 0xC9, 0xCA, 0xCB, 0xCC, 0xCD, 0xCE, 0xCF ]
    }
  ]
}

# Security Level Table (security level required for each MAC frame type and subtype)
securityLevelTable_dev1 = {
  'nrOfSecurityLevelDescriptors': 7,
  'securityLevelDescriptors': [
    {
    'frameType': ftdf.FTDF_ACKNOWLEDGEMENT_FRAME,
    'commandFrameId': 0,
    'securityMinimum': 1,
    'deviceOverrideSecurityMinimum': 0,
    'allowedSecurityLevels': 0
    },
    {
    'frameType': ftdf.FTDF_DATA_FRAME,
    'commandFrameId': 0,
    'securityMinimum': 1,
    'deviceOverrideSecurityMinimum': 0,
    'allowedSecurityLevels': 0
    },
    {
    'frameType': ftdf.FTDF_MAC_COMMAND_FRAME,
    'commandFrameId': 1,
    'securityMinimum': 1,
    'deviceOverrideSecurityMinimum': 0,
    'allowedSecurityLevels': 0
    },
    {
    'frameType': ftdf.FTDF_MAC_COMMAND_FRAME,
    'commandFrameId': 2,
    'securityMinimum': 1,
    'deviceOverrideSecurityMinimum': 0,
    'allowedSecurityLevels': 0
    },
    {
    'frameType': ftdf.FTDF_MAC_COMMAND_FRAME,
    'commandFrameId': 4,
    'securityMinimum': 1,
    'deviceOverrideSecurityMinimum': 0,
    'allowedSecurityLevels': 0
    },
    {
    'frameType': ftdf.FTDF_MULTIPURPOSE_FRAME,
    'commandFrameId': 0,
    'securityMinimum': 1,
    'deviceOverrideSecurityMinimum': 0,
    'allowedSecurityLevels': 0
    },
    {
    'frameType': ftdf.FTDF_BEACON_FRAME,
    'commandFrameId': 0,
    'securityMinimum': 0,
    'deviceOverrideSecurityMinimum': 0,
    'allowedSecurityLevels': 0
    }
  ]
}

securityLevelTable_dev2 = {
  'nrOfSecurityLevelDescriptors': 7,
  'securityLevelDescriptors': [
    {
    'frameType': ftdf.FTDF_ACKNOWLEDGEMENT_FRAME,
    'commandFrameId': 0,
    'securityMinimum': 1,
    'deviceOverrideSecurityMinimum': 0,
    'allowedSecurityLevels': 0
    },
    {
    'frameType': ftdf.FTDF_DATA_FRAME,
    'commandFrameId': 0,
    'securityMinimum': 1,
    'deviceOverrideSecurityMinimum': 0,
    'allowedSecurityLevels': 0
    },
    {
    'frameType': ftdf.FTDF_MAC_COMMAND_FRAME,
    'commandFrameId': 1,
    'securityMinimum': 1,
    'deviceOverrideSecurityMinimum': 0,
    'allowedSecurityLevels': 0
    },
    {
    'frameType': ftdf.FTDF_MAC_COMMAND_FRAME,
    'commandFrameId': 2,
    'securityMinimum': 1,
    'deviceOverrideSecurityMinimum': 0,
    'allowedSecurityLevels': 0
    },
    {
    'frameType': ftdf.FTDF_MAC_COMMAND_FRAME,
    'commandFrameId': 4,
    'securityMinimum': 1,
    'deviceOverrideSecurityMinimum': 0,
    'allowedSecurityLevels': 0
    },
    {
    'frameType': ftdf.FTDF_MULTIPURPOSE_FRAME,
    'commandFrameId': 0,
    'securityMinimum': 1,
    'deviceOverrideSecurityMinimum': 0,
    'allowedSecurityLevels': 0
    },
    {
    'frameType': ftdf.FTDF_BEACON_FRAME,
    'commandFrameId': 0,
    'securityMinimum': 0,
    'deviceOverrideSecurityMinimum': 0,
    'allowedSecurityLevels': 0
    }
  ]
}

# Device Table (Each remote device that uses security to communicate)
deviceTable_dev1 = {
  'nrOfDeviceDescriptors': 1,
  'deviceDescriptors': [
    {
      'PANId': PANId,
      'shortAddress': 0x0020,
      'extAddress': 0x0000000000000020,
      'frameCounter': 0,
      'exempt': False # If minimum security level overiding is needed
    }
  ]
}

deviceTable_dev2 = {
  'nrOfDeviceDescriptors': 1,
  'deviceDescriptors': [
    {
      'PANId': PANId,
      'shortAddress': 0x0010,
      'extAddress': 0x0000000000000010,
      'frameCounter': 0,
      'exempt': False # If minimum security level overiding is needed
    }
  ]
}


msgSET_SecurityEnabled = {
  'msgId': ftdf.FTDF_SET_REQUEST,
  'PIBAttribute': ftdf.FTDF_PIB_SECURITY_ENABLED,
  'PIBAttributeValue': True
}

msgSET_Dev1_SecurityKeyTable = {
  'msgId': ftdf.FTDF_SET_REQUEST,
  'PIBAttribute': ftdf.FTDF_PIB_KEY_TABLE,
  'PIBAttributeValue': keyTable_dev1
}
msgSET_Dev2_SecurityKeyTable = {
  'msgId': ftdf.FTDF_SET_REQUEST,
  'PIBAttribute': ftdf.FTDF_PIB_KEY_TABLE,
  'PIBAttributeValue': keyTable_dev2
}

msgSET_Dev1_SecurityLevelTable = {
  'msgId': ftdf.FTDF_SET_REQUEST,
  'PIBAttribute': ftdf.FTDF_PIB_SECURITY_LEVEL_TABLE,
  'PIBAttributeValue': securityLevelTable_dev1
}
msgSET_Dev2_SecurityLevelTable = {
  'msgId': ftdf.FTDF_SET_REQUEST,
  'PIBAttribute': ftdf.FTDF_PIB_SECURITY_LEVEL_TABLE,
  'PIBAttributeValue': securityLevelTable_dev2
}

msgSET_Dev1_SecurityDeviceTable = {
  'msgId': ftdf.FTDF_SET_REQUEST,
  'PIBAttribute': ftdf.FTDF_PIB_DEVICE_TABLE,
  'PIBAttributeValue': deviceTable_dev1
}
msgSET_Dev2_SecurityDeviceTable = {
  'msgId': ftdf.FTDF_SET_REQUEST,
  'PIBAttribute': ftdf.FTDF_PIB_DEVICE_TABLE,
  'PIBAttributeValue': deviceTable_dev2
}

msgSET_Dev1_macPANCoordExtendedAddress = {
  'msgId': ftdf.FTDF_SET_REQUEST,
  'PIBAttribute': ftdf.FTDF_PIB_PAN_COORD_EXTENDED_ADDRESS ,
  'PIBAttributeValue': 0x0000000000000010
}
msgSET_Dev1_macPANCoordShortAddress = {
  'msgId': ftdf.FTDF_SET_REQUEST,
  'PIBAttribute': ftdf.FTDF_PIB_PAN_COORD_SHORT_ADDRESS,
  'PIBAttributeValue': 0x0010
}

msgSET_SecurityDefaultKeySource = {
  'msgId': ftdf.FTDF_SET_REQUEST,
  'PIBAttribute': ftdf.FTDF_PIB_DEFAULT_KEY_SOURCE,
  'PIBAttributeValue': [0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f]
}

msgSET_macFrameCounter_4 = {
  'msgId': ftdf.FTDF_SET_REQUEST,
  'PIBAttribute': ftdf.FTDF_PIB_FRAME_COUNTER,
  'PIBAttributeValue': 0x00000000
}

msgSET_MT_SecurityLevel = {
  'msgId': ftdf.FTDF_SET_REQUEST,
  'PIBAttribute': ftdf.FTDF_PIB_MT_DATA_SECURITY_LEVEL,
  'PIBAttributeValue': secLvl
}
msgSET_MT_KeyIdMode = {
  'msgId': ftdf.FTDF_SET_REQUEST,
  'PIBAttribute': ftdf.FTDF_PIB_MT_DATA_KEY_ID_MODE,
  'PIBAttributeValue': keyIdMode
}
msgSET_MT_KeySource = {
  'msgId': ftdf.FTDF_SET_REQUEST,
  'PIBAttribute': ftdf.FTDF_PIB_MT_DATA_KEY_SOURCE,
  'PIBAttributeValue': keySource
}
msgSET_MT_KeyIndex = {
  'msgId': ftdf.FTDF_SET_REQUEST,
  'PIBAttribute': ftdf.FTDF_PIB_MT_DATA_KEY_INDEX,
  'PIBAttributeValue': keyIndex
}


# Message order
msgFlow = ( devId1, msgRESET, ftdf.FTDF_RESET_CONFIRM,
      devId2, msgRESET, ftdf.FTDF_RESET_CONFIRM,

      ##################################
      # Set short address, extended address and PAN ID
      ##################################
      devId1, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
      devId2, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,

      devId1, msgSET_Dev1_ShortAddress, ftdf.FTDF_SET_CONFIRM,
      devId2, msgSET_Dev2_ShortAddress, ftdf.FTDF_SET_CONFIRM,

      devId1, msgSET_Dev1_ExtendedAddress, ftdf.FTDF_SET_CONFIRM,
      devId2, msgSET_Dev2_ExtendedAddress, ftdf.FTDF_SET_CONFIRM,

      ##################################
      # Set macCSLPeriod, macCSLMaxPeriod,
      #  macCSLTxSyncMargin and macCSLMaxAgeRemoteInfo
      ##################################
      devId1, set_csl_period_msg, ftdf.FTDF_SET_CONFIRM,
      devId2, set_csl_period_msg, ftdf.FTDF_SET_CONFIRM,

      devId1, set_csl_period_max_msg, ftdf.FTDF_SET_CONFIRM,
      devId2, set_csl_period_max_msg, ftdf.FTDF_SET_CONFIRM,

      devId1, set_csl_sync_tx_margin_msg, ftdf.FTDF_SET_CONFIRM,
      devId2, set_csl_sync_tx_margin_msg, ftdf.FTDF_SET_CONFIRM,

      devId1, set_csl_max_age_msg, ftdf.FTDF_SET_CONFIRM,
      devId2, set_csl_max_age_msg, ftdf.FTDF_SET_CONFIRM,

      ##################################
      # Set security tables
      ##################################
      devId1, msgSET_Dev1_macPANCoordExtendedAddress, ftdf.FTDF_SET_CONFIRM,
      devId1, msgSET_Dev1_macPANCoordShortAddress, ftdf.FTDF_SET_CONFIRM,

      devId1, msgSET_SecurityDefaultKeySource, ftdf.FTDF_SET_CONFIRM,
      devId2, msgSET_SecurityDefaultKeySource, ftdf.FTDF_SET_CONFIRM,

      devId1, msgSET_Dev1_SecurityKeyTable, ftdf.FTDF_SET_CONFIRM,
      devId2, msgSET_Dev2_SecurityKeyTable, ftdf.FTDF_SET_CONFIRM,

      devId1, msgSET_Dev1_SecurityLevelTable, ftdf.FTDF_SET_CONFIRM,
      devId2, msgSET_Dev2_SecurityLevelTable, ftdf.FTDF_SET_CONFIRM,

      devId1, msgSET_Dev1_SecurityDeviceTable, ftdf.FTDF_SET_CONFIRM,
      devId2, msgSET_Dev2_SecurityDeviceTable, ftdf.FTDF_SET_CONFIRM,

      devId1, msgSET_macFrameCounter_4, ftdf.FTDF_SET_CONFIRM,
      devId2, msgSET_macFrameCounter_4, ftdf.FTDF_SET_CONFIRM,

      devId1, msgSET_MT_SecurityLevel, ftdf.FTDF_SET_CONFIRM,
      devId2, msgSET_MT_SecurityLevel, ftdf.FTDF_SET_CONFIRM,

      devId1, msgSET_MT_KeyIdMode, ftdf.FTDF_SET_CONFIRM,
      devId2, msgSET_MT_KeyIdMode, ftdf.FTDF_SET_CONFIRM,

      devId1, msgSET_MT_KeySource, ftdf.FTDF_SET_CONFIRM,
      devId2, msgSET_MT_KeySource, ftdf.FTDF_SET_CONFIRM,

      devId1, msgSET_MT_KeyIndex, ftdf.FTDF_SET_CONFIRM,
      devId2, msgSET_MT_KeyIndex, ftdf.FTDF_SET_CONFIRM,

      devId1, msgSET_SecurityEnabled, ftdf.FTDF_SET_CONFIRM,
      devId2, msgSET_SecurityEnabled, ftdf.FTDF_SET_CONFIRM )


idx = 0

while( idx < len( msgFlow ) ):
  # Send message
  DTS_sndMsg( msgFlow[idx], msgFlow[idx+1] )

  # Get message confirm
  res, ret = DTS_getMsg( msgFlow[idx],responseTimeout )

  # Check received expected confirm
  if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
  elif ret['msgId'] != msgFlow[idx+2]:
    logstr = ( 'SCRIPT: ERROR: Expected ', msgFlow[idx+2], ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )

  idx += 3


##################################
# Enable bluetooth stack interference with intervals of 5ms
##################################
DTS_simulateBLE( devId1, True )
DTS_simulateBLE( devId2, True )


##################################
# Enable legacy debug modus
##################################
DTS_setRegister( 1, 0x40090390, 4, 0x01 )
DTS_setRegister( 2, 0x40090390, 4, 0x01 )

##################################
# Set sleep attributes
# - lpc frequency = 32.768 kHz
# - lpc period    = 30517578 ps
# - in FPGA is no wakeup latency, but assume it will be 3ms for an asic
# - 3ms / 30517578 = 100 clock cycles
##################################
#DTS_setSleepAttributes(devId1, 30517578, 100)
#DTS_setSleepAttributes(devId2, 30517578, 100)


##################################
# Set responseWaitTime
##################################
DTS_sndMsg(devId1,msgSET_responseWaitTime)
DTS_sndMsg(devId2,msgSET_responseWaitTime)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    raise StopScript("Could not set macResponseWaitTime")

res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    raise StopScript("Could not set macResponseWaitTime")


##################################
# Set slotframes
##################################
for n in range( 0, 2 ):
    msg = { 'msgId': ftdf.FTDF_SET_SLOTFRAME_REQUEST, 'handle': n, 'operation': ftdf.FTDF_ADD, 'size': 7 + ( n * 6 ) }

    DTS_sndMsg( devId1, msg )
    DTS_sndMsg( devId2, msg )

    # Retrieve results
    res1, ret1 = DTS_getMsg( devId1, 1 )
    res2, ret2 = DTS_getMsg( devId2, 1 )

    if (res1 == False or res2 == False):
        raise StopScript( "No response received from device!" )
    elif (ret1['msgId'] != ftdf.FTDF_SET_SLOTFRAME_CONFIRM or
          ret2['msgId'] != ftdf.FTDF_SET_SLOTFRAME_CONFIRM):
        raise StopScript( "Incorrect response received from device: ret1=%s ret2=%s" % (ret1['msgId'],ret2['msgId']))

##################################
# Set links
##################################
links = [ { 'linkHandle': 0, 'linkOptions': 1, 'linkType': 0, 'slotframeHandle': 1, 'nodeAddress': 0x0020, 'timeslot': 0, 'channelOffset': 0 },
          { 'linkHandle': 1, 'linkOptions': 2, 'linkType': 0, 'slotframeHandle': 1, 'nodeAddress': 0x0000, 'timeslot': 12, 'channelOffset': 0 },
          { 'linkHandle': 2, 'linkOptions': 2, 'linkType': 0, 'slotframeHandle': 0, 'nodeAddress': 0x0000, 'timeslot': 3, 'channelOffset': 0 },
          { 'linkHandle': 3, 'linkOptions': 5, 'linkType': 0, 'slotframeHandle': 0, 'nodeAddress': 0x0020, 'timeslot': 2, 'channelOffset': 0 },
          { 'linkHandle': 4, 'linkOptions': 7, 'linkType': 1, 'slotframeHandle': 1, 'nodeAddress': 0xffff, 'timeslot': 6, 'channelOffset': 0 },
          { 'linkHandle': 5, 'linkOptions': 2, 'linkType': 0, 'slotframeHandle': 1, 'nodeAddress': 0x0000, 'timeslot': 4, 'channelOffset': 0 } ]

for link in links:
    msg = link
    msg.update( { 'msgId': ftdf.FTDF_SET_LINK_REQUEST, 'operation': ftdf.FTDF_ADD } )

    DTS_sndMsg( 1, msg )

    # Retrieve results
    res1, ret1 = DTS_getMsg( 1, 1 )

    if (res1 == False):
        raise StopScript( "No response received from device!" )
    elif (ret1['msgId'] != ftdf.FTDF_SET_LINK_CONFIRM):
        raise StopScript( "Incorrect response received from device: ret1=%s" % ret1['msgId'])


links = [ { 'linkHandle': 0, 'linkOptions': 10, 'linkType': 0, 'slotframeHandle': 1, 'nodeAddress': 0x0000, 'timeslot': 0, 'channelOffset': 0 },
          { 'linkHandle': 1, 'linkOptions': 9, 'linkType': 0, 'slotframeHandle': 1, 'nodeAddress': 0x0010, 'timeslot': 12, 'channelOffset': 0 },
          { 'linkHandle': 2, 'linkOptions': 9, 'linkType': 0, 'slotframeHandle': 0, 'nodeAddress': 0x0010, 'timeslot': 3, 'channelOffset': 0 },
          { 'linkHandle': 3, 'linkOptions': 10, 'linkType': 0, 'slotframeHandle': 0, 'nodeAddress': 0x0000, 'timeslot': 2, 'channelOffset': 0 },
          { 'linkHandle': 4, 'linkOptions': 7, 'linkType': 0, 'slotframeHandle': 1, 'nodeAddress': 0x0010, 'timeslot': 6, 'channelOffset': 0 },
          { 'linkHandle': 5, 'linkOptions': 2, 'linkType': 0, 'slotframeHandle': 1, 'nodeAddress': 0x0010, 'timeslot': 4, 'channelOffset': 0 } ]

for link in links:
    msg = link
    msg.update( { 'msgId': ftdf.FTDF_SET_LINK_REQUEST, 'operation': ftdf.FTDF_ADD } )

    DTS_sndMsg( 2, msg )

    # Retrieve results
    res2, ret2 = DTS_getMsg( 2, 1 )

    if (res2 == False):
        raise StopScript( "No response received from device!" )
    elif (ret2['msgId'] != ftdf.FTDF_SET_LINK_CONFIRM):
        raise StopScript( "Incorrect response received from device: ret2=%s" % ret2['msgId'])



##################################
# Start request
##################################
DTS_sndMsg(devId1,msgSTART_REQ)

res, ret = DTS_getMsg(devId1, 1)
if res == False or ret['msgId'] != ftdf.FTDF_START_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    raise StopScript("Expected FTDF_START_CONFIRM(FTDF_SUCCESS)")


##################################
# Set associatePermit to allow association
##################################
DTS_sndMsg(devId1,msgSET_ASSOC_PERMIT)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    raise StopScript("Could not set macAssociatePermit")


##################################
# Set RX on when idle
##################################
DTS_sndMsg(devId1,msgRxOnWhenIdle_ena)

res, ret = DTS_getMsg(devId1, 1)
if res == False or ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    raise StopScript("Expected FTDF_SET_CONFIRM(FTDF_SUCCESS)")


##################################
# Let device 2 associate with device 1
##################################

# associate request
DTS_sndMsg(devId2, msgASSOC_REQ)

# associate indication
res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_ASSOCIATE_INDICATION or ret['capabilityInformation'] != msgASSOC_REQ['capabilityInformation']:
    raise StopScript("Incorrect association capability information rcvd")

# associate response
DTS_sndMsg(devId1, msgASSOC_RESP)

# associate confirm
res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_ASSOCIATE_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS or ret['assocShortAddress'] != msgASSOC_RESP['assocShortAddress']:
    raise StopScript("Incorrect associate confirm received")

# comm status indication
res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_COMM_STATUS_INDICATION or ret['status'] != ftdf.FTDF_SUCCESS:
    raise StopScript("Incorrect COMM_STATUS_INDICATION")




##################################
##################################
# Test can be repeated as many times as wished for from here
##################################
##################################

for test_repeat_nr in range( 2 ):
    ##################################
    # Set RX on when idle
    ##################################
    DTS_sndMsg(devId1,msgRxOnWhenIdle_ena)

    res, ret = DTS_getMsg(devId1, 1)
    if res == False or ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
        raise StopScript("Expected FTDF_SET_CONFIRM(FTDF_SUCCESS)")


    ##################################
    # Repeat next steps 10 times
    ##################################
    for i in range( 10 ):
        ##################################
        # Send poll request
        ##################################
        DTS_sndMsg(devId2, msgPOLL_REQ)

        # Poll confirm
        res, ret = DTS_getMsg( devId2, responseTimeout )
        if res == False or ret['msgId'] != ftdf.FTDF_POLL_CONFIRM or ret['status'] != ftdf.FTDF_NO_DATA:
            raise StopScript("Expected FTDF_POLL_CONFIRM(NO_DATA)")

        ##################################
        # Send indirect data frame
        ##################################
        msdu = [0x1, 0x2, 0x3, 0x4, 0x5]
        msgDATA_indirect = {
          'msgId': ftdf.FTDF_DATA_REQUEST,
          'srcAddrMode': ftdf.FTDF_SHORT_ADDRESS,
          'dstAddrMode': ftdf.FTDF_SHORT_ADDRESS,
          'dstPANId': PANId,
          'dstAddr': 0x0020,
          'msduLength': len( msdu ),
          'msdu': msdu,
          'msduHandle': 1,
          'ackTX': True,
          'GTSTX': False,
          'indirectTX': True,
          'securityLevel': secLvl,
          'keyIdMode': keyIdMode,
          'keySource': keySource,
          'keyIndex': keyIndex,
          'frameControlOptions': 0,
          'headerIEList': 0,
          'payloadIEList': 0,
          'sendMultiPurpose': False }

        DTS_sndMsg(devId1, msgDATA_indirect)
        time.sleep( .5 )

        ##################################
        # Send poll request
        ##################################
        DTS_sndMsg(devId2, msgPOLL_REQ)

        # Poll confirm
        res, ret = DTS_getMsg( devId2, responseTimeout )
        if res == False or ret['msgId'] != ftdf.FTDF_POLL_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
            raise StopScript("Expected FTDF_POLL_CONFIRM(SUCCESS)")

        # Data indication
        res, ret = DTS_getMsg( devId2, responseTimeout )
        if res == False or ret['msgId'] != ftdf.FTDF_DATA_INDICATION:
            raise StopScript("Expected FTDF_DATA_INDICATION")

        # Data confirm
        res, ret = DTS_getMsg( devId1, responseTimeout )
        if res == False or ret['msgId'] != ftdf.FTDF_DATA_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
            raise StopScript("Expected FTDF_DATA_CONFIRM(SUCCESS)")

        time.sleep( .5 )


    ##################################
    # Send 16 direct data frames
    ##################################
    msdu = [0xa, 0xb, 0xc, 0xd, 0xe]
    msgDATA_direct = {
      'msgId': ftdf.FTDF_DATA_REQUEST,
      'srcAddrMode': ftdf.FTDF_SHORT_ADDRESS,
      'dstAddrMode': ftdf.FTDF_SHORT_ADDRESS,
      'dstPANId': PANId,
      'dstAddr': 0x0010,
      'msduLength': len( msdu ),
      'msdu': msdu,
      'msduHandle': 1,
      'ackTX': True,
      'GTSTX': False,
      'indirectTX': False,
      'securityLevel': secLvl,
      'keyIdMode': keyIdMode,
      'keySource': keySource,
      'keyIndex': keyIndex,
      'frameControlOptions': 0,
      'headerIEList': 0,
      'payloadIEList': 0,
      'sendMultiPurpose': False }

    for i in range( 16 ):
        # 16x data request
        DTS_sndMsg(devId2, msgDATA_direct)

        # 16x data confirm
        res, ret = DTS_getMsg( devId2, responseTimeout )
        if res == False or ret['msgId'] != ftdf.FTDF_DATA_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
            raise StopScript("Expected FTDF_DATA_CONFIRM(SUCCESS)")

        # 16x data indication
        res, ret = DTS_getMsg( devId1, responseTimeout )
        if res == False or ret['msgId'] != ftdf.FTDF_DATA_INDICATION:
            raise StopScript("Expected FTDF_DATA_INDICATION")



    ##################################
    # Disable RX on when idle
    ##################################
    DTS_sndMsg(devId1,msgRxOnWhenIdle_dis)

    res, ret = DTS_getMsg(devId1, 1)
    if res == False or ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
        raise StopScript("Expected FTDF_SET_CONFIRM(FTDF_SUCCESS)")


    ##################################
    # Set macLeEnabled to true
    ##################################
    DTS_sndMsg(devId1,set_le_ena_msg)
    DTS_sndMsg(devId2,set_le_ena_msg)

    res, ret = DTS_getMsg(devId1, 1)
    if res == False or ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
        raise StopScript("Expected FTDF_SET_CONFIRM(FTDF_SUCCESS)")

    res, ret = DTS_getMsg(devId2, 1)
    if res == False or ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
        raise StopScript("Expected FTDF_SET_CONFIRM(FTDF_SUCCESS)")


    ##################################
    # Enable sleep when possible for device 2
    ##################################
    time.sleep(1)
    #DTS_sleepWhenPossible( devId2, True )

    ##################################
    # Send 16 data frames
    ##################################
    msdu = [0xa, 0xb, 0xc, 0xd, 0xe]
    msgDATA_le = {
      'msgId': ftdf.FTDF_DATA_REQUEST,
      'srcAddrMode': ftdf.FTDF_SHORT_ADDRESS,
      'dstAddrMode': ftdf.FTDF_SHORT_ADDRESS,
      'dstPANId': PANId,
      'dstAddr': 0x0020,
      'msduLength': len( msdu ),
      'msdu': msdu,
      'msduHandle': 1,
      'ackTX': True,
      'GTSTX': False,
      'indirectTX': False,
      'securityLevel': secLvl,
      'keyIdMode': keyIdMode,
      'keySource': keySource,
      'keyIndex': keyIndex,
      'frameControlOptions': 0,
      'headerIEList': 0,
      'payloadIEList': 0,
      'sendMultiPurpose': False }

    for i in range( 16 ):
        # 16x data request
        DTS_sndMsg(devId1, msgDATA_le)

        # 16x data confirm
        res, ret = DTS_getMsg( devId1, responseTimeout )
        if res == False or ret['msgId'] != ftdf.FTDF_DATA_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
            raise StopScript("Expected FTDF_DATA_CONFIRM(SUCCESS)")

        # 16x data indication
        res, ret = DTS_getMsg( devId2, responseTimeout )
        if res == False or ret['msgId'] != ftdf.FTDF_DATA_INDICATION:
            raise StopScript("Expected FTDF_DATA_INDICATION")


    ##################################
    # Disable sleep when possible for device 2
    ##################################
    #DTS_sleepWhenPossible( devId2, False )

    # It can be that a wakeup ready message is received
    while True:
        res, ret = DTS_getMsg( devId2, 1 )
        if res == False:
            break


    ##################################
    # Set macLeEnabled to false
    ##################################
    DTS_sndMsg(devId2,set_le_dis_msg)

    res, ret = DTS_getMsg(devId2, 1)
    if res == False or ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
        raise StopScript("Expected FTDF_SET_CONFIRM(FTDF_SUCCESS)")


    ##################################
    # Set RX on when idle
    ##################################
    DTS_sndMsg(devId2,msgRxOnWhenIdle_ena)

    res, ret = DTS_getMsg(devId2, 1)
    if res == False or ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
        raise StopScript("Expected FTDF_SET_CONFIRM(FTDF_SUCCESS)")


    ##################################
    # Enable transparent mode
    ##################################
    DTS_enableTransparantMode( devId2, True, ftdf.FTDF_TRANSPARENT_PASS_ALL_FRAME_TYPES )


    ##################################
    # Send unacknowledged data frame
    ##################################
    msdu = [0xa, 0xb, 0xc, 0xd, 0xe]
    msgDATA_le = {
      'msgId': ftdf.FTDF_DATA_REQUEST,
      'srcAddrMode': ftdf.FTDF_SHORT_ADDRESS,
      'dstAddrMode': ftdf.FTDF_SHORT_ADDRESS,
      'dstPANId': PANId,
      'dstAddr': 0x0020,
      'msduLength': len( msdu ),
      'msdu': msdu,
      'msduHandle': 1,
      'ackTX': False,
      'GTSTX': False,
      'indirectTX': False,
      'securityLevel': secLvl,
      'keyIdMode': keyIdMode,
      'keySource': keySource,
      'keyIndex': keyIndex,
      'frameControlOptions': 0,
      'headerIEList': 0,
      'payloadIEList': 0,
      'sendMultiPurpose': False }

    DTS_sndMsg(devId1, msgDATA_le)

    res, ret = DTS_getMsg( devId1, responseTimeout )
    if res == False or ret['msgId'] != ftdf.FTDF_DATA_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
        raise StopScript("Expected FTDF_DATA_CONFIRM(SUCCESS)")


    ##################################
    # Expect no more than 2 wakeup frames and after that a data frame on device 2
    ##################################
    count = 0
    while True:
        res, ret = DTS_getMsg( devId2, 1 )

        if res == False:
            break

        if ret['frameLength'] == 13:
            count += 1
        else:
            break

    if count > 2:
        raise StopScript( "Expected no more than 2 wakeup frames" )



    ##################################
    # Disable transparent mode
    ##################################
    DTS_enableTransparantMode( devId2, False, 0 )


    ##################################
    # Disable RX on when idle
    ##################################
    DTS_sndMsg(devId2,msgRxOnWhenIdle_dis)

    res, ret = DTS_getMsg(devId2, 1)
    if res == False or ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
        raise StopScript("Expected FTDF_SET_CONFIRM(FTDF_SUCCESS)")


    ##################################
    # Set macLeEnabled to false
    ##################################
    DTS_sndMsg(devId1,set_le_dis_msg)

    res, ret = DTS_getMsg(devId1, 1)
    if res == False or ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
        raise StopScript("Expected FTDF_SET_CONFIRM(FTDF_SUCCESS)")



    ##################################
    # TSCH mode request
    ##################################
    msgTSCH_MODE_REQ['timeslotStartTime'] = 0
    DTS_sndMsg(devId1,msgTSCH_MODE_REQ)

    res, ret = DTS_getMsg(devId1, 1)
    if res == False or ret['msgId'] != ftdf.FTDF_TSCH_MODE_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
        raise StopScript("Expected FTDF_TSCH_MODE_CONFIRM(FTDF_SUCCESS)")


    ##################################
    # Set macAutoRequest to false
    ##################################
    msg = { 'msgId': ftdf.FTDF_SET_REQUEST, 'PIBAttribute': ftdf.FTDF_PIB_AUTO_REQUEST, 'PIBAttributeValue': 0 }
    DTS_sndMsg( 2, msg )

    # Retrieve results
    res2, ret2 = DTS_getMsg( 2, 1 )

    if res2 == False:
        raise StopScript( "No response received from device!" )
    elif (ret2['msgId'] != ftdf.FTDF_SET_CONFIRM):
        raise StopScript( "Incorrect response received from device: ret2=%s" % ret2['msgId'])



    ##################################
    # Passive scan request
    ##################################
    DTS_sndMsg(devId2,msgSCAN_REQ)

    ##################################
    # Send enhanced beacon request
    ##################################
    DTS_sndMsg(devId1,msgENHANCED_BEACON)

    res, ret = DTS_getMsg(devId1, 10)
    if res == False or ret['msgId'] != ftdf.FTDF_BEACON_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
        raise StopScript("Expected FTDF_BEACON_CONFIRM(FTDF_SUCCESS)")

    ##################################
    # Wait for enhanced beacon notification
    ##################################
    slotStartTime = 0
    ASN = 0

    res, ret = DTS_getMsg(devId2, 1)
    if res == False or ret['msgId'] != ftdf.FTDF_BEACON_NOTIFY_INDICATION:
        raise StopScript("Expected FTDF_BEACON_NOTIFICATION_INDICATION")
    else:
        slotStartTime = ret['timestamp'] - 80
        shift = 0
        for n in range(5):
            ASN = ASN + (ret['IEList']['IEs'][0]['content']['subIEs'][0]['content'][n] << shift)
            shift = shift + 8

    ##################################
    # Receive scan confirm
    ##################################
    res, ret = DTS_getMsg(devId2, 20)
    if res == False or ret['msgId'] != ftdf.FTDF_SCAN_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
        raise StopScript("Expected FTDF_SCAN_CONFIRM(FTDF_SUCCESS)")


    ##################################
    # Set ASN
    ##################################
    msg = { 'msgId': ftdf.FTDF_SET_REQUEST, 'PIBAttribute': ftdf.FTDF_PIB_ASN, 'PIBAttributeValue': ASN }
    DTS_sndMsg( 2, msg )

    # Retrieve results
    res2, ret2 = DTS_getMsg( 2, 1 )

    if res2 == False:
        raise StopScript( "No response received from device!" )
    elif (ret2['msgId'] != ftdf.FTDF_SET_CONFIRM):
        raise StopScript( "Incorrect response received from device: ret2=%s" % ret2['msgId'])


    ##################################
    # TSCH mode request
    ##################################
    msgTSCH_MODE_REQ['timeslotStartTime'] = slotStartTime
    DTS_sndMsg(devId2,msgTSCH_MODE_REQ)

    res, ret = DTS_getMsg(devId2, 1)
    if res == False or ret['msgId'] != ftdf.FTDF_TSCH_MODE_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
        raise StopScript("Expected FTDF_TSCH_MODE_CONFIRM(FTDF_SUCCESS)")



    ##################################
    # Send 16 data frames to both devices
    ##################################
    msdu = [0xa, 0xb, 0xc, 0xd, 0xe]
    msgDATA_dev1 = {
      'msgId': ftdf.FTDF_DATA_REQUEST,
      'srcAddrMode': ftdf.FTDF_SHORT_ADDRESS,
      'dstAddrMode': ftdf.FTDF_SHORT_ADDRESS,
      'dstPANId': PANId,
      'dstAddr': 0x0020,
      'msduLength': len( msdu ),
      'msdu': msdu,
      'msduHandle': 1,
      'ackTX': True,
      'GTSTX': False,
      'indirectTX': False,
      'securityLevel': secLvl,
      'keyIdMode': keyIdMode,
      'keySource': keySource,
      'keyIndex': keyIndex,
      'frameControlOptions': 0,
      'headerIEList': 0,
      'payloadIEList': 0,
      'sendMultiPurpose': False }

    msgDATA_dev2 = {
      'msgId': ftdf.FTDF_DATA_REQUEST,
      'srcAddrMode': ftdf.FTDF_SHORT_ADDRESS,
      'dstAddrMode': ftdf.FTDF_SHORT_ADDRESS,
      'dstPANId': PANId,
      'dstAddr': 0x0010,
      'msduLength': len( msdu ),
      'msdu': msdu,
      'msduHandle': 1,
      'ackTX': True,
      'GTSTX': False,
      'indirectTX': False,
      'securityLevel': secLvl,
      'keyIdMode': keyIdMode,
      'keySource': keySource,
      'keyIndex': keyIndex,
      'frameControlOptions': 0,
      'headerIEList': 0,
      'payloadIEList': 0,
      'sendMultiPurpose': False }


    for i in range( 16 ):
        # 16x data request
        DTS_sndMsg(devId1, msgDATA_dev1)

        # 16x data confirm
        res, ret = DTS_getMsg( devId1, responseTimeout )
        if res == False or ret['msgId'] != ftdf.FTDF_DATA_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
            raise StopScript("Expected FTDF_DATA_CONFIRM(SUCCESS)")

        # 16x data indication
        res, ret = DTS_getMsg( devId2, responseTimeout )
        if res == False or ret['msgId'] != ftdf.FTDF_DATA_INDICATION:
            raise StopScript("Expected FTDF_DATA_INDICATION")

        # 16x data request
        DTS_sndMsg(devId2, msgDATA_dev2)

        # 16x data confirm
        res, ret = DTS_getMsg( devId2, responseTimeout )
        if res == False or ret['msgId'] != ftdf.FTDF_DATA_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
            raise StopScript("Expected FTDF_DATA_CONFIRM(SUCCESS)")

        # 16x data indication
        res, ret = DTS_getMsg( devId1, responseTimeout )
        if res == False or ret['msgId'] != ftdf.FTDF_DATA_INDICATION:
            raise StopScript("Expected FTDF_DATA_INDICATION")


    ##################################
    # Disable TSCH mode
    ##################################
    DTS_sndMsg(devId1,msgTSCH_MODE_OFF)

    res, ret = DTS_getMsg(devId1, 1)
    if res == False or ret['msgId'] != ftdf.FTDF_TSCH_MODE_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
        raise StopScript("Expected FTDF_TSCH_MODE_CONFIRM(FTDF_SUCCESS)")

    DTS_sndMsg(devId2,msgTSCH_MODE_OFF)

    res, ret = DTS_getMsg(devId2, 1)
    if res == False or ret['msgId'] != ftdf.FTDF_TSCH_MODE_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
        raise StopScript("Expected FTDF_TSCH_MODE_CONFIRM(FTDF_SUCCESS)")


##################################
# Disable bluetooth stack interference
##################################
DTS_simulateBLE( devId1, False )
DTS_simulateBLE( devId2, False )

