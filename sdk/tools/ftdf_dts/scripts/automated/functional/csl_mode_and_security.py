import sys  #cli arguments
import time  #sleep

from scriptIncludes import *

# SCRIPT Settings:
keyIdMode = 3

set_csl_period_msg =         { 'msgId': ftdf.FTDF_SET_REQUEST, 
                               'PIBAttribute': ftdf.FTDF_PIB_CSL_PERIOD, 
                               'PIBAttributeValue': 80 }

set_csl_period_max_msg =     { 'msgId': ftdf.FTDF_SET_REQUEST, 
                               'PIBAttribute': ftdf.FTDF_PIB_CSL_MAX_PERIOD, 
                               'PIBAttributeValue': 80 }

set_csl_sync_tx_margin_msg = { 'msgId': ftdf.FTDF_SET_REQUEST, 
                               'PIBAttribute': ftdf.FTDF_PIB_CSL_SYNC_TX_MARGIN, 
                               'PIBAttributeValue': 80 }  

set_csl_max_age_msg =        { 'msgId': ftdf.FTDF_SET_REQUEST, 
                               'PIBAttribute': ftdf.FTDF_PIB_CSL_MAX_AGE_REMOTE_INFO, 
                               'PIBAttributeValue': 40000 } 

set_le_ena_msg =             { 'msgId': ftdf.FTDF_SET_REQUEST, 
                               'PIBAttribute': ftdf.FTDF_PIB_LE_ENABLED, 
                               'PIBAttributeValue': True } 


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
        'keySource': [0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f],
        'keyIndex': 5,
        'deviceAddrMode': ftdf.FTDF_SHORT_ADDRESS,
        'devicePANId': 0x0001,
        'deviceAddress': 0x0020
        }
      ],

      # Device Descriptor Handles (Device Table entrys that this key is for)
      'nrOfDeviceDescriptorHandles': 1,
      'deviceDescriptorHandles': [0],

      # Key Usage Descriptors (Frame types this key may be used on)
      'nrOfKeyUsageDescriptors': 4,
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
      'nrOfKeyIdLookupDescriptors': 1,
      'keyIdLookupDescriptors': [
        {
        'keyIdMode': keyIdMode, # Determens whitch of these fields shoud be used
        'keySource': [0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f],
        'keyIndex': 5,
        'deviceAddrMode': ftdf.FTDF_SHORT_ADDRESS,
        'devicePANId': 0x0001,
        'deviceAddress': 0x0010
        }
      ],

      # Device Descriptor Handles (Device Table entrys that this key is for)
      'nrOfDeviceDescriptorHandles': 1,
      'deviceDescriptorHandles': [0],

      # Key Usage Descriptors (Frame types this key may be used on)
      'nrOfKeyUsageDescriptors': 4,
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
  'nrOfSecurityLevelDescriptors': 4,
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
    'frameType': ftdf.FTDF_MULTIPURPOSE_FRAME,
    'commandFrameId': 0,
    'securityMinimum': 1,
    'deviceOverrideSecurityMinimum': 0,
    'allowedSecurityLevels': 0
    },
    {
    'frameType': ftdf.FTDF_BEACON_FRAME,
    'commandFrameId': 0,
    'securityMinimum': 1,
    'deviceOverrideSecurityMinimum': 0,
    'allowedSecurityLevels': 0
    }
  ]
}

securityLevelTable_dev2 = {
  'nrOfSecurityLevelDescriptors': 4,
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
    'frameType': ftdf.FTDF_MULTIPURPOSE_FRAME,
    'commandFrameId': 0,
    'securityMinimum': 1,
    'deviceOverrideSecurityMinimum': 0,
    'allowedSecurityLevels': 0
    },
    {
    'frameType': ftdf.FTDF_BEACON_FRAME,
    'commandFrameId': 0,
    'securityMinimum': 1,
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
      'PANId': 0x0001,
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
      'PANId': 0x0001,
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
msgSET_SecurityDisabled = {
  'msgId': ftdf.FTDF_SET_REQUEST,
  'PIBAttribute': ftdf.FTDF_PIB_SECURITY_ENABLED,
  'PIBAttributeValue': False
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

msgSET_frameCounterMode_4 = {
  'msgId': ftdf.FTDF_SET_REQUEST,
  'PIBAttribute': ftdf.FTDF_PIB_FRAME_COUNTER_MODE,
  'PIBAttributeValue': 0x04
}
msgSET_frameCounterMode_5 = {
  'msgId': ftdf.FTDF_SET_REQUEST,
  'PIBAttribute': ftdf.FTDF_PIB_FRAME_COUNTER_MODE,
  'PIBAttributeValue': 0x05
}
msgSET_macFrameCounter_4 = {
  'msgId': ftdf.FTDF_SET_REQUEST,
  'PIBAttribute': ftdf.FTDF_PIB_FRAME_COUNTER,
  'PIBAttributeValue': 0xfffffff1
}
msgSET_macFrameCounter_5 = {
  'msgId': ftdf.FTDF_SET_REQUEST,
  'PIBAttribute': ftdf.FTDF_PIB_FRAME_COUNTER,
  'PIBAttributeValue': 0xfffffffff1
}


# Message order
msgFlow = ( devId1, msgRESET, ftdf.FTDF_RESET_CONFIRM,
      devId2, msgRESET, ftdf.FTDF_RESET_CONFIRM,

      ##################################
      # 1+2> Set short address, extended address and PAN ID
      ##################################
      devId1, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
      devId2, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,

      devId1, msgSET_Dev1_ShortAddress, ftdf.FTDF_SET_CONFIRM,
      devId2, msgSET_Dev2_ShortAddress, ftdf.FTDF_SET_CONFIRM,

      devId1, msgSET_Dev1_ExtendedAddress, ftdf.FTDF_SET_CONFIRM,
      devId2, msgSET_Dev2_ExtendedAddress, ftdf.FTDF_SET_CONFIRM,

      devId1, msgSET_DSN, ftdf.FTDF_SET_CONFIRM,
      devId2, msgSET_DSN, ftdf.FTDF_SET_CONFIRM,

      ##################################
      # 1+2> Set macCSLPeriod, macCSLMaxPeriod,
      #      macCSLTxSyncMargin and macCSLMaxAgeRemoteInfo
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
      # 1+2> Set security tables
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

      devId1, msgSET_frameCounterMode_4, ftdf.FTDF_SET_CONFIRM,
      devId2, msgSET_macFrameCounter_4, ftdf.FTDF_SET_CONFIRM,

      devId1, msgSET_SecurityEnabled, ftdf.FTDF_SET_CONFIRM,
      devId2, msgSET_SecurityEnabled, ftdf.FTDF_SET_CONFIRM,

      ##################################
      # 1+2> Set LE enabled
      ##################################
      devId1, set_le_ena_msg, ftdf.FTDF_SET_CONFIRM,
      devId2, set_le_ena_msg, ftdf.FTDF_SET_CONFIRM )


idx = 0
res = True
error = 0

while( idx < len( msgFlow ) ):
  # Send message
  DTS_sndMsg( msgFlow[idx], msgFlow[idx+1] )

  # Get message confirm
  res, ret = DTS_getMsg( msgFlow[idx],responseTimeout )

  # Check received expected confirm
  if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    error += 1
  elif ret['msgId'] != msgFlow[idx+2]:
    logstr = ( 'SCRIPT: ERROR: Expected ', msgFlow[idx+2], ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )
    error += 1

  idx += 3


# Data frame
msdu = [0x1, 0x2, 0x3, 0x4, 0x5]

msgDATA = {
  'msgId': ftdf.FTDF_DATA_REQUEST,
  'srcAddrMode': ftdf.FTDF_SHORT_ADDRESS,
  'dstAddrMode': ftdf.FTDF_SHORT_ADDRESS,
  'dstPANId': 0x0001,
  'dstAddr': 0x0020,
  'msduLength': len( msdu ),
  'msdu': msdu,
  'msduHandle': 1,
  'ackTX': True,
  'GTSTX': False,
  'indirectTX': False,
  'securityLevel': 5,
  'keyIdMode': keyIdMode,
  'keySource': [0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f],
  'keyIndex': 5,
  'frameControlOptions': 0,
  'headerIEList': 0,
  'payloadIEList': 0,
  'sendMultiPurpose': False }


########################################
# 1> Send data frame with short address matching DUT2
#    and security parameters matching the security tables
########################################
DTS_sndMsg( devId1, msgDATA )

res, ret = DTS_getMsg( devId1, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    error += 1
elif( ret['msgId'] != ftdf.FTDF_DATA_CONFIRM ):
    logstr = ( 'SCRIPT: ERROR: expected msgId DATA_CONFIRM', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )
    error += 1
else:
    ################################################
    # 2< Receive data frame matching sent data frame
    ################################################
    res, ret = DTS_getMsg( devId2, responseTimeout )
    if( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        error += 1
    elif( ret['msgId'] != ftdf.FTDF_DATA_INDICATION ):
        logstr = ( 'SCRIPT: ERROR: expected msgId DATA_INDICATION', ret['msgId'] )
        raise StopScript( ''.join( map( str, logstr ) ) )
        error += 1
    else:
        if msgDATA['msdu'] != ret['msdu']:
            raise StopScript( 'SCRIPT: ERROR: Received unexpected MSDU' )

