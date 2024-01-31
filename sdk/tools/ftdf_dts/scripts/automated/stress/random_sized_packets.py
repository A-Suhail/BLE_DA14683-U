import sys     #cli arguments

from scriptIncludes import *

from datetime import datetime
from random import randint


msdu = [0xFF]
msgDATA = {
    'msgId': ftdf.FTDF_DATA_REQUEST,
    'srcAddrMode': ftdf.FTDF_SHORT_ADDRESS,
    'dstAddrMode': ftdf.FTDF_SHORT_ADDRESS,
    'dstPANId': 0x0001,
    'dstAddr': 0x0020,
    'msduLength': len( msdu ),
    'msdu': msdu,
    'msduHandle': 0,
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

msgRxEnable = {
    'msgId': ftdf.FTDF_SET_REQUEST,
    'PIBAttribute': ftdf.FTDF_PIB_RX_ON_WHEN_IDLE,
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

    devId2, msgRxEnable, ftdf.FTDF_SET_CONFIRM,
)


idx = 0
while( idx < len( msgFlow ) ):
    DTS_sndMsg( msgFlow[idx], msgFlow[idx+1] )

    res, ret = DTS_getMsg( msgFlow[idx], responseTimeout )
    if( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    elif( ret['msgId'] != msgFlow[idx+2] ):
        logstr = ( 'SCRIPT: ERROR: Expected ', msgFlow[idx+2], ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
        raise StopScript( ''.join( map( str, logstr ) ) )
    elif( ret['status'] != ftdf.FTDF_SUCCESS ):
        logstr = 'SCRIPT: ERROR: received status: ' + resultStr[ret['status']]
        raise StopScript( logstr )

    elif( ret['msgId'] == ftdf.FTDF_SET_CONFIRM ):
        # Check set request with get request
        msgGet['PIBAttribute'] = msgFlow[idx+1]['PIBAttribute']

        DTS_sndMsg( msgFlow[idx], msgGet )

        res, ret = DTS_getMsg( msgFlow[idx], responseTimeout )
        if( res == False ):
            raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        elif ret['msgId'] != ftdf.FTDF_GET_CONFIRM:
            logstr = ( 'SCRIPT: ERROR: Expected GET_CONFIRM, instead received ', ret['msgId'] )
            raise StopScript( ''.join( map( str, logstr ) ) )
        elif ret['PIBAttributeValue'] != msgFlow[idx+1]['PIBAttributeValue']:
            logstr = ( 'SCRIPT: ERROR: Incorrect set PIBAttribute: ', msgGet['PIBAttribute'] );
            raise StopScript( ''.join( map( str, logstr ) ) )

    idx += 3


# Get time
curTime = datetime.now()
startHour = curTime.hour
startMinute = curTime.minute

# Loop to send random data packets for one hour
while( 1 ):
    # Get time
    curTime = datetime.now()
    currentHour = curTime.hour
    currentMinute = curTime.minute

    if( startHour == 23 ):
        if( currentMinute >= startMinute and
            currentHour < startHour ):
            break
    else:
        if( currentMinute >= startMinute and
            currentHour > startHour ):
            break

    DTS_sndMsg( devId1, msgDATA )

    res, ret = DTS_getMsg( devId1, responseTimeout )
    if( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    elif( ret['msgId'] != ftdf.FTDF_DATA_CONFIRM ):
        logstr = ( 'SCRIPT: ERROR: Expected DATA_CONFIRM, instead received ', msgNameStr[ ret['msgId'] -1 ])
        raise StopScript( ''.join( map( str, logstr ) ) )
    elif( ret['status'] != ftdf.FTDF_SUCCESS ):
        logstr = 'SCRIPT: ERROR: received status: ' + resultStr[ret['status']]
        raise StopScript( logstr )
    else:
        # Check data frame received correctly
        res, ret = DTS_getMsg( devId2, responseTimeout )
        if( res == False ):
            raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        elif ret['msgId'] != ftdf.FTDF_DATA_INDICATION:
            logstr = ( 'SCRIPT: ERROR: Expected FTDF_DATA_INDICATION confirm, instead received ', ret['msgId'] )
            raise StopScript( ''.join( map( str, logstr ) ) )
        else:
            if( msgDATA['srcAddrMode'] != ret['srcAddrMode'] ):
                logstr = ( 'SCRIPT: ERROR: Data Frame: srcAddrMode: ', msgDATA['srcAddrMode'], ' / ', ret['srcAddrMode'], ' (TX/RX)' )
                raise StopScript( ''.join( map( str, logstr ) ) )
            if( msgDATA['dstAddrMode'] != ret['dstAddrMode'] ):
                logstr = ( 'SCRIPT: ERROR: Data Frame: dstAddrMode: ', msgDATA['dstAddrMode'], ' / ', ret['dstAddrMode'], ' (TX/RX)' )
                raise StopScript( ''.join( map( str, logstr ) ) )
            if( msgDATA['dstPANId'] != ret['dstPANId'] ):
                logstr = ( 'SCRIPT: ERROR: Data Frame: dstPANId: ', msgDATA['dstPANId'], ' / ', ret['dstPANId'], ' (TX/RX)' )
                raise StopScript( ''.join( map( str, logstr ) ) )
            if( msgDATA['dstAddr'] != ret['dstAddr'] ):
                logstr = ( 'SCRIPT: ERROR: Data Frame: dstAddr: ', msgDATA['dstAddr'], ' / ', ret['dstAddr'], ' (TX/RX)' )
                raise StopScript( ''.join( map( str, logstr ) ) )
            if( msgDATA['msduLength'] != ret['msduLength'] ):
                logstr = ( 'SCRIPT: ERROR: Data Frame: msduLength: ', msgDATA['msduLength'], ' / ', ret['msduLength'], ' (TX/RX)' )
                raise StopScript( ''.join( map( str, logstr ) ) )
            if( msgDATA['msdu'] != ret['msdu'] ):
                logstr = ( 'SCRIPT: ERROR: Data Frame: msdu: ', msgDATA['msdu'], ' / ', ret['msdu'], ' (TX/RX)' )
                raise StopScript( ''.join( map( str, logstr ) ) )
            if( msgDATA['securityLevel'] != ret['securityLevel'] ):
                logstr = ( 'SCRIPT: ERROR: Data Frame: securityLevel: ', msgDATA['securityLevel'], ' / ', ret['securityLevel'], ' (TX/RX)' )
                raise StopScript( ''.join( map( str, logstr ) ) )
            if ( msgDATA['securityLevel'] ):
                if( msgDATA['keyIdMode'] != ret['keyIdMode'] ):
                    logstr = ( 'SCRIPT: ERROR: Data Frame: keyIdMode: ', msgDATA['keyIdMode'], ' / ', ret['keyIdMode'], ' (TX/RX)' )
                    raise StopScript( ''.join( map( str, logstr ) ) )
                if( msgDATA['keySource'] != ret['keySource'] ):
                    logstr = ( 'SCRIPT: ERROR: Data Frame: keySource: ', msgDATA['keySource'], ' / ', ret['keySource'], ' (TX/RX)' )
                    raise StopScript( ''.join( map( str, logstr ) ) )
                if( msgDATA['keyIndex'] != ret['keyIndex'] ):
                    logstr = ( 'SCRIPT: ERROR: Data Frame: keyIndex: ', msgDATA['keyIndex'], ' / ', ret['keyIndex'], ' (TX/RX)' )
                    raise StopScript( ''.join( map( str, logstr ) ) )

    # Change data frame msdu size
    msdu = []
    msduLength = randint(1,116) # Max PSDU size is 127 byte. The MSDU incaptulation in this example is 11 byte then the max MSDU size is 116
    for i in range( msduLength ):
        msdu.append( i )

    msgDATA['msdu'] = msdu
    msgDATA['msduLength'] = msduLength