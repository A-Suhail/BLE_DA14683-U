import sys    #cli arguments

from scriptIncludes import *

# Data frame
msdu = [0x1, 0x2, 0x3, 0x4, 0x5]
msgDATA_shortAddress = {
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
    'keySource': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
    'keyIndex': 0,
    'frameControlOptions': 0,
    'headerIEList': 0,
    'payloadIEList': 0,
    'sendMultiPurpose': False
}
msgDATA_extendedAddress = {
    'msgId': ftdf.FTDF_DATA_REQUEST,
    'srcAddrMode': ftdf.FTDF_EXTENDED_ADDRESS,
    'dstAddrMode': ftdf.FTDF_EXTENDED_ADDRESS,
    'dstPANId': 0x0001,
    'dstAddr': 0x0000000000000020,
    'msduLength': len( msdu ),
    'msdu': msdu,
    'msduHandle': 1,
    'ackTX': False,
    'GTSTX': False,
    'indirectTX': False,
    'securityLevel': 0,
    'keyIdMode': 0,
    'keySource': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
    'keyIndex': 0,
    'frameControlOptions': 0,
    'headerIEList': 0,
    'payloadIEList': 0,
    'sendMultiPurpose': False
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

            devId2, msgRxEnable_On, ftdf.FTDF_RX_ENABLE_CONFIRM,

            devId1, msgDATA_shortAddress, ftdf.FTDF_DATA_CONFIRM,
            devId1, msgDATA_extendedAddress, ftdf.FTDF_DATA_CONFIRM )

idx = 0
while( idx < len( msgFlow ) ):
    # Send message
    DTS_sndMsg( msgFlow[idx], msgFlow[idx+1] )

    # Get message confirm
    res, ret = DTS_getMsg( msgFlow[idx], responseTimeout )

    # Check received expected confirm
    if( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    elif( ret['msgId'] != msgFlow[idx+2] ):
        logstr = ( 'SCRIPT: ERROR: Expected ', msgFlow[idx+2], ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
        raise StopScript( ''.join( map( str, logstr ) ) )
    elif( ret['status'] != ftdf.FTDF_SUCCESS ):
        errStr = 'SCRIPT: ERROR: received status: ' + resultStr[ret['status']]
        raise StopScript( errStr )
    elif( ret['msgId'] == ftdf.FTDF_DATA_CONFIRM ):
        # Check data frame received correctly
        res2, ret2 = DTS_getMsg( devId2, responseTimeout )
        if( res2 == False ):
            raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        elif ret2['msgId'] != ftdf.FTDF_DATA_INDICATION:
            logstr = ( 'SCRIPT: ERROR: Expected FTDF_DATA_INDICATION confirm, instead received ', ret2['msgId'] )
            raise StopScript( ''.join( map( str, logstr ) ) )
        else:
            dataFrameValid = True
            if( msgFlow[idx+1]['srcAddrMode'] != ret2['srcAddrMode'] ):
                dataFrameValid = False
                logstr = ( 'SCRIPT: ERROR: Data Frame: srcAddrMode: ', msgFlow[idx+1]['srcAddrMode'], ' / ', ret2['srcAddrMode'], ' (TX/RX)' )
                raise StopScript( ''.join( map( str, logstr ) ) )
            if( msgFlow[idx+1]['dstAddrMode'] != ret2['dstAddrMode'] ):
                dataFrameValid = False
                logstr = ( 'SCRIPT: ERROR: Data Frame: dstAddrMode: ', msgFlow[idx+1]['dstAddrMode'], ' / ', ret2['dstAddrMode'], ' (TX/RX)' )
                raise StopScript( ''.join( map( str, logstr ) ) )
            if( msgFlow[idx+1]['dstPANId'] != ret2['dstPANId'] ):
                dataFrameValid = False
                logstr = ( 'SCRIPT: ERROR: Data Frame: dstPANId: ', msgFlow[idx+1]['dstPANId'], ' / ', ret2['dstPANId'], ' (TX/RX)' )
                raise StopScript( ''.join( map( str, logstr ) ) )
            if( msgFlow[idx+1]['dstAddr'] != ret2['dstAddr'] ):
                dataFrameValid = False
                logstr = ( 'SCRIPT: ERROR: Data Frame: dstAddr: ', msgFlow[idx+1]['dstAddr'], ' / ', ret2['dstAddr'], ' (TX/RX)' )
                raise StopScript( ''.join( map( str, logstr ) ) )
            if( msgFlow[idx+1]['msduLength'] != ret2['msduLength'] ):
                dataFrameValid = False
                logstr = ( 'SCRIPT: ERROR: Data Frame: msduLength: ', msgFlow[idx+1]['msduLength'], ' / ', ret2['msduLength'], ' (TX/RX)' )
                raise StopScript( ''.join( map( str, logstr ) ) )
            if( msgFlow[idx+1]['msdu'] != ret2['msdu'] ):
                dataFrameValid = False
                logstr = ( 'SCRIPT: ERROR: Data Frame: msdu: ', msgFlow[idx+1]['msdu'], ' / ', ret2['msdu'], ' (TX/RX)' )
                raise StopScript( ''.join( map( str, logstr ) ) )
            if( msgFlow[idx+1]['securityLevel'] != ret2['securityLevel'] ):
                dataFrameValid = False
                logstr = ( 'SCRIPT: ERROR: Data Frame: securityLevel: ', msgFlow[idx+1]['securityLevel'], ' / ', ret2['securityLevel'], ' (TX/RX)' )
                raise StopScript( ''.join( map( str, logstr ) ) )
            if ( msgFlow[idx+1]['securityLevel'] ):
                if( msgFlow[idx+1]['keyIdMode'] != ret2['keyIdMode'] ):
                    dataFrameValid = False
                    logstr = ( 'SCRIPT: ERROR: Data Frame: keyIdMode: ', msgFlow[idx+1]['keyIdMode'], ' / ', ret2['keyIdMode'], ' (TX/RX)' )
                    raise StopScript( ''.join( map( str, logstr ) ) )
                if( msgFlow[idx+1]['keySource'] != ret2['keySource'] ):
                    dataFrameValid = False
                    logstr = ( 'SCRIPT: ERROR: Data Frame: keySource: ', msgFlow[idx+1]['keySource'], ' / ', ret2['keySource'], ' (TX/RX)' )
                    raise StopScript( ''.join( map( str, logstr ) ) )
                if( msgFlow[idx+1]['keyIndex'] != ret2['keyIndex'] ):
                    dataFrameValid = False
                    logstr = ( 'SCRIPT: ERROR: Data Frame: keyIndex: ', msgFlow[idx+1]['keyIndex'], ' / ', ret2['keyIndex'], ' (TX/RX)' )
                    raise StopScript( ''.join( map( str, logstr ) ) )

            if( not dataFrameValid ):
                raise StopScript('SCRIPT: FAILED')

    elif ret['msgId'] == ftdf.FTDF_SET_CONFIRM:
        # Check set request with get request
        msgGet['PIBAttribute'] = msgFlow[idx+1]['PIBAttribute']

        DTS_sndMsg( msgFlow[idx], msgGet )

        res2, ret2 = DTS_getMsg( msgFlow[idx], responseTimeout )
        if( res2 == False ):
            raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        elif ret2['msgId'] != ftdf.FTDF_GET_CONFIRM:
            logstr = ( 'SCRIPT: ERROR: Expected GET_CONFIRM, instead received ', ret2['msgId'] )
            raise StopScript( ''.join( map( str, logstr ) ) )
        elif ret2['PIBAttributeValue'] != msgFlow[idx+1]['PIBAttributeValue']:
            logstr = ( 'SCRIPT: ERROR: Incorrect set PIBAttribute: ', msgGet['PIBAttribute'] );
            raise StopScript( ''.join( map( str, logstr ) ) )

    idx += 3


# Test data frame is droppend when using incorrect dstPANId
msgDATA = {
    'msgId': ftdf.FTDF_DATA_REQUEST,
    'srcAddrMode': ftdf.FTDF_EXTENDED_ADDRESS,
    'dstAddrMode': ftdf.FTDF_EXTENDED_ADDRESS,
    'dstPANId': 0x0002,
    'dstAddr': 0x0000000000000020,
    'msduLength': len( msdu ),
    'msdu': msdu,
    'msduHandle': 1,
    'ackTX': False,
    'GTSTX': False,
    'indirectTX': False,
    'securityLevel': 0,
    'keyIdMode': 0,
    'keySource': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
    'keyIndex': 0,
    'frameControlOptions': 0,
    'headerIEList': 0,
    'payloadIEList': 0,
    'sendMultiPurpose': False
}

DTS_sndMsg( devId1, msgDATA )

res, ret = DTS_getMsg( devId2, responseTimeout )
if( res != False ):
    raise StopScript( 'SCRIPT: ERROR: Data frame with incorrect dstPANId should not be received' )


# Test data frame is droppend when using incorrect dstAddr
msgDATA = {
    'msgId': ftdf.FTDF_DATA_REQUEST,
    'srcAddrMode': ftdf.FTDF_EXTENDED_ADDRESS,
    'dstAddrMode': ftdf.FTDF_EXTENDED_ADDRESS,
    'dstPANId': 0x0002,
    'dstAddr': 0x0000000000000040,
    'msduLength': len( msdu ),
    'msdu': msdu,
    'msduHandle': 1,
    'ackTX': False,
    'GTSTX': False,
    'indirectTX': False,
    'securityLevel': 0,
    'keyIdMode': 0,
    'keySource': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
    'keyIndex': 0,
    'frameControlOptions': 0,
    'headerIEList': 0,
    'payloadIEList': 0,
    'sendMultiPurpose': False
}

DTS_sndMsg( devId1, msgDATA )

res, ret = DTS_getMsg( devId2, responseTimeout )
if( res != False ):
    raise StopScript( 'SCRIPT: ERROR: Data frame with incorrect dstAddr should not be received' )