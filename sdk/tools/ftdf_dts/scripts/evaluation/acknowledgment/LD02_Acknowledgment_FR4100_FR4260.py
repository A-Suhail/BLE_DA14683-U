# Load-drop 2 Test: Security
#

import sys    #cli arguments
import time    #sleep

from scriptIncludes import *

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
    'ackTX': True,
    'GTSTX': False,
    'indirectTX': False,
    'securityLevel': 0,
    'keyIdMode': 3,
    'keySource': [0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f],
    'keyIndex': 5,
    'frameControlOptions': 0,
    'headerIEList': 0,
    'payloadIEList': 0,
    'sendMultiPurpose': False }

msgGET_MaxFrameRetries = {
    'msgId': ftdf.FTDF_GET_REQUEST,
    'PIBAttribute': ftdf.FTDF_PIB_MAX_FRAME_RETRIES,
}

# Message order
msgFlow = ( devId1, msgRESET, ftdf.FTDF_RESET_CONFIRM,
            devId2, msgRESET, ftdf.FTDF_RESET_CONFIRM,

            devId1, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,

            devId1, msgSET_Dev1_ShortAddress, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_Dev2_ShortAddress, ftdf.FTDF_SET_CONFIRM,

            devId1, msgGET_MaxFrameRetries, ftdf.FTDF_GET_CONFIRM,
            
            devId2, msgRxEnable_On, ftdf.FTDF_RX_ENABLE_CONFIRM )


idx = 0
result = True
maxFrameRetries = 0
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
        if( ret['msgId'] == ftdf.FTDF_GET_CONFIRM ):
            maxFrameRetries = ret['PIBAttributeValue']

        elif( ret['msgId'] == ftdf.FTDF_SET_CONFIRM ):

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


if(result):
    # Enable Transparant Mode Receiving DUT
    options = ( ftdf.FTDF_TRANSPARENT_PASS_ALL_FRAME_TYPES )
    enable = True
    DTS_enableTransparantMode( devId2, enable, options )

    DTS_sndMsg( devId1, msgDATA )

    res, ret = DTS_getMsg( devId1, responseTimeout )
    if( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        result = False
    elif( ret['status'] != ftdf.FTDF_NO_ACK ):
        logstr = ( 'SCRIPT: ERROR: expected error NO_ACK error received', resultStr[ ret['status'] ] )
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False

if(result):
    res, ret = DTS_getMsg( devId2, responseTimeout )
    if( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        result = False

if(result):
    idx = 0
    while( maxFrameRetries > idx ):
        res, ret = DTS_getMsg( devId2, responseTimeout )
        if( res == False ):
            raise StopScript( 'SCRIPT: ERROR: No response received from device' )
            result = False
            break

        idx += 1

if ( not result ):
    raise StopScript('SCRIPT: FAILED')
