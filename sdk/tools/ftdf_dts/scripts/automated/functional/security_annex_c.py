# Load-drop 2 Test: Security AnnexC

# This script will test the example frames of IEEE 802.15.4-2011 AnnexC 2.2 and AnnexC 2.3

import sys    #cli arguments
import time    #sleep

from scriptIncludes import *

# SCRIPT Settings:
keyIdMode = 0


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
                'deviceAddrMode': ftdf.FTDF_EXTENDED_ADDRESS,
                'devicePANId': 0x4321,
                'deviceAddress': 0xacde480000000002
                }
            ],

            # Device Descriptor Handles (Device Table entrys that this key is for)
            'nrOfDeviceDescriptorHandles': 1,
            'deviceDescriptorHandles': [0],

            # Key Usage Descriptors (Frame types this key may be used on)
            'nrOfKeyUsageDescriptors': 2,
            'keyUsageDescriptors': [
                {
                'frameType': ftdf.FTDF_DATA_FRAME,
                'commandFrameId': 0
                },
                {
                'frameType': ftdf.FTDF_MAC_COMMAND_FRAME,
                'commandFrameId': ftdf.FTDF_COMMAND_ASSOCIATION_REQUEST
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
                'deviceAddrMode': ftdf.FTDF_EXTENDED_ADDRESS,
                'devicePANId': 0x4321,
                'deviceAddress': 0xacde480000000002
                }
            ],

            # Device Descriptor Handles (Device Table entrys that this key is for)
            'nrOfDeviceDescriptorHandles': 1,
            'deviceDescriptorHandles': [0],

            # Key Usage Descriptors (Frame types this key may be used on)
            'nrOfKeyUsageDescriptors': 2,
            'keyUsageDescriptors': [
                {
                'frameType': ftdf.FTDF_DATA_FRAME,
                'commandFrameId': 0
                },
                {
                'frameType': ftdf.FTDF_MAC_COMMAND_FRAME,
                'commandFrameId': ftdf.FTDF_COMMAND_ASSOCIATION_REQUEST
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
    'nrOfSecurityLevelDescriptors': 2,
    'securityLevelDescriptors': [
        {
        'frameType': ftdf.FTDF_DATA_FRAME,
        'commandFrameId': 0,
        'securityMinimum': 1,
        'deviceOverrideSecurityMinimum': 0,
        'allowedSecurityLevels': 0
        },
        {
        'frameType': ftdf.FTDF_MAC_COMMAND_FRAME,
        'commandFrameId': ftdf.FTDF_COMMAND_ASSOCIATION_REQUEST,
        'securityMinimum': 1,
        'deviceOverrideSecurityMinimum': 0,
        'allowedSecurityLevels': 0
        }
    ]
}

securityLevelTable_dev2 = {
    'nrOfSecurityLevelDescriptors': 2,
    'securityLevelDescriptors': [
        {
        'frameType': ftdf.FTDF_DATA_FRAME,
        'commandFrameId': 0,
        'securityMinimum': 1,
        'deviceOverrideSecurityMinimum': 0,
        'allowedSecurityLevels': 0
        },
        {
        'frameType': ftdf.FTDF_MAC_COMMAND_FRAME,
        'commandFrameId': ftdf.FTDF_COMMAND_ASSOCIATION_REQUEST,
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
            'PANId': 0x4321,
            'shortAddress': 0x0002,
            'extAddress': 0xacde480000000002,
            'frameCounter': 0,
            'exempt': False # If minimum security level overiding is needed
        }
    ]
}

deviceTable_dev2 = {
    'nrOfDeviceDescriptors': 1,
    'deviceDescriptors': [
        {
            'PANId': 0x4321,
            'shortAddress': 0x0001,
            'extAddress': 0xacde480000000001,
            'frameCounter': 0,
            'exempt': False # If minimum security level overiding is needed
        }
    ]
}


# Frames definition:
# Data frame
msdu = [0x61, 0x62, 0x63, 0x64]
msgDATA_REQUEST = { 
    'msgId': ftdf.FTDF_DATA_REQUEST,
    'srcAddrMode': ftdf.FTDF_EXTENDED_ADDRESS,
    'dstAddrMode': ftdf.FTDF_EXTENDED_ADDRESS,
    'dstPANId': 0x4321,
    'dstAddr': 0xacde480000000002,
    'msduLength': len( msdu ),
    'msdu': msdu,
    'msduHandle': 1,
    'ackTX': False,
    'GTSTX': False,
    'indirectTX': False,
    'securityLevel': 4,
    'keyIdMode': keyIdMode,
    'keySource': [0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f],
    'keyIndex': 5,
    'frameControlOptions': 0,
    'headerIEList': 0,
    'payloadIEList': 0,
    'sendMultiPurpose': False }

# Command frame (Association Request)
msgASSOCIATE_REQUEST = {
    'msgId': ftdf.FTDF_ASSOCIATE_REQUEST,
    'channelNumber': 11,
    'channelPage': 0,
    'coordAddrMode': ftdf.FTDF_EXTENDED_ADDRESS,
    'coordPANId': 0x4321,
    'coordAddr': 0xacde480000000002,
    'capabilityInformation': 0xCE,
    'securityLevel': 6,
    'keyIdMode': keyIdMode,
    'keySource': [0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f],
    'keyIndex': 5,
    'channelOffset': 0,
    'hoppingSequenceId': 0
}


# Message defines:
msgSET_PANId1 = { 'msgId': ftdf.FTDF_SET_REQUEST,
                  'PIBAttribute': ftdf.FTDF_PIB_PAN_ID,
                  'PIBAttributeValue': 0xFFFF }

msgSET_PANId2 = { 'msgId': ftdf.FTDF_SET_REQUEST,
                  'PIBAttribute': ftdf.FTDF_PIB_PAN_ID,
                  'PIBAttributeValue': 0x4321 }

msgSET_Dev1_ExtendedAddress = { 'msgId': ftdf.FTDF_SET_REQUEST,
                                'PIBAttribute': ftdf.FTDF_PIB_EXTENDED_ADDRESS,
                                'PIBAttributeValue': 0xacde480000000001 }

msgSET_Dev2_ExtendedAddress = { 'msgId': ftdf.FTDF_SET_REQUEST,
                                'PIBAttribute': ftdf.FTDF_PIB_EXTENDED_ADDRESS,
                                'PIBAttributeValue': 0xacde480000000002 }

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

msgSET_macFrameCounter = {
    'msgId': ftdf.FTDF_SET_REQUEST,
    'PIBAttribute': ftdf.FTDF_PIB_FRAME_COUNTER,
    'PIBAttributeValue': 5
}

msgSET_DSN = {
    'msgId': ftdf.FTDF_SET_REQUEST,
    'PIBAttribute': ftdf.FTDF_PIB_DSN,
    'PIBAttributeValue': 132
}


# RESET DUT's
msg = {'msgId': ftdf.FTDF_RESET_REQUEST,
       'setDefaultPIB': 1}

DTS_sndMsg( 1, msg )
DTS_sndMsg( 2, msg )

res1, ret1 = DTS_getMsg( 1, 1 )
res2, ret2 = DTS_getMsg( 2, 1 )
if (res1 == False or res2 == False):
    raise stopScript('SCRIPT: ERROR: No response received from device')
elif (ret1['msgId'] != ftdf.FTDF_RESET_CONFIRM or
      ret2['msgId'] != ftdf.FTDF_RESET_CONFIRM):
    logstr = ("SCRIPT: ERROR: Incorrect response received from device: ret1=%s ret2=%s" % (ret1['msgId'],ret2['msgId']))
    raise StopScript( ''.join( map( str, logstr ) ) )


# Enable Transparant Mode on receiving DUT
transparantOptions = (
    ftdf.FTDF_TRANSPARENT_PASS_ALL_FRAME_TYPES |
    ftdf.FTDF_TRANSPARENT_PASS_ALL_FRAME_VERSION |
    ftdf.FTDF_TRANSPARENT_AUTO_ACK |
    ftdf.FTDF_TRANSPARENT_PASS_ALL_ADDR )
enable = True
DTS_enableTransparantMode( devId2, enable, transparantOptions )


# Message order
msgFlow = ( devId1, msgSET_PANId2, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_PANId2, ftdf.FTDF_SET_CONFIRM,

            devId1, msgSET_Dev1_ExtendedAddress, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_Dev2_ExtendedAddress, ftdf.FTDF_SET_CONFIRM,

            devId1, msgSET_SecurityEnabled, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_SecurityEnabled, ftdf.FTDF_SET_CONFIRM,

            devId1, msgSET_Dev1_SecurityKeyTable, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_Dev2_SecurityKeyTable, ftdf.FTDF_SET_CONFIRM,

            devId1, msgSET_Dev1_SecurityLevelTable, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_Dev2_SecurityLevelTable, ftdf.FTDF_SET_CONFIRM,

            devId1, msgSET_Dev1_SecurityDeviceTable, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_Dev2_SecurityDeviceTable, ftdf.FTDF_SET_CONFIRM,

            devId2, msgRxEnable_On, ftdf.FTDF_RX_ENABLE_CONFIRM,

            devId1, msgSET_macFrameCounter, ftdf.FTDF_SET_CONFIRM, # For geting the correct security frame counter value as in the AnnexC examples

            devId1, msgSET_DSN, ftdf.FTDF_SET_CONFIRM, # For geting the correct frame sequence value as in the AnnexC examples

            devId1, msgDATA_REQUEST, ftdf.FTDF_DATA_CONFIRM,

            devId1, msgSET_PANId1, ftdf.FTDF_SET_CONFIRM,

            devId1, msgSET_DSN, ftdf.FTDF_SET_CONFIRM, # For geting the correct frame sequence value as in the AnnexC examples

            devId1, msgSET_macFrameCounter, ftdf.FTDF_SET_CONFIRM, # For geting the correct security frame counter value as in the AnnexC examples

            devId1, msgASSOCIATE_REQUEST, ftdf.FTDF_ASSOCIATE_CONFIRM
)


idx = 0
dataFrameValid = False
commandFrameValid = False

while( idx < len( msgFlow ) ):
    # Send message
    DTS_sndMsg( msgFlow[idx], msgFlow[idx+1] )

    # Get message confirm
    res, ret = DTS_getMsg( msgFlow[idx], responseTimeout )

    # Check received expected confirm
    if( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        break
    elif ret['msgId'] != msgFlow[idx+2]:
        logstr = ( 'SCRIPT: ERROR: Expected ', msgFlow[idx+2], ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
        raise StopScript( ''.join( map( str, logstr ) ) )
        break
    else:
        if ret['msgId'] == ftdf.FTDF_SET_CONFIRM:
            if( ret['status'] != ftdf.FTDF_SUCCESS ):
                break
            # Check set request with get request
            msgGet['PIBAttribute'] = msgFlow[idx+1]['PIBAttribute']

            DTS_sndMsg( msgFlow[idx], msgGet )

            res, ret = DTS_getMsg( msgFlow[idx], responseTimeout )

            if( res == False ):
                raise StopScript( 'SCRIPT: ERROR: No response received from device' )
                break
            elif ret['msgId'] != ftdf.FTDF_GET_CONFIRM:
                logstr = ( 'SCRIPT: ERROR: Expected GET_CONFIRM, instead received ', ret['msgId'] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                break
            elif ret['PIBAttributeValue'] != msgFlow[idx+1]['PIBAttributeValue']:
                logstr = ( 'SCRIPT: ERROR: Incorrect set PIBAttribute: ', msgGet['PIBAttribute'] );
                raise StopScript( ''.join( map( str, logstr ) ) )
                break

        elif( ret['msgId'] == ftdf.FTDF_DATA_CONFIRM ):
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
                expectedFrame = [
                    0x49, 0xDC, 0x84, 0x21, 0x43, 0x02, 0x00, 0x00,
                    0x00, 0x00, 0x48, 0xDE, 0xAC, 0x01, 0x00, 0x00,
                    0x00, 0x00, 0x48, 0xDE, 0xAC, 0x04, 0x05, 0x00,
                    0x00, 0x00, 0xD4, 0x3E, 0x02, 0x2B, 0xc4, 0x26
                ]
                dataFrameValid = True
                # Print received frame
                idx2 = 0
                while( idx2 < len( ret['frame'] ) ):
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

        elif ret['msgId'] == ftdf.FTDF_ASSOCIATE_CONFIRM:
            res, ret = DTS_getMsg( devId2, responseTimeout )

            if( res == False ):
                raise StopScript( 'SCRIPT: ERROR: No response received from device' )
                break
            elif ret['msgId'] != ftdf.FTDF_TRANSPARENT_INDICATION:
                logstr = ( 'SCRIPT: ERROR: Expected ftdf.FTDF_TRANSPARENT_INDICATION confirm, instead received ', ret['msgId'] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                break
            else:
                # Check received command frame
                expectedFrame = [
                    0x2B, 0xDC, 0x84, 0x21, 0x43, 0x02, 0x00, 0x00,
                    0x00, 0x00, 0x48, 0xDE, 0xAC, 0xFF, 0xFF, 0x01,
                    0x00, 0x00, 0x00, 0x00, 0x48, 0xDE, 0xAC, 0x06,
                    0x05, 0x00, 0x00, 0x00, 0x01, 0xD8, 0x4F, 0xDE,
                    0x52, 0x90, 0x61, 0xF9, 0xC6, 0xF1, 0xe4, 0x4f
                ]
                commandFrameValid = True

                # Print received frame
                idx2 = 0
                while( idx2 < len( ret['frame'] ) ):
                    idx2+=1

                # Check frame length
                if( len( expectedFrame ) != len( ret['frame'] ) ):
                    raise StopScript( 'SCRIPT: ERROR: COMMAND frame length incorrect' )
                    commandFrameValid = False
                # Check frame bytes
                else:
                    idx2 = 0
                    while( idx2 < len( expectedFrame ) ):
                        if( expectedFrame[idx2] != ret['frame'][idx2] ):
                            logstr = ( 'SCRIPT: ERROR: COMMAND frame byte number:', idx2, 'incorrect' )
                            raise StopScript( ''.join( map( str, logstr ) ) )
                            commandFrameValid = False
                        idx2+=1

        else:
            if( ret['status'] != ftdf.FTDF_SUCCESS ):
                break

    idx += 3

while True:
    res, ret = DTS_getMsg( devId2, responseTimeout )
    if res == False:
        break

DTS_enableTransparantMode( devId2, False, 0 )

if ((not dataFrameValid) or (not commandFrameValid)):
    raise StopScript('SCRIPT: FAILED')
