import sys, datetime, time
from scriptIncludes import *

nrOfFrames = 10000

msgSET_rxOnWhenIdle = { 'msgId': ftdf.FTDF_SET_REQUEST,
                        'PIBAttribute': ftdf.FTDF_PIB_RX_ON_WHEN_IDLE,
                        'PIBAttributeValue': True }

##############################################
# Security tables
##############################################
# Key Table
keyTable_dev1 = {
  'nrOfKeyDescriptors': 1,
  'keyDescriptors': [
    {
      # Key Id Lookup Descriptors (one of the descriptors need to match)
      'nrOfKeyIdLookupDescriptors': 1,
      'keyIdLookupDescriptors': [
        {
        'keyIdMode': 3,
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
        'keyIdMode': 3,
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



# Message order
msgFlow = ( devId1, msgRESET, ftdf.FTDF_RESET_CONFIRM,
            devId2, msgRESET, ftdf.FTDF_RESET_CONFIRM,

            devId1, msgSET_Dev1_ShortAddress, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_Dev2_ShortAddress, ftdf.FTDF_SET_CONFIRM,

            devId1, msgSET_Dev1_ExtendedAddress, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_Dev2_ExtendedAddress, ftdf.FTDF_SET_CONFIRM,

            devId1, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,

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

            devId1, msgSET_SecurityEnabled, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_SecurityEnabled, ftdf.FTDF_SET_CONFIRM,

            devId2, msgSET_rxOnWhenIdle, ftdf.FTDF_SET_CONFIRM )


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



logmsg = 'Normal secure performance (acknowledged):\n'
####################################
# 29 + 16
####################################
logmsg = logmsg + 'Frame size 29 + 16 : '

msdu = []
for i in range( 16 ):
    msdu.append( i )

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
    'securityLevel': 1,
    'keyIdMode': 3,
    'keySource': [0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f],
    'keyIndex': 5,
    'frameControlOptions': 0,
    'headerIEList': 0,
    'payloadIEList': 0,
    'sendMultiPurpose': False
}

DTS_setQueueParameters( devId1,
                       ftdf.DTS_QUEUE_SND,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       nrOfFrames - 1, 0 )

DTS_setQueueParameters( devId2,
                       ftdf.DTS_QUEUE_RCV,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       0, 0 )

DTS_sndMsg( devId1, msgDATA )

# Get current time
t1 = datetime.datetime.now( )

# start sending of frames
DTS_setQueueEnable( devId1, True )

res, ret = DTS_getMsg( devId1, 100 )

if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgTotal'] != nrOfFrames:
    raise StopScript( 'Expected ' + str(nrOfFrames) + ' sent messages' )
elif ret['msgSuccess'] != nrOfFrames:
    raise StopScript( 'Expected ' + str(nrOfFrames) + ' successful messages' )


# get time after end of test
t2 = datetime.datetime.now( )
deltat = t2 - t1
fps = nrOfFrames / deltat.total_seconds()

logmsg = logmsg + str(nrOfFrames) + ' frames in ' + str( deltat.total_seconds() ) +\
         ' seconds (' + str(int(fps)) + ' frames per second)\n'

time.sleep(2)

DTS_setQueueParameters( devId2,
                       ftdf.DTS_QUEUE_DIS,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       0, 0 )

res, ret = DTS_getMsg( devId2, responseTimeout )

if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgTotal'] != nrOfFrames:
    dtsLog.warning( 'Expected ' + str(nrOfFrames) + ' rcvd messages' )
elif ret['msgSuccess'] != nrOfFrames:
    dtsLog.warning( 'Expected ' + str(nrOfFrames) + ' successful messages' )


####################################
# 29 + 64
####################################
logmsg = logmsg + 'Frame size 29 + 64 : '

msdu = []
for i in range( 64 ):
    msdu.append( i )

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
    'securityLevel': 1,
    'keyIdMode': 3,
    'keySource': [0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f],
    'keyIndex': 5,
    'frameControlOptions': 0,
    'headerIEList': 0,
    'payloadIEList': 0,
    'sendMultiPurpose': False
}

DTS_setQueueParameters( devId1,
                       ftdf.DTS_QUEUE_SND,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       nrOfFrames - 1, 0 )

DTS_setQueueParameters( devId2,
                       ftdf.DTS_QUEUE_RCV,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       0, 0 )

DTS_sndMsg( devId1, msgDATA )

# Get current time
t1 = datetime.datetime.now( )

# start sending of frames
DTS_setQueueEnable( devId1, True )

res, ret = DTS_getMsg( devId1, 100 )

if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgTotal'] != nrOfFrames:
    raise StopScript( 'Expected ' + str(nrOfFrames) + ' sent messages' )
elif ret['msgSuccess'] != nrOfFrames:
    raise StopScript( 'Expected ' + str(nrOfFrames) + ' successful messages' )


# get time after end of test
t2 = datetime.datetime.now( )
deltat = t2 - t1
fps = nrOfFrames / deltat.total_seconds()

logmsg = logmsg + str(nrOfFrames) + ' frames in ' + str( deltat.total_seconds() ) +\
         ' seconds (' + str(int(fps)) + ' frames per second)\n'

time.sleep(2)

DTS_setQueueParameters( devId2,
                       ftdf.DTS_QUEUE_DIS,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       0, 0 )

res, ret = DTS_getMsg( devId2, responseTimeout )

if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgTotal'] != nrOfFrames:
    dtsLog.warning( 'Expected ' + str(nrOfFrames) + ' rcvd messages' )
elif ret['msgSuccess'] != nrOfFrames:
    dtsLog.warning( 'Expected ' + str(nrOfFrames) + ' successful messages' )


####################################
# 29 + 98
####################################
logmsg = logmsg + 'Frame size 29 + 98 : '

msdu = []
for i in range( 98 ):
    msdu.append( i )

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
    'securityLevel': 1,
    'keyIdMode': 3,
    'keySource': [0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f],
    'keyIndex': 5,
    'frameControlOptions': 0,
    'headerIEList': 0,
    'payloadIEList': 0,
    'sendMultiPurpose': False
}

DTS_setQueueParameters( devId1,
                       ftdf.DTS_QUEUE_SND,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       nrOfFrames - 1, 0 )

DTS_setQueueParameters( devId2,
                       ftdf.DTS_QUEUE_RCV,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       0, 0 )

DTS_sndMsg( devId1, msgDATA )

# Get current time
t1 = datetime.datetime.now( )

# start sending of frames
DTS_setQueueEnable( devId1, True )

res, ret = DTS_getMsg( devId1, 100 )

if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgTotal'] != nrOfFrames:
    raise StopScript( 'Expected ' + str(nrOfFrames) + ' sent messages' )
elif ret['msgSuccess'] != nrOfFrames:
    raise StopScript( 'Expected ' + str(nrOfFrames) + ' successful messages' )


# get time after end of test
t2 = datetime.datetime.now( )
deltat = t2 - t1
fps = nrOfFrames / deltat.total_seconds()

logmsg = logmsg + str(nrOfFrames) + ' frames in ' + str( deltat.total_seconds() ) +\
         ' seconds (' + str(int(fps)) + ' frames per second)\n'

time.sleep(2)

DTS_setQueueParameters( devId2,
                       ftdf.DTS_QUEUE_DIS,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       0, 0 )

res, ret = DTS_getMsg( devId2, responseTimeout )

if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgTotal'] != nrOfFrames:
    dtsLog.warning( 'Expected ' + str(nrOfFrames) + ' rcvd messages' )
elif ret['msgSuccess'] != nrOfFrames:
    dtsLog.warning( 'Expected ' + str(nrOfFrames) + ' successful messages' )

logmsg = logmsg + '\nNormal secure performance (unacknowledged):\n'
####################################
# 29 + 16
####################################
logmsg = logmsg + 'Frame size 29 + 16 : '

msdu = []
for i in range( 16 ):
    msdu.append( i )

msgDATA = {
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
    'securityLevel': 1,
    'keyIdMode': 3,
    'keySource': [0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f],
    'keyIndex': 5,
    'frameControlOptions': 0,
    'headerIEList': 0,
    'payloadIEList': 0,
    'sendMultiPurpose': False
}

DTS_setQueueParameters( devId1,
                       ftdf.DTS_QUEUE_SND,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       nrOfFrames - 1, 0 )

DTS_setQueueParameters( devId2,
                       ftdf.DTS_QUEUE_RCV,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       0, 0 )

DTS_sndMsg( devId1, msgDATA )

# Get current time
t1 = datetime.datetime.now( )

# start sending of frames
DTS_setQueueEnable( devId1, True )

res, ret = DTS_getMsg( devId1, 100 )

if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgTotal'] != nrOfFrames:
    raise StopScript( 'Expected ' + str(nrOfFrames) + ' sent messages' )
elif ret['msgSuccess'] != nrOfFrames:
    raise StopScript( 'Expected ' + str(nrOfFrames) + ' successful messages' )


# get time after end of test
t2 = datetime.datetime.now( )
deltat = t2 - t1
fps = nrOfFrames / deltat.total_seconds()

logmsg = logmsg + str(nrOfFrames) + ' frames in ' + str( deltat.total_seconds() ) +\
         ' seconds (' + str(int(fps)) + ' frames per second)\n'

time.sleep(2)

DTS_setQueueParameters( devId2,
                       ftdf.DTS_QUEUE_DIS,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       0, 0 )

res, ret = DTS_getMsg( devId2, responseTimeout )

if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgTotal'] != nrOfFrames:
    dtsLog.warning( 'Expected ' + str(nrOfFrames) + ' rcvd messages' )
elif ret['msgSuccess'] != nrOfFrames:
    dtsLog.warning( 'Expected ' + str(nrOfFrames) + ' successful messages' )


####################################
# 29 + 64
####################################
logmsg = logmsg + 'Frame size 29 + 64 : '

msdu = []
for i in range( 64 ):
    msdu.append( i )

msgDATA = {
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
    'securityLevel': 1,
    'keyIdMode': 3,
    'keySource': [0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f],
    'keyIndex': 5,
    'frameControlOptions': 0,
    'headerIEList': 0,
    'payloadIEList': 0,
    'sendMultiPurpose': False
}

DTS_setQueueParameters( devId1,
                       ftdf.DTS_QUEUE_SND,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       nrOfFrames - 1, 0 )

DTS_setQueueParameters( devId2,
                       ftdf.DTS_QUEUE_RCV,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       0, 0 )

DTS_sndMsg( devId1, msgDATA )

# Get current time
t1 = datetime.datetime.now( )

# start sending of frames
DTS_setQueueEnable( devId1, True )

res, ret = DTS_getMsg( devId1, 100 )

if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgTotal'] != nrOfFrames:
    raise StopScript( 'Expected ' + str(nrOfFrames) + ' sent messages' )
elif ret['msgSuccess'] != nrOfFrames:
    raise StopScript( 'Expected ' + str(nrOfFrames) + ' successful messages' )


# get time after end of test
t2 = datetime.datetime.now( )
deltat = t2 - t1
fps = nrOfFrames / deltat.total_seconds()

logmsg = logmsg + str(nrOfFrames) + ' frames in ' + str( deltat.total_seconds() ) +\
         ' seconds (' + str(int(fps)) + ' frames per second)\n'

time.sleep(2)

DTS_setQueueParameters( devId2,
                       ftdf.DTS_QUEUE_DIS,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       0, 0 )

res, ret = DTS_getMsg( devId2, responseTimeout )

if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgTotal'] != nrOfFrames:
    dtsLog.warning( 'Expected ' + str(nrOfFrames) + ' rcvd messages' )
elif ret['msgSuccess'] != nrOfFrames:
    dtsLog.warning( 'Expected ' + str(nrOfFrames) + ' successful messages' )


####################################
# 29 + 98
####################################
logmsg = logmsg + 'Frame size 29 + 98 : '

msdu = []
for i in range( 98 ):
    msdu.append( i )

msgDATA = {
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
    'securityLevel': 1,
    'keyIdMode': 3,
    'keySource': [0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f],
    'keyIndex': 5,
    'frameControlOptions': 0,
    'headerIEList': 0,
    'payloadIEList': 0,
    'sendMultiPurpose': False
}

DTS_setQueueParameters( devId1,
                       ftdf.DTS_QUEUE_SND,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       nrOfFrames - 1, 0 )

DTS_setQueueParameters( devId2,
                       ftdf.DTS_QUEUE_RCV,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       0, 0 )

DTS_sndMsg( devId1, msgDATA )

# Get current time
t1 = datetime.datetime.now( )

# start sending of frames
DTS_setQueueEnable( devId1, True )

res, ret = DTS_getMsg( devId1, 100 )

if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgTotal'] != nrOfFrames:
    raise StopScript( 'Expected ' + str(nrOfFrames) + ' sent messages' )
elif ret['msgSuccess'] != nrOfFrames:
    raise StopScript( 'Expected ' + str(nrOfFrames) + ' successful messages' )


# get time after end of test
t2 = datetime.datetime.now( )
deltat = t2 - t1
fps = nrOfFrames / deltat.total_seconds()

logmsg = logmsg + str(nrOfFrames) + ' frames in ' + str( deltat.total_seconds() ) +\
         ' seconds (' + str(int(fps)) + ' frames per second)\n'

time.sleep(2)

DTS_setQueueParameters( devId2,
                       ftdf.DTS_QUEUE_DIS,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       0, 0 )

res, ret = DTS_getMsg( devId2, responseTimeout )

if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgTotal'] != nrOfFrames:
    dtsLog.warning( 'Expected ' + str(nrOfFrames) + ' rcvd messages' )
elif ret['msgSuccess'] != nrOfFrames:
    dtsLog.warning( 'Expected ' + str(nrOfFrames) + ' successful messages' )


# Return performance results via exception
raise PerformanceResults( logmsg )
