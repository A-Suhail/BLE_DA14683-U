# Load-drop 2 Test: Security

#

import sys    #cli arguments
import time    #sleep

from scriptIncludes import *

# SCRIPT Settings:
keyIdMode = 3


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
        'securityMinimum': 0,                    # 0 is Unsecured frames allowed
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
        'securityMinimum': 0,                    # 0 is Unsecured frames allowed
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


# Msg definition:
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

# Message order
msgFlow = ( devId1, msgRESET, ftdf.FTDF_RESET_CONFIRM,
            devId2, msgRESET, ftdf.FTDF_RESET_CONFIRM,
            
            devId1, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
            
            devId1, msgSET_Dev1_ShortAddress, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_Dev2_ShortAddress, ftdf.FTDF_SET_CONFIRM,

            devId1, msgSET_Dev1_ExtendedAddress, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_Dev2_ExtendedAddress, ftdf.FTDF_SET_CONFIRM,
            
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

            devId2, msgRxEnable_On, ftdf.FTDF_RX_ENABLE_CONFIRM )


idx = 0
result = True
while( idx < len( msgFlow ) ):
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
        logstr = ( 'SCRIPT: ERROR: Expected ', msgFlow[idx+2], ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False
        break
    else:
        if ret['msgId'] == ftdf.FTDF_SET_CONFIRM:

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

    idx += 3


# Frames definition:

# Frame Control:
#frameControl_FrameType            = 0x0000 # Beacon
frameControl_FrameType            = 0x0001 # DataFrame
#frameControl_FrameType            = 0x0002 # Acknowledgment
#frameControl_FrameType            = 0x0003 # MAC command
#frameControl_FrameType            = 0x0004 # LLDN
#frameControl_FrameType            = 0x0005 # Multipurpose

#frameControl_SecurityEnabled    = 0x0008 # Bit: 3 (Yes)
frameControl_SecurityEnabled    = 0x0000 # Bit: 3 (No)

#frameControl_AckReq            = 0x0020 # Bit: 5 (Yes)
frameControl_AckReq                = 0x0000 # Bit: 5 (No)

#frameControl_PANidCompression    = 0x0040 # Bit: 6 (Yes)
frameControl_PANidCompression    = 0x0000 # Bit: 6 (No)

#frameControl_SequenceNrSup        = 0x0100 # Bit: 8 (Yes) # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved
frameControl_SequenceNrSup        = 0x0000 # Bit: 8 (No)  # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved

#frameControl_IEListPresent        = 0x0200 # Bit: 9 (Yes) # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved
frameControl_IEListPresent        = 0x0000 # Bit: 9 (No) # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved

frameControl_dstAddrMode        = 0x0800 # Bit: 10-11 (Short)

#frameControl_FrameVersion        = 0x0000 # Bit: 12-13 (IEEE Std 802.15.4-2003)
frameControl_FrameVersion        = 0x1000 # Bit: 12-13 (IEEE Std 802.15.4-2006)
#frameControl_FrameVersion        = 0x2000 # Bit: 12-13 (IEEE Std 802.15.4)
#frameControl_FrameVersion        = 0x3000 # Bit: 12-13 (Reserved)

frameControl_srcAddrMode        = 0x8000 # Bit: 14-15 (Short)

frameControl = ( frameControl_FrameType |
                 frameControl_SecurityEnabled |
                 frameControl_AckReq |
                 frameControl_PANidCompression |
                 frameControl_SequenceNrSup |
                 frameControl_IEListPresent |
                 frameControl_dstAddrMode |
                 frameControl_FrameVersion |
                 frameControl_srcAddrMode )

frameControlByte0 = frameControl & 0x00ff
frameControlByte1 = frameControl >> 8

# Auxiliary security header:
frameAuxSecCon_SecurityLevel            = 0x04 # Bit 0-2 (Tip: using 4 disables the use of MIC (the need to calculate and add the association bytes in the transparent send frame))
frameAuxSecCon_KeyIdentifierMode        = 0x18 # Bit 3-4
frameAuxSecCon_FrameCounterSuppression    = 0x00 # Bit 5 (No Suppression)
frameAuxSecCon_FrameCounterSize            = 0x00 # Bit 6 (4 Byte)
frameAuxSecCon_Reserved                    = 0x00 # Bit 7

frameAuxSecCon = (    frameAuxSecCon_SecurityLevel |
                    frameAuxSecCon_KeyIdentifierMode |
                    frameAuxSecCon_FrameCounterSuppression |
                    frameAuxSecCon_FrameCounterSize |
                    frameAuxSecCon_Reserved )

frame = (
    frameControlByte0,
    frameControlByte1, # Frame Control
    0x01, # Sequence number
    0x01, # Destination PanId
    0x00,
    0x20, # Destination address
    0x00,
    0x01, # Source PanId
    0x00,
    0x10, # Source address
    0x00,
    frameAuxSecCon, # Auxiliary security header: Security Control
    0x00, # Auxiliary security header: Frame Counter (4 Byte)
    0x00,
    0x00,
    0x01,
    0x08, # Key Source (8 Byte)
    0x09,
    0x0a,
    0x0b,
    0x0c,
    0x0d,
    0x0e,
    0x0f,
    0x05, # Key Index
    0xFF, # Payload
    0xFF, # MIC32 or just extra payload
    0xFF,
    0xFF,
    0xFF,
    0x00, # FCS
    0x00
)


# Enable Transparant Mode
options = ( ftdf.FTDF_TRANSPARENT_PASS_ALL_FRAME_TYPES |
            ftdf.FTDF_TRANSPARENT_PASS_ALL_FRAME_VERSION |
            ftdf.FTDF_TRANSPARENT_ENABLE_FCS_GENERATION |
            ftdf.FTDF_TRANSPARENT_PASS_ALL_ADDR )

enable = True
DTS_enableTransparantMode( devId1, enable, options )


# ----------------- Send Frame Transparant:
length = len( frame )
channel = 11
handle = 0 # Application can pas data using this handle to itself
csmaSuppress = ftdf.FTDF_FALSE

DTS_sendFrameTransparant( devId1, length, frame, channel, csmaSuppress, handle )

res, ret = DTS_getMsg( devId1, responseTimeout )

if( res == False ):
    raise StopScript('SCRIPT: ERROR: No response received from device')
    result = False
elif ret['msgId'] != ftdf.FTDF_TRANSPARENT_CONFIRM:
    logstr = ( 'SCRIPT: ERROR: Expected ftdf.FTDF_TRANSPARENT_CONFIRM instead received ', ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )
    result = False
else:
    if( ret['status'] != ftdf.FTDF_SUCCESS ):
        result = False
    else:
        res, ret = DTS_getMsg( devId2, responseTimeout )
        if( res == False ):
            raise StopScript('SCRIPT: ERROR: No response received from device')
            result = False
        elif ret['msgId'] != ftdf.FTDF_COMM_STATUS_INDICATION:
            logstr = ( 'SCRIPT: ERROR: Expected COMM_STATUS_INDICATION instead received ', ret['msgId'] )
            raise StopScript( ''.join( map( str, logstr ) ) )
            result = False
        else:
            if(ret['securityLevel'] != 0 ):
                raise StopScript('SCRIPT: ERROR: securityLevel should be 0')
                result = False


if( not result ):
    raise StopScript('SCRIPT: FAILED')
