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
                'frameType': ftdf.FTDF_MULTIPURPOSE_FRAME,
                'commandFrameId': 0
                },
                {
                'frameType': ftdf.FTDF_BEACON_FRAME,
                'commandFrameId': 0
                },
                {
                'frameType': ftdf.FTDF_MAC_COMMAND_FRAME,
                'commandFrameId': ftdf.FTDF_COMMAND_ASSOCIATION_REQUEST
                },
                {
                'frameType': ftdf.FTDF_MAC_COMMAND_FRAME,
                'commandFrameId': ftdf.FTDF_COMMAND_ASSOCIATION_RESPONSE
                },
                {
                'frameType': ftdf.FTDF_MAC_COMMAND_FRAME,
                'commandFrameId': ftdf.FTDF_COMMAND_DATA_REQUEST
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
                'frameType': ftdf.FTDF_MULTIPURPOSE_FRAME,
                'commandFrameId': 0
                },
                {
                'frameType': ftdf.FTDF_BEACON_FRAME,
                'commandFrameId': 0
                },
                {
                'frameType': ftdf.FTDF_MAC_COMMAND_FRAME,
                'commandFrameId': ftdf.FTDF_COMMAND_ASSOCIATION_REQUEST
                },
                {
                'frameType': ftdf.FTDF_MAC_COMMAND_FRAME,
                'commandFrameId': ftdf.FTDF_COMMAND_ASSOCIATION_RESPONSE
                },
                {
                'frameType': ftdf.FTDF_MAC_COMMAND_FRAME,
                'commandFrameId': ftdf.FTDF_COMMAND_DATA_REQUEST
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
        'commandFrameId': ftdf.FTDF_COMMAND_ASSOCIATION_REQUEST,
        'securityMinimum': 1,
        'deviceOverrideSecurityMinimum': 0,
        'allowedSecurityLevels': 0
        },
        {
        'frameType': ftdf.FTDF_MAC_COMMAND_FRAME,
        'commandFrameId': ftdf.FTDF_COMMAND_ASSOCIATION_RESPONSE,
        'securityMinimum': 1,
        'deviceOverrideSecurityMinimum': 0,
        'allowedSecurityLevels': 0
        },
        {
        'frameType': ftdf.FTDF_MAC_COMMAND_FRAME,
        'commandFrameId': ftdf.FTDF_COMMAND_DATA_REQUEST,
        'securityMinimum': 1,
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
        'commandFrameId': ftdf.FTDF_COMMAND_ASSOCIATION_REQUEST,
        'securityMinimum': 1,
        'deviceOverrideSecurityMinimum': 0,
        'allowedSecurityLevels': 0
        },
        {
        'frameType': ftdf.FTDF_MAC_COMMAND_FRAME,
        'commandFrameId': ftdf.FTDF_COMMAND_ASSOCIATION_RESPONSE,
        'securityMinimum': 1,
        'deviceOverrideSecurityMinimum': 0,
        'allowedSecurityLevels': 0
        },
        {
        'frameType': ftdf.FTDF_MAC_COMMAND_FRAME,
        'commandFrameId': ftdf.FTDF_COMMAND_DATA_REQUEST,
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

msgDATA_2 = {
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

msgSET_ASSOC_PERMIT = {
    'msgId': ftdf.FTDF_SET_REQUEST,
    'PIBAttribute': ftdf.FTDF_PIB_ASSOCIATION_PERMIT,
    'PIBAttributeValue': True
}

msgSET_autoRequest = {
    'msgId': ftdf.FTDF_SET_REQUEST,
    'PIBAttribute': ftdf.FTDF_PIB_AUTO_REQUEST,
    'PIBAttributeValue': False
}

msgSET_responseWaitTime = {
    'msgId': ftdf.FTDF_SET_REQUEST,
    'PIBAttribute': ftdf.FTDF_PIB_RESPONSE_WAIT_TIME,
    'PIBAttributeValue': 127
}

msgSET_transactionPersistenceTime = {
    'msgId': ftdf.FTDF_SET_REQUEST,
    'PIBAttribute': ftdf.FTDF_PIB_TRANSACTION_PERSISTENCE_TIME,
    'PIBAttributeValue': 0xffff
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
            
            devId1, msgSET_responseWaitTime, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_responseWaitTime, ftdf.FTDF_SET_CONFIRM,

            devId1, msgSET_transactionPersistenceTime, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_transactionPersistenceTime, ftdf.FTDF_SET_CONFIRM,

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

            devId2, msgRxEnable_On, ftdf.FTDF_RX_ENABLE_CONFIRM,

            devId1, msgDATA_1, ftdf.FTDF_DATA_CONFIRM,
            devId1, msgDATA_2, ftdf.FTDF_DATA_CONFIRM,

            devId2, msgSET_autoRequest, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSTART, ftdf.FTDF_START_CONFIRM,
            devId1, msgBEACON, ftdf.FTDF_BEACON_CONFIRM,

            devId2, msgSET_ASSOC_PERMIT, ftdf.FTDF_SET_CONFIRM,
            devId1, msgASSOCIATE_Request, ftdf.FTDF_ASSOCIATE_CONFIRM )


idx = 0
result = True
while( idx < len( msgFlow ) ):
    # Send message
    DTS_sndMsg( msgFlow[idx], msgFlow[idx+1] )

    if( msgFlow[idx+2] == ftdf.FTDF_ASSOCIATE_CONFIRM ):
        res, ret = DTS_getMsg( devId2, responseTimeout )
        if( res == False ):
            raise StopScript( 'SCRIPT: ERROR: No response received from device' )
            result = False
            break
        elif ret['msgId'] != ftdf.FTDF_ASSOCIATE_INDICATION:
            logstr = ( 'SCRIPT: ERROR: Expected FTDF_ASSOCIATE_INDICATION confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
            raise StopScript( ''.join( map( str, logstr ) ) )
            result = False
            break
        else:
            if( msgFlow[idx+1]['capabilityInformation'] != ret['capabilityInformation'] ):
                logstr = ( 'SCRIPT: ERROR: Data Frame: capabilityInformation: ', msgFlow[idx+1]['capabilityInformation'], ' / ', ret['capabilityInformation'], ' (TX/RX)' )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break
            if( msgFlow[idx+1]['securityLevel'] != ret['securityLevel'] ):
                logstr = ( 'SCRIPT: ERROR: Data Frame: securityLevel: ', msgFlow[idx+1]['securityLevel'], ' / ', ret['securityLevel'], ' (TX/RX)' )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break
            if( msgFlow[idx+1]['keyIdMode'] != ret['keyIdMode'] ):
                logstr = ( 'SCRIPT: ERROR: Data Frame: keyIdMode: ', msgFlow[idx+1]['keyIdMode'], ' / ', ret['keyIdMode'], ' (TX/RX)' )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break
            if( msgFlow[idx+1]['keySource'] != ret['keySource'] ):
                logstr = ( 'SCRIPT: ERROR: Data Frame: keySource: ', msgFlow[idx+1]['keySource'], ' / ', ret['keySource'], ' (TX/RX)' )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break
            if( msgFlow[idx+1]['keyIndex'] != ret['keyIndex'] ):
                logstr = ( 'SCRIPT: ERROR: Data Frame: keyIndex: ', msgFlow[idx+1]['keyIndex'], ' / ', ret['keyIndex'], ' (TX/RX)' )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break
            if( msgFlow[idx+1]['channelOffset'] != ret['channelOffset'] ):
                logstr = ( 'SCRIPT: ERROR: Data Frame: channelOffset: ', msgFlow[idx+1]['channelOffset'], ' / ', ret['channelOffset'], ' (TX/RX)' )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break
            if( msgFlow[idx+1]['hoppingSequenceId'] != ret['hoppingSequenceId'] ):
                logstr = ( 'SCRIPT: ERROR: Data Frame: hoppingSequenceId: ', msgFlow[idx+1]['hoppingSequenceId'], ' / ', ret['hoppingSequenceId'], ' (TX/RX)' )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break

            # Send Associate Response
            DTS_sndMsg( devId2, msgASSOCIATE_Response )

            res, ret = DTS_getMsg( devId2, responseTimeout )
            if( res == False ):
                raise StopScript( 'SCRIPT: ERROR: No response received from device' )
                result = False
                break
            elif ret['msgId'] != ftdf.FTDF_COMM_STATUS_INDICATION:
                logstr = ( 'SCRIPT: ERROR: Expected FTDF_COMM_STATUS_INDICATION confirm, instead received ', msgNameStr[ ret['msgId'] -1 ] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break

    if( msgFlow[idx+2] == ftdf.FTDF_BEACON_CONFIRM ):
            res, ret = DTS_getMsg( devId2, responseTimeout )
            if( res == False ):
                raise StopScript( 'SCRIPT: ERROR: No response received from device' )
                result = False
                break
            elif ret['msgId'] != ftdf.FTDF_BEACON_NOTIFY_INDICATION:
                logstr = ( 'SCRIPT: ERROR: Expected BEACON_NOTIFY_INDICATION confirm, instead received ', msgNameStr[ ret['msgId'] -1 ] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break
            else:
                if( msgFlow[idx+1]['beaconType'] != ret['beaconType'] ):
                    logstr = ( 'SCRIPT: ERROR: Data Frame: beaconType: ', msgFlow[idx+1]['beaconType'], ' / ', ret['beaconType'], ' (TX/RX)' )
                    raise StopScript( ''.join( map( str, logstr ) ) )
                    result = False


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
        if( ret['msgId'] == ftdf.FTDF_DATA_CONFIRM ):

            if( ret['status'] != ftdf.FTDF_SUCCESS ):
                result = False
                break

            # Check data frame received correctly
            res2, ret2 = DTS_getMsg( devId2, responseTimeout )
            if( res2 == False ):
                raise StopScript( 'SCRIPT: ERROR: No response received from device' )
                result = False
                break
            elif ret2['msgId'] != ftdf.FTDF_DATA_INDICATION:
                logstr = ( 'SCRIPT: ERROR: Expected FTDF_DATA_INDICATION confirm, instead received ', ret2['msgId'] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break
            else:
                if( msgFlow[idx+1]['srcAddrMode'] != ret2['srcAddrMode'] ):
                    logstr = ( 'SCRIPT: ERROR: Data Frame: srcAddrMode: ', msgFlow[idx+1]['srcAddrMode'], ' / ', ret2['srcAddrMode'], ' (TX/RX)' )
                    raise StopScript( ''.join( map( str, logstr ) ) )
                    result = False

                if( msgFlow[idx+1]['dstAddrMode'] != ret2['dstAddrMode'] ):
                    logstr = ( 'SCRIPT: ERROR: Data Frame: dstAddrMode: ', msgFlow[idx+1]['dstAddrMode'], ' / ', ret2['dstAddrMode'], ' (TX/RX)' )
                    raise StopScript( ''.join( map( str, logstr ) ) )
                    result = False
                if( msgFlow[idx+1]['dstPANId'] != ret2['dstPANId'] ):
                    logstr = ( 'SCRIPT: ERROR: Data Frame: dstPANId: ', msgFlow[idx+1]['dstPANId'], ' / ', ret2['dstPANId'], ' (TX/RX)' )
                    raise StopScript( ''.join( map( str, logstr ) ) )
                    result = False
                if( msgFlow[idx+1]['dstAddr'] != ret2['dstAddr'] ):
                    logstr = ( 'SCRIPT: ERROR: Data Frame: dstAddr: ', msgFlow[idx+1]['dstAddr'], ' / ', ret2['dstAddr'], ' (TX/RX)' )
                    raise StopScript( ''.join( map( str, logstr ) ) )
                    result = False

                if( msgFlow[idx+1]['msduLength'] != ret2['msduLength'] ):
                    logstr = ( 'SCRIPT: ERROR: Data Frame: msduLength: ', msgFlow[idx+1]['msduLength'], ' / ', ret2['msduLength'], ' (TX/RX)' )
                    raise StopScript( ''.join( map( str, logstr ) ) )
                    result = False
                if( msgFlow[idx+1]['msdu'] != ret2['msdu'] ):
                    logstr = ( 'SCRIPT: ERROR: Data Frame: msdu: ', msgFlow[idx+1]['msdu'], ' / ', ret2['msdu'], ' (TX/RX)' )
                    raise StopScript( ''.join( map( str, logstr ) ) )
                    result = False

                if( msgFlow[idx+1]['securityLevel'] != ret2['securityLevel'] ):
                    logstr = ( 'SCRIPT: ERROR: Data Frame: securityLevel: ', msgFlow[idx+1]['securityLevel'], ' / ', ret2['securityLevel'], ' (TX/RX)' )
                    raise StopScript( ''.join( map( str, logstr ) ) )
                    result = False
                if ( msgFlow[idx+1]['securityLevel'] ):
                    if( msgFlow[idx+1]['keyIdMode'] != ret2['keyIdMode'] ):
                        logstr = ( 'SCRIPT: ERROR: Data Frame: keyIdMode: ', msgFlow[idx+1]['keyIdMode'], ' / ', ret2['keyIdMode'], ' (TX/RX)' )
                        raise StopScript( ''.join( map( str, logstr ) ) )
                        result = False
                    if( msgFlow[idx+1]['keySource'] != ret2['keySource'] and
                        msgFlow[idx+1]['keyIdMode'] >= 2 ):
                        logstr = ( 'SCRIPT: ERROR: Data Frame: keySource: ', msgFlow[idx+1]['keySource'], ' / ', ret2['keySource'], ' (TX/RX)' )
                        raise StopScript( ''.join( map( str, logstr ) ) )
                        result = False
                    if( msgFlow[idx+1]['keyIndex'] != ret2['keyIndex'] and
                        msgFlow[idx+1]['keyIdMode'] >= 1 ):
                        logstr = ( 'SCRIPT: ERROR: Data Frame: keyIndex: ', msgFlow[idx+1]['keyIndex'], ' / ', ret2['keyIndex'], ' (TX/RX)' )
                        raise StopScript( ''.join( map( str, logstr ) ) )
                        result = False

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

    idx += 3


if( not result ):
    raise StopScript('SCRIPT: FAILED')
