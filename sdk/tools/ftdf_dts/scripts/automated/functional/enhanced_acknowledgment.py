import sys  #cli arguments
import time  #sleep

from scriptIncludes import *

PANId     = 0x0001
channel   = 11
secLvl    = 1
keyIdMode = 3
keyIndex  = 5
keySource = [0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f]

msgRxOnWhenIdle_ena = {'msgId': ftdf.FTDF_SET_REQUEST,
                       'PIBAttribute': ftdf.FTDF_PIB_RX_ON_WHEN_IDLE,
                       'PIBAttributeValue': True}

keyTable_dev2 = {
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
        'deviceAddress': 0x0010
        }
      ],

      # Device Descriptor Handles (Device Table entrys that this key is for)
      'nrOfDeviceDescriptorHandles': 1,
      'deviceDescriptorHandles': [0],

      # Key Usage Descriptors (Frame types this key may be used on)
      'nrOfKeyUsageDescriptors': 1,
      'keyUsageDescriptors': [
        {
        'frameType': ftdf.FTDF_DATA_FRAME,
        'commandFrameId': 0
        }
      ],

      # Key
      'key': [ 0xC0, 0xC1, 0xC2, 0xC3, 0xC4, 0xC5, 0xC6, 0xC7,
           0xC8, 0xC9, 0xCA, 0xCB, 0xCC, 0xCD, 0xCE, 0xCF ]
    }
  ]
}

securityLevelTable_dev2 = {
  'nrOfSecurityLevelDescriptors': 1,
  'securityLevelDescriptors': [
    {
    'frameType': ftdf.FTDF_DATA_FRAME,
    'commandFrameId': 0,
    'securityMinimum': 1,
    'deviceOverrideSecurityMinimum': 0,
    'allowedSecurityLevels': 0
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
msgSET_SecurityDisabled = {
  'msgId': ftdf.FTDF_SET_REQUEST,
  'PIBAttribute': ftdf.FTDF_PIB_SECURITY_ENABLED,
  'PIBAttributeValue': False
}

msgSET_Dev2_SecurityKeyTable = {
  'msgId': ftdf.FTDF_SET_REQUEST,
  'PIBAttribute': ftdf.FTDF_PIB_KEY_TABLE,
  'PIBAttributeValue': keyTable_dev2
}

msgSET_Dev2_SecurityLevelTable = {
  'msgId': ftdf.FTDF_SET_REQUEST,
  'PIBAttribute': ftdf.FTDF_PIB_SECURITY_LEVEL_TABLE,
  'PIBAttributeValue': securityLevelTable_dev2
}

msgSET_Dev2_SecurityDeviceTable = {
  'msgId': ftdf.FTDF_SET_REQUEST,
  'PIBAttribute': ftdf.FTDF_PIB_DEVICE_TABLE,
  'PIBAttributeValue': deviceTable_dev2
}

msgSET_SecurityDefaultKeySource = {
  'msgId': ftdf.FTDF_SET_REQUEST,
  'PIBAttribute': ftdf.FTDF_PIB_DEFAULT_KEY_SOURCE,
  'PIBAttributeValue': [0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f]
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
      # Set security tables
      ##################################
      devId2, msgSET_SecurityDefaultKeySource, ftdf.FTDF_SET_CONFIRM,
      devId2, msgSET_Dev2_SecurityKeyTable, ftdf.FTDF_SET_CONFIRM,
      devId2, msgSET_Dev2_SecurityLevelTable, ftdf.FTDF_SET_CONFIRM,
      devId2, msgSET_Dev2_SecurityDeviceTable, ftdf.FTDF_SET_CONFIRM,
      devId2, msgSET_SecurityEnabled, ftdf.FTDF_SET_CONFIRM,

      ##################################
      # Set rx on when idle
      ##################################
      devId1, msgRxOnWhenIdle_ena, ftdf.FTDF_SET_CONFIRM,
      devId2, msgRxOnWhenIdle_ena, ftdf.FTDF_SET_CONFIRM )


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
# Enable transparent mode
##################################
DTS_enableTransparantMode( devId1, True, ftdf.FTDF_TRANSPARENT_PASS_ALL_FRAME_TYPES |
                                         ftdf.FTDF_TRANSPARENT_PASS_ALL_NO_DEST_ADDR |
                                         ftdf.FTDF_TRANSPARENT_ENABLE_FCS_GENERATION )

##################################
# Prepare transparent secured data frame with AR=1
##################################
fc_frameType    = 0x0001 # dataframe
fc_secEna       = 0x0008 # secured
fc_ar           = 0x0020 # ack request
fc_dstAddrMode  = 0x0800 # short
fc_frameVersion = 0x2000 # frame version 2
fc_srcAddrMode  = 0x8000 # short

frameControl = ( fc_frameType | fc_secEna | fc_ar | fc_dstAddrMode | fc_frameVersion | fc_srcAddrMode )

fc_byte0 = frameControl & 0x00ff
fc_byte1 = frameControl >> 8

sh_secLvl    = 0x04 # 4 disables the use of MIC
sh_keyIdMode = 0x18 # keyIdMode 3

securityHeader = ( sh_secLvl | sh_keyIdMode )

dataFrame = [
    fc_byte0, # frame control
    fc_byte1,
    0x01, # SN
    0x01, # Dest PAN ID
    0x00,
    0x20, # Dest address
    0x00,
    0x10, # Source address
    0x00,
    securityHeader, # Security header
    0x00, # Frame counter (4 bytes)
    0x00,
    0x00,
    0x01,
    0x08, # Key source (8 bytes)
    0x09,
    0x0a,
    0x0b,
    0x0c,
    0x0d,
    0x0e,
    0x0f,
    0x05, # Key index
    0x01, # payload
    0x02,
    0x03,
    0x04,
    0x05,
    0x00, # FCS
    0x00
]

##################################
# Send transparent frame
##################################
DTS_sendFrameTransparant( devId1, len( dataFrame ), dataFrame, channel, False, 1 )

# Confirm
res, ret = DTS_getMsg( devId1, responseTimeout )
if ( res == False ):
    raise StopScript('No response from device' )
elif ret['status'] != ftdf.FTDF_SUCCESS:
    raise StopScript( 'Transparent frame could not be sent' )

##################################
# Receive transparent an secured enhanced acknowledgment frame
##################################
res, ret = DTS_getMsg( devId1, responseTimeout )
if ( res == False ):
    raise StopScript('No response from device' )
elif ((ret['frame'][0] & 0x0008) != 0x0008 or (ret['frame'][0] & 0x0002) != 0x0002):
    raise StopScript('Expected enhanced acknowledgment frame')

##################################
# Receive data indication
##################################
res, ret = DTS_getMsg( devId2, responseTimeout )
if res == False or ret['msgId'] != ftdf.FTDF_DATA_INDICATION:
    raise StopScript("Expected FTDF_DATA_INDICATION")



##################################
# Disable security
##################################
DTS_sndMsg( devId2, msgSET_SecurityDisabled )

res, ret = DTS_getMsg( devId2, responseTimeout )
if res == False or ret['msgId'] != ftdf.FTDF_SET_CONFIRM:
    raise StopScript("Expected FTDF_SET_CONFIRM")


##################################
# Prepare transparent non-secure data frame with AR=1
##################################
fc_frameType    = 0x0001 # dataframe
fc_secEna       = 0x0000 # non-secured
fc_ar           = 0x0020 # ack request
fc_dstAddrMode  = 0x0800 # short
fc_frameVersion = 0x2000 # frame version 2
fc_srcAddrMode  = 0x8000 # short

frameControl = ( fc_frameType | fc_secEna | fc_ar | fc_dstAddrMode | fc_frameVersion | fc_srcAddrMode )

fc_byte0 = frameControl & 0x00ff
fc_byte1 = frameControl >> 8

dataFrame = [
    fc_byte0, # frame control
    fc_byte1,
    0x02, # SN
    0x01, # Dest PAN ID
    0x00,
    0x20, # Dest address
    0x00,
    0x10, # Source address
    0x00,
    0x01, # payload
    0x02,
    0x03,
    0x04,
    0x05,
    0x00, # FCS
    0x00
]

##################################
# Send transparent frame
##################################
DTS_sendFrameTransparant( devId1, len( dataFrame ), dataFrame, channel, False, 2 )

# Confirm
res, ret = DTS_getMsg( devId1, responseTimeout )
if ( res == False ):
    raise StopScript('No response from device' )
elif ret['status'] != ftdf.FTDF_SUCCESS:
    raise StopScript( 'Transparent frame could not be sent' )

##################################
# Receive transparent an unsecured enhanced acknowledgment frame
##################################
res, ret = DTS_getMsg( devId1, responseTimeout )
if ( res == False ):
    raise StopScript('No response from device' )
elif ((ret['frame'][0] & 0x0008) != 0 or (ret['frame'][0] & 0x0002) != 0x0002):
    raise StopScript('Expected enhanced acknowledgment frame')

##################################
# Receive data indication
##################################
res, ret = DTS_getMsg( devId2, responseTimeout )
if res == False or ret['msgId'] != ftdf.FTDF_DATA_INDICATION:
    raise StopScript("Expected FTDF_DATA_INDICATION")


