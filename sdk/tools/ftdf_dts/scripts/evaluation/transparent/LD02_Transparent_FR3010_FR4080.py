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
            'nrOfKeyUsageDescriptors': 6,
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
                },
                {
                'frameType': ftdf.FTDF_MAC_COMMAND_FRAME,
                'commandFrameId': 1
                },
                {
                'frameType': ftdf.FTDF_MAC_COMMAND_FRAME,
                'commandFrameId': 2
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
            'nrOfKeyUsageDescriptors': 6,
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
                },
                {
                'frameType': ftdf.FTDF_MAC_COMMAND_FRAME,
                'commandFrameId': 1
                },
                {
                'frameType': ftdf.FTDF_MAC_COMMAND_FRAME,
                'commandFrameId': 2
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
    'nrOfSecurityLevelDescriptors': 6,
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
        }
    ]
}

securityLevelTable_dev2 = {
    'nrOfSecurityLevelDescriptors': 6,
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
    'securityLevel': 5,
    'keyIdMode': keyIdMode,
    'keySource': [0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f],
    'keyIndex': 5,
    'frameControlOptions': 0,
    'headerIEList': 0,
    'payloadIEList': 0,
    'sendMultiPurpose': False }
    
# Data frame MultiPurpose
msgDATA_MultiPurpose = {
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
    'frameControlOptions': ftdf.FTDF_PAN_ID_PRESENT, # Includes destination PAN ID incase Multi Purpose frame
    'headerIEList': 0,
    'payloadIEList': 0,
    'sendMultiPurpose': True }
    
msgDATA_Ack = {
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
    
# Data frame MultiPurpose
msgDATA_MultiPurpose_Ack = {
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
    'frameControlOptions': ftdf.FTDF_PAN_ID_PRESENT, # Includes destination PAN ID incase Multi Purpose frame
    'headerIEList': 0,
    'payloadIEList': 0,
    'sendMultiPurpose': True }

# Command frame (Association Request)
msgASSOCIATE_Request = {
    'msgId': ftdf.FTDF_ASSOCIATE_REQUEST,
    'channelNumber': 11,
    'channelPage': 0,
    'coordAddrMode': ftdf.FTDF_EXTENDED_ADDRESS,
    'coordPANId': 0x0001,
    'coordAddr': 0x0020,
    'capabilityInformation': 0xCE,
    'securityLevel': 6,
    'keyIdMode': keyIdMode,
    'keySource': [0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f],
    'keyIndex': 5,
    'channelOffset': 0,
    'hoppingSequenceId': 0
}
msgASSOCIATE_Response = {
    'msgId': ftdf.FTDF_ASSOCIATE_RESPONSE,
    'deviceAddress': 0x0000000000000010,
    'assocShortAddress': 0x0010,
    'status': ftdf.FTDF_SUCCESS,
    'fastA': False,
    'securityLevel': 6,
    'keyIdMode': keyIdMode,
    'keySource': [0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f],
    'keyIndex': 5,
    'channelOffset': 0,
    'hoppingSequenceLength': 0,
    'hoppingSequence': 0
}

# Beacon frame
msgBEACON = {
    'msgId': ftdf.FTDF_BEACON_REQUEST,
    'beaconType': ftdf.FTDF_NORMAL_BEACON,
    'channel': 11,
    'channelPage': 0,
    'superframeOrder': 0xff,
    'beaconSecurityLevel': 5,
    'beaconKeyIdMode': keyIdMode,
    'beaconKeySource': [0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f],
    'beaconKeyIndex': 5,
    'dstAddrMode': ftdf.FTDF_SHORT_ADDRESS,
    'dstAddr': 0x0020,
    'BSNSuppression': False
}

msgSTART = {
    'msgId': ftdf.FTDF_START_REQUEST,
    'PANId': 0x0001,
    'channelNumber': 11,
    'channelPage': 0,
    'startTime': 0x000000,
    'beaconOrder': 15,
    'superframeOrder': 15,
    'PANCoordinator': True,
    'batteryLifeExtension':False,
    'coordRealignment': False,
    'coordRealignSecurityLevel': 0,
    'coordRealignKeyIdMode': keyIdMode,
    'coordRealignKeySource':[0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f],
    'coordRealignKeyIndex': 5,
    'beaconSecurityLevel': 5,
    'beaconKeyIdMode': keyIdMode,
    'beaconKeySource': [0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f],
    'beaconKeyIndex': 5
}


# Message defines:
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
    'PIBAttributeValue': 0x0000000000000020
}
msgSET_Dev1_macPANCoordShortAddress = {
    'msgId': ftdf.FTDF_SET_REQUEST,
    'PIBAttribute': ftdf.FTDF_PIB_PAN_COORD_SHORT_ADDRESS,
    'PIBAttributeValue': 0x0020
}

msgSET_SecurityDefaultKeySource = {
    'msgId': ftdf.FTDF_SET_REQUEST,
    'PIBAttribute': ftdf.FTDF_PIB_DEFAULT_KEY_SOURCE,
    'PIBAttributeValue': [0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f]
}

msgSET_ASSOC_PERMIT = {
    'msgId': ftdf.FTDF_SET_REQUEST,
    'PIBAttribute': ftdf.FTDF_PIB_ASSOCIATION_PERMIT,
    'PIBAttributeValue': True
}

msgGET_PerformanceMetrics = {
    'msgId': ftdf.FTDF_GET_REQUEST,
    'PIBAttribute': ftdf.FTDF_PIB_PERFORMANCE_METRICS,
}

msgSET_metricsEnabled = {
    'msgId': ftdf.FTDF_SET_REQUEST,
    'PIBAttribute': ftdf.FTDF_PIB_METRICS_ENABLED,
    'PIBAttributeValue': True
}

# Message order
msgFlow = (
    devId1, msgRESET, ftdf.FTDF_RESET_CONFIRM,
    devId2, msgRESET, ftdf.FTDF_RESET_CONFIRM,

    devId1, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
    devId2, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,

    devId1, msgSET_Dev1_ShortAddress, ftdf.FTDF_SET_CONFIRM,
    devId2, msgSET_Dev2_ShortAddress, ftdf.FTDF_SET_CONFIRM,

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

    devId2, msgSTART, ftdf.FTDF_START_CONFIRM,

    devId2, msgSET_ASSOC_PERMIT, ftdf.FTDF_SET_CONFIRM,

    devId2, msgRxEnable_On, ftdf.FTDF_RX_ENABLE_CONFIRM
)


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
        if( ret['msgId'] == ftdf.FTDF_SET_CONFIRM ):

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


# Message order
msgFlow = (
    devId1, msgBEACON, ftdf.FTDF_BEACON_CONFIRM,                # FRAME_TYPE_0

    devId1, msgDATA, ftdf.FTDF_DATA_CONFIRM,                    # FRAME_TYPE_1
    
    devId1, msgASSOCIATE_Request, ftdf.FTDF_ASSOCIATE_CONFIRM,    # FRAME_TYPE_3

    devId1, msgDATA_MultiPurpose, ftdf.FTDF_DATA_CONFIRM,        # FRAME_TYPE_5
)


# Test: receive frames based on frame type
if(result):
    # Enable Transparant Mode Receiving DUT
    # Available frame types 0,1,3,5 all of these frames should now be received
    options = ( ftdf.FTDF_TRANSPARENT_AUTO_ACK |
                ftdf.FTDF_TRANSPARENT_PASS_FRAME_TYPE_0 |
                ftdf.FTDF_TRANSPARENT_PASS_FRAME_TYPE_1 |
                ftdf.FTDF_TRANSPARENT_PASS_FRAME_TYPE_3 |
                ftdf.FTDF_TRANSPARENT_PASS_FRAME_TYPE_5 )
    enable = True
    DTS_enableTransparantMode( devId2, enable, options )

    idx = 0
    while( idx < len( msgFlow ) ):
        # Send message
        DTS_sndMsg( msgFlow[idx], msgFlow[idx+1] )

        if( msgFlow[idx+2] == ftdf.FTDF_ASSOCIATE_CONFIRM ):
            # Send Associate Response
            res, ret = DTS_getMsg( devId2, responseTimeout )
            if( res == False ):
                raise StopScript( 'SCRIPT: ERROR: No response received from device' )
                result = False
                break
            elif ret['msgId'] != ftdf.FTDF_TRANSPARENT_INDICATION:
                logstr = ( 'SCRIPT: ERROR: Expected ftdf.FTDF_TRANSPARENT_INDICATION confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break
            else:
                DTS_sndMsg( devId2, msgASSOCIATE_Response )
                res, ret = DTS_getMsg( devId2, responseTimeout )
                if( res == False ):
                    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
                    result = False
                    break
                elif ret['msgId'] != ftdf.FTDF_TRANSPARENT_INDICATION:
                    logstr = ( 'SCRIPT: ERROR: Expected ftdf.FTDF_TRANSPARENT_INDICATION confirm, instead received ', msgNameStr[ ret['msgId'] -1 ] )
                    raise StopScript( ''.join( map( str, logstr ) ) )
                    result = False
                    break

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

            if( (msgFlow[idx+2] != ftdf.FTDF_ASSOCIATE_CONFIRM)):
                res, ret = DTS_getMsg( devId2, responseTimeout )
                if( res == False ):
                    logstr = ( 'SCRIPT: ERROR: Message', msgNameStr[ msgFlow[idx+1]['msgId'] -1 ], 'should be received' )
                    raise StopScript( ''.join( map( str, logstr ) ) )
                    result = False
                    break
        idx += 3


# Message order
msgFlow = (
    devId1, msgDATA_Ack, ftdf.FTDF_DATA_CONFIRM,                    # FRAME_TYPE_1
    
    devId1, msgASSOCIATE_Request, ftdf.FTDF_ASSOCIATE_CONFIRM,    # FRAME_TYPE_3

    devId1, msgDATA_MultiPurpose_Ack, ftdf.FTDF_DATA_CONFIRM,        # FRAME_TYPE_5
)


# Test: No Ack is returned when in transparent mode
if(result):
    # Enable Transparant Mode Receiving DUT
    options = ( ftdf.FTDF_TRANSPARENT_PASS_FRAME_TYPE_1 |
                ftdf.FTDF_TRANSPARENT_PASS_FRAME_TYPE_3 |
                ftdf.FTDF_TRANSPARENT_PASS_FRAME_TYPE_5 )
    enable = True
    DTS_enableTransparantMode( devId2, enable, options )

    idx = 0
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

            if( ret['status'] !=  ftdf.FTDF_NO_ACK ):
                logstr = ( 'SCRIPT: ERROR: Acknowledgement frame should not be received')
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break

        idx += 3


# Message order
msgFlow = (
    devId1, msgDATA, ftdf.FTDF_DATA_CONFIRM, 1,                    # FRAME_TYPE_1

    devId1, msgDATA_MultiPurpose, ftdf.FTDF_DATA_CONFIRM, 2,    # FRAME_TYPE_5
)

# Test: no decription or verfication is done on a received frame in transparent mode
if(result):
    # Enable Transparant Mode Receiving DUT
    options = ( ftdf.FTDF_TRANSPARENT_AUTO_ACK |
                ftdf.FTDF_TRANSPARENT_PASS_FRAME_TYPE_1 |
                ftdf.FTDF_TRANSPARENT_PASS_FRAME_TYPE_5 )
    enable = True
    DTS_enableTransparantMode( devId2, enable, options )

    idx = 0
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

            if( ret['status'] != ftdf.FTDF_SUCCESS ):
                result = False
                break

            if( msgFlow[idx+2] == 1 ):
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
                    expectedFrame = [73, 152, 119, 1, 0, 32, 0, 16, 0, 29, 0, 0, 0, 0, 8, 9, 10, 11, 12, 13, 14, 15, 5, 171, 175, 32, 119, 41, 195, 47, 138, 126, 84, 35]

                    commandFrameValid = True

                    # Print received frame
                    idx2 = 0
                    while( idx2 < len( ret['frame'] ) ):
                        idx2+=1

                    # Check frame length
                    if( len( expectedFrame ) != len( ret['frame'] ) ):
                        raise StopScript( 'SCRIPT: ERROR: frame length incorrect' )
                        commandFrameValid = False
                    # Check frame bytes
                    else:
                        idx2 = 0
                        while( idx2 < len( expectedFrame ) ):
                            if( expectedFrame[idx2] != ret['frame'][idx2] ):
                                logstr = ( 'SCRIPT: ERROR: frame byte number:', idx2, 'incorrect' )
                                raise StopScript( ''.join( map( str, logstr ) ) )
                                commandFrameValid = False
                            idx2+=1

            elif( msgFlow[idx+2] == 2 ):
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
                    expectedFrame = [173, 3, 120, 1, 0, 32, 0, 16, 0, 29, 1, 0, 0, 0, 8, 9, 10, 11, 12, 13, 14, 15, 5, 71, 92, 244, 108, 6, 214, 38, 6, 126, 254, 50]

                    commandFrameValid = True

                    # Print received frame
                    idx2 = 0
                    while( idx2 < len( ret['frame'] ) ):
                        idx2+=1

                    # Check frame length
                    if( len( expectedFrame ) != len( ret['frame'] ) ):
                        raise StopScript( 'SCRIPT: ERROR: frame length incorrect' )
                        commandFrameValid = False
                    # Check frame bytes
                    else:
                        idx2 = 0
                        while( idx2 < len( expectedFrame ) ):
                            if( expectedFrame[idx2] != ret['frame'][idx2] ):
                                logstr = ( 'SCRIPT: ERROR: frame byte number:', idx2, 'incorrect' )
                                raise StopScript( ''.join( map( str, logstr ) ) )
                                commandFrameValid = False
                            idx2+=1

        idx += 4

for j in range( 2 ):
    while(1):
        res, ret = DTS_getMsg( devId1, 1 )
        if( res == False ):
            break
    while(1):
        res, ret = DTS_getMsg( devId2, 1 )
        if( res == False ):
            break

    time.sleep(5)

# Message order
msgFlow = (
    devId2, msgSET_metricsEnabled, ftdf.FTDF_SET_CONFIRM, 0,
    devId2, msgGET_PerformanceMetrics, ftdf.FTDF_GET_CONFIRM, 1,
    devId1, msgDATA, ftdf.FTDF_DATA_CONFIRM, 0,
    devId2, msgGET_PerformanceMetrics, ftdf.FTDF_GET_CONFIRM, 2 )

# Test: RXSuccessCount for transparent passed frame types
if(result):
    # Enable Transparant Mode Receiving DUT
    options = ( ftdf.FTDF_TRANSPARENT_AUTO_ACK |
                ftdf.FTDF_TRANSPARENT_PASS_FRAME_TYPE_1 )
    enable = True
    DTS_enableTransparantMode( devId2, enable, options )

    idx = 0
    rXSuccessCount = 0
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
            logstr = ( 'SCRIPT: ERROR: Expected ', msgFlow[idx+2], ' confirm, instead received ',  ret['msgId']  )
            raise StopScript( ''.join( map( str, logstr ) ) )
            result = False
            break
        else:

            if( ret['status'] != ftdf.FTDF_SUCCESS ):
                result = False
                break

            if( msgFlow[idx+2] == ftdf.FTDF_GET_CONFIRM ):
                if( msgFlow[idx+3] == 1 ):
                    rXSuccessCount = ret['PIBAttributeValue']['RXSuccessCount']
                if( msgFlow[idx+3] == 2 ):
                    if( ret['PIBAttributeValue']['RXSuccessCount'] != (rXSuccessCount+1) ):
                        raise StopScript( 'SCRIPT: ERROR: RXSuccessCount not incremented' )
                        result = False
                        break
            elif( msgFlow[idx+2] == ftdf.FTDF_DATA_CONFIRM ):
                # Remove frame from que
                res, ret = DTS_getMsg( devId2, responseTimeout )

        idx += 4


if( not result ):
    raise StopScript('SCRIPT: FAILED')
