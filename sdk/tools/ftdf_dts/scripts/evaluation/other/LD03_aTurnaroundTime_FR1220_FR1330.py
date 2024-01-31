# Load-drop 3 Test: 
#

import sys    #cli arguments
import time    #sleep

from scriptIncludes import *


msdu = [0x01,0x02,0x03,0x04,0x05]
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
    'securityLevel': 0,
    'keyIdMode': 0,
    'keySource': [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
    'keyIndex': 0,
    'frameControlOptions': 0,
    'headerIEList': 0,
    'payloadIEList': 0,
    'sendMultiPurpose': False
}
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
    'securityLevel': 0,
    'keyIdMode': 0,
    'keySource': [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
    'keyIndex': 0,
    'frameControlOptions': 0,
    'headerIEList': 0,
    'payloadIEList': 0,
    'sendMultiPurpose': False
}

# Message order
msgFlow = (
    devId1, msgRESET, ftdf.FTDF_RESET_CONFIRM,
    devId2, msgRESET, ftdf.FTDF_RESET_CONFIRM,

    devId1, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
    devId2, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,

    devId1, msgSET_Dev1_ShortAddress, ftdf.FTDF_SET_CONFIRM,
    devId2, msgSET_Dev2_ShortAddress, ftdf.FTDF_SET_CONFIRM,

    devId1, msgRxEnable_On, ftdf.FTDF_RX_ENABLE_CONFIRM,
    devId2, msgRxEnable_On, ftdf.FTDF_RX_ENABLE_CONFIRM,

    devId1, msgDATA, ftdf.FTDF_DATA_CONFIRM,

    devId1, msgDATA_Ack, ftdf.FTDF_DATA_CONFIRM
)


idx = 0
result = True
while( idx < len( msgFlow ) ):
    # Send message
    DTS_sndMsg( msgFlow[idx], msgFlow[idx+1] )

    if( msgFlow[idx+2] == ftdf.FTDF_SCAN_CONFIRM ):
        idx += 3
        continue

    # Get message confirm
    res, ret = DTS_getMsg( msgFlow[idx], responseTimeout )

    # Check received expected confirm
    if( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        result = False
        break
    elif( ret['msgId'] != msgFlow[idx+2] ):
        logstr = ( 'SCRIPT: ERROR: Expected ', msgFlow[idx+2], ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False
        break
    else:
        if( ret['msgId'] == ftdf.FTDF_RESET_CONFIRM ):
            # Transmitting device - Delay PHY RX and TX transisions by number of symbols
            # adr = 0x40090188 msk = 0xff000000
            registerSize = 4
            DTS_getRegister( devId1, 0x40090188, registerSize )
            res, ret = DTS_getMsg( devId1, responseTimeout )

            registerValue = ret['val']

            # Create register value
            nrOfSymbols = 12
            waitTime = 16 * nrOfSymbols
            waitTime = waitTime << 24

            registerValue = registerValue | waitTime

            DTS_setRegister( devId1, 0x40090188, registerSize, registerValue )
            res, ret = DTS_getMsg( devId1, responseTimeout )

            DTS_getRegister( devId1, 0x40090188, registerSize )
            res, ret = DTS_getMsg( devId1, responseTimeout )

            # Receiving device - Delay PHY RX and TX transisions by number of symbols
            # adr = 0x40090188 msk = 0xff000000
            registerSize = 4
            DTS_getRegister( devId2, 0x40090188, registerSize )
            res, ret = DTS_getMsg( devId2, responseTimeout )

            registerValue = ret['val']

            # Create register value
            nrOfSymbols = 12
            waitTime = 16 * nrOfSymbols
            waitTime = waitTime << 24

            registerValue = registerValue | waitTime

            DTS_setRegister( devId2, 0x40090188, registerSize, registerValue )
            res, ret = DTS_getMsg( devId2, responseTimeout )

            DTS_getRegister( devId2, 0x40090188, registerSize )
            res, ret = DTS_getMsg( devId2, responseTimeout )


        elif( ret['msgId'] == ftdf.FTDF_SET_CONFIRM ):
            if( ret['status'] != ftdf.FTDF_SUCCESS ):
                logstr = ( 'SCRIPT: ERROR: devId:', msgFlow[idx], ' request:', msgNameStr[ msgFlow[idx+1]['msgId'] -1 ], 'attribute:', pibAttributeStr[ msgFlow[idx+1]['PIBAttribute'] -1 ], ' result:', resultStr[ ret['status'] ] )
                raise StopScript( ''.join( map( str, logstr ) ) )
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
            elif( ret2['status'] != ftdf.FTDF_SUCCESS ):
                logstr = ( 'SCRIPT: devId:', msgFlow[idx], ' request: GET_REQUEST', 'attribute:', pibAttributeStr[ msgFlow[idx+1]['PIBAttribute'] -1 ], ' result:', resultStr[ ret2['status'] ] )
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
                logstr = ( 'SCRIPT: devId:', msgFlow[idx], ' request:', msgNameStr[ msgFlow[idx+1]['msgId'] -1 ], ' result:', resultStr[ ret['status'] ] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break

    idx += 3


if( not result ):
    raise StopScript('SCRIPT: FAILED')
