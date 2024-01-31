# Load-drop 2 Test: Security

#

import sys  #cli arguments
import time  #sleep

from scriptIncludes import *


DTS_getReleaseInfo(devId1)
DTS_getReleaseInfo(devId2)
res, ret = DTS_getMsg( devId1,responseTimeout )
res, ret = DTS_getMsg( devId2,responseTimeout )

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

set_enh_ack_wait_msg =       { 'msgId': ftdf.FTDF_SET_REQUEST, 
                               'PIBAttribute': ftdf.FTDF_PIB_ENH_ACK_WAIT_DURATION, 
                               'PIBAttributeValue': 864 }    

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


# Frames definition:
# Data frame
msdu = [0x1, 0x2, 0x3, 0x4, 0x5]

msgDATA_1 = {
  'msgId': ftdf.FTDF_DATA_REQUEST,
  'srcAddrMode': ftdf.FTDF_SHORT_ADDRESS,
  'dstAddrMode': ftdf.FTDF_SHORT_ADDRESS,
  'dstPANId': 0x0001,
  'dstAddr': 0x0020,
  'msduLength': len( msdu ),
  'msdu': msdu,
  'msduHandle': 1,
  'ackTX': False,
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
msgFlow = ( devId1, msgRESET, ftdf.FTDF_RESET_CONFIRM, 0,
      devId2, msgRESET, ftdf.FTDF_RESET_CONFIRM, 0,

      devId1, msgSET_PANId, ftdf.FTDF_SET_CONFIRM, 0,
      devId2, msgSET_PANId, ftdf.FTDF_SET_CONFIRM, 0,

      devId1, msgSET_Dev1_ShortAddress, ftdf.FTDF_SET_CONFIRM, 0,
      devId2, msgSET_Dev2_ShortAddress, ftdf.FTDF_SET_CONFIRM, 0,

      devId1, msgSET_Dev1_ExtendedAddress, ftdf.FTDF_SET_CONFIRM, 0,
      devId2, msgSET_Dev2_ExtendedAddress, ftdf.FTDF_SET_CONFIRM, 0,

      devId1, msgSET_DSN, ftdf.FTDF_SET_CONFIRM, 0,
      devId2, msgSET_DSN, ftdf.FTDF_SET_CONFIRM, 0,

      devId1, msgSET_Dev1_macPANCoordExtendedAddress, ftdf.FTDF_SET_CONFIRM, 0,

      devId1, msgSET_Dev1_macPANCoordShortAddress, ftdf.FTDF_SET_CONFIRM, 0,

      devId1, set_csl_period_msg, ftdf.FTDF_SET_CONFIRM, 0,
      devId2, set_csl_period_msg, ftdf.FTDF_SET_CONFIRM, 0,

      devId1, set_csl_period_max_msg, ftdf.FTDF_SET_CONFIRM, 0,
      devId2, set_csl_period_max_msg, ftdf.FTDF_SET_CONFIRM, 0,

      devId1, set_csl_sync_tx_margin_msg, ftdf.FTDF_SET_CONFIRM, 0,
      devId2, set_csl_sync_tx_margin_msg, ftdf.FTDF_SET_CONFIRM, 0,

      devId1, set_csl_max_age_msg, ftdf.FTDF_SET_CONFIRM, 0,
      devId2, set_csl_max_age_msg, ftdf.FTDF_SET_CONFIRM, 0,

      devId1, set_enh_ack_wait_msg, ftdf.FTDF_SET_CONFIRM, 0,

      devId1, set_le_ena_msg, ftdf.FTDF_SET_CONFIRM, 0,

      devId1, msgSET_SecurityDefaultKeySource, ftdf.FTDF_SET_CONFIRM, 0,
      devId2, msgSET_SecurityDefaultKeySource, ftdf.FTDF_SET_CONFIRM, 0,

      devId1, msgSET_Dev1_SecurityKeyTable, ftdf.FTDF_SET_CONFIRM, 0,
      devId2, msgSET_Dev2_SecurityKeyTable, ftdf.FTDF_SET_CONFIRM, 0,

      devId1, msgSET_Dev1_SecurityLevelTable, ftdf.FTDF_SET_CONFIRM, 0,
      devId2, msgSET_Dev2_SecurityLevelTable, ftdf.FTDF_SET_CONFIRM, 0,

      devId1, msgSET_Dev1_SecurityDeviceTable, ftdf.FTDF_SET_CONFIRM, 0,
      devId2, msgSET_Dev2_SecurityDeviceTable, ftdf.FTDF_SET_CONFIRM, 0,

      devId1, msgSET_SecurityEnabled, ftdf.FTDF_SET_CONFIRM, 0,
      devId2, msgSET_SecurityEnabled, ftdf.FTDF_SET_CONFIRM, 0,

      devId2, msgRxEnable_On, ftdf.FTDF_RX_ENABLE_CONFIRM, 0,

      devId1, msgSET_frameCounterMode_4, ftdf.FTDF_SET_CONFIRM, 0,
      devId1, msgSET_macFrameCounter_4, ftdf.FTDF_SET_CONFIRM, 0,
      devId1, msgDATA_1, ftdf.FTDF_DATA_CONFIRM, 1,

      devId1, msgSET_frameCounterMode_5, ftdf.FTDF_SET_CONFIRM, 0,
      devId1, msgSET_macFrameCounter_5, ftdf.FTDF_SET_CONFIRM, 0,
      devId1, msgDATA_1, ftdf.FTDF_DATA_CONFIRM, 2,
      )


idx = 0
result = True
while( idx < len( msgFlow ) ):

  if( msgFlow[idx+2] == ftdf.FTDF_RX_ENABLE_CONFIRM ):
    # Enable Transparant Mode Receiving DUT
    options = ( ftdf.FTDF_TRANSPARENT_AUTO_ACK )
    enable = True
    DTS_enableTransparantMode( devId2, enable, options )

  # Send message
  DTS_sndMsg( msgFlow[idx], msgFlow[idx+1] )

  # Get message confirm
  res, ret = DTS_getMsg( msgFlow[idx], responseTimeout )

  # Check received expected confirm
  if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    result = False
    break
  elif ret['msgId'] != msgFlow[idx+2]:
    logstr = ( 'SCRIPT: ERROR: Expected ', msgFlow[idx+2], ' confirm, instead received ', ret['msgId'] -1 )
    raise StopScript( ''.join( map( str, logstr ) ) )
    result = False
    break
  else:
    if( ret['msgId'] == ftdf.FTDF_DATA_CONFIRM and
        msgFlow[idx+3] != 3 ):
      res, ret = DTS_getMsg( devId2, responseTimeout )

      if( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        break
      elif ret['msgId'] != ftdf.FTDF_TRANSPARENT_INDICATION:
        logstr = ( 'SCRIPT: ERROR: Expected ftdf.FTDF_TRANSPARENT_INDICATION confirm, instead received ', ret['msgId'] )
        raise StopScript( ''.join( map( str, logstr ) ) )
        break
      else:
        # Check received data frame
        if( msgFlow[idx+3] == 1 ):
            expectedFrame = [9, 168, 119, 1, 0, 32, 0, 16, 0, 29, 241, 255, 255, 255, 8, 9, 10, 11, 12, 13, 14, 15, 5, 116, 98, 238, 59, 74, 93, 65, 21, 22, 253, 204]
        elif( msgFlow[idx+3] == 2 ):
            expectedFrame = [9, 168, 120, 1, 0, 32, 0, 16, 0, 93, 241, 255, 255, 255, 255, 8, 9, 10, 11, 12, 13, 14, 15, 5, 98, 173, 204, 251, 78, 124, 208, 153, 213, 184, 135]
        dataFrameValid = True

        # Print received frame
        idx2 = 0
        while( idx2 < len( ret['frame'] ) ):
          #print( idx2, ' ', hex( ret['frame'][idx2] ) )
          idx2+=1

        # Check frame length
        if( len( expectedFrame ) != len( ret['frame'] ) ):
          raise StopScript( 'SCRIPT: ERROR: DATA frame length incorrect' )
          dataFrameValid = False
        # Check frame bytes
        else:
          idx2 = 0
          while( idx2 < len( expectedFrame ) ):
            if( expectedFrame[idx2] != ret['frame'][idx2] ):
              logstr = ( 'SCRIPT: ERROR: DATA frame byte number:', idx2, 'incorrect' )
              raise StopScript( ''.join( map( str, logstr ) ) )
              dataFrameValid = False
            idx2+=1

        if( dataFrameValid == False ):
          result = False
          break

        if( msgFlow[idx+3] == 2 ):
          # Disable Transparant Mode Receiving DUT
          options = ( ftdf.FTDF_TRANSPARENT_AUTO_ACK )
          enable = False
          DTS_enableTransparantMode( devId2, enable, options )

    if( ret['msgId'] == ftdf.FTDF_DATA_CONFIRM and
        msgFlow[idx+3] == 3 ):

        res, ret = DTS_getMsg( devId2, responseTimeout )
        if( res == False ):
            raise StopScript( 'SCRIPT: ERROR: No response received from device' )
            break
        elif ret['msgId'] != ftdf.FTDF_DATA_INDICATION:
            logstr = ( 'SCRIPT: ERROR: Expected DATA_INDICATION confirm, instead received ', ret['msgId'] )
            raise StopScript( ''.join( map( str, logstr ) ) )
            break
        elif( ret['msdu'] != msdu ):
            raise StopScript( 'SCRIPT: ERROR: Data frame decryption failed' )
            result = False
            break

    elif ret['msgId'] == ftdf.FTDF_SET_CONFIRM:

      if( ret['status'] != ftdf.FTDF_SUCCESS ):
        result = False
        break

      # Check set request with get request
      msgGet['PIBAttribute'] = msgFlow[idx+1]['PIBAttribute']

      DTS_sndMsg( msgFlow[idx], msgGet )

      res2, ret2 = DTS_getMsg( msgFlow[idx], responseTimeout )
      if( res2 == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        result = False
        break
      elif ret2['msgId'] != ftdf.FTDF_GET_CONFIRM:
        logstr = ( 'SCRIPT: ERROR: Expected GET_CONFIRM, instead received ', ret2['msgId'] )
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False
        break
      elif ret2['PIBAttributeValue'] != msgFlow[idx+1]['PIBAttributeValue']:
        logstr = ( 'SCRIPT: ERROR: Incorrect set PIBAttribute: ', msgGet['PIBAttribute'] )
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False
        break
    else:
      if( ret['status'] != ftdf.FTDF_SUCCESS ):
        result = False
        break

  idx += 4


if( not result ):
    raise StopScript('SCRIPT: FAILED')
