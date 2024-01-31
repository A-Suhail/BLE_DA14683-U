import sys  #cli arguments

from scriptIncludes import *


msgBR  = {
    'msgId': ftdf.FTDF_BEACON_REQUEST,
    'beaconType': ftdf.FTDF_NORMAL_BEACON,
    'channel': 11,
    'channelPage': 0,
    'superframeOrder': 0,
    'beaconSecurityLevel': 0,
    'beaconKeyIdMode': 0,
    'beaconKeySource': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
    'beaconKeyIndex': 0,
    'dstAddrMode': ftdf.FTDF_SHORT_ADDRESS,
    'dstAddr': 0xFFFF,
    'BSNSuppression': 0
}

set_autore_msg =  {
    'msgId': ftdf.FTDF_SET_REQUEST,
    'PIBAttribute': ftdf.FTDF_PIB_AUTO_REQUEST,
    'PIBAttributeValue': True
}

unset_autore_msg = {
    'msgId': ftdf.FTDF_SET_REQUEST, 
    'PIBAttribute': ftdf.FTDF_PIB_AUTO_REQUEST,
    'PIBAttributeValue': False
}

counter_msg = {
    'msgId': ftdf.FTDF_GET_REQUEST,
    'PIBAttribute': ftdf.FTDF_PIB_TRAFFIC_COUNTERS
}

# Message order
msgFlow = (
    devId1, msgRESET, ftdf.FTDF_RESET_CONFIRM, 0,
    devId2, msgRESET, ftdf.FTDF_RESET_CONFIRM, 0,

    devId1, msgSET_PANId, ftdf.FTDF_SET_CONFIRM, 0,
    devId2, msgSET_PANId, ftdf.FTDF_SET_CONFIRM, 0,

    devId1, msgSET_Dev1_ShortAddress, ftdf.FTDF_SET_CONFIRM, 0,
    devId2, msgSET_Dev2_ShortAddress, ftdf.FTDF_SET_CONFIRM, 0,

    # Test beacons received, macAutoRequest = False
    devId1, unset_autore_msg, ftdf.FTDF_SET_CONFIRM, 0,
    devId2, unset_autore_msg, ftdf.FTDF_SET_CONFIRM, 0,
    devId1, msgRxEnable_On, ftdf.FTDF_RX_ENABLE_CONFIRM, 0,
    devId2, msgRxEnable_On, ftdf.FTDF_RX_ENABLE_CONFIRM, 0,
    devId1, msgBR, ftdf.FTDF_BEACON_CONFIRM, 0,
    devId2, msgBR, ftdf.FTDF_BEACON_CONFIRM, 0,

    # Test beacons received, macAutoRequest = True
    devId1, set_autore_msg, ftdf.FTDF_SET_CONFIRM, 0,
    devId2, set_autore_msg, ftdf.FTDF_SET_CONFIRM, 0,
    devId1, msgRxEnable_On, ftdf.FTDF_RX_ENABLE_CONFIRM, 0,
    devId2, msgRxEnable_On, ftdf.FTDF_RX_ENABLE_CONFIRM, 0,
    devId1, msgBR, ftdf.FTDF_BEACON_CONFIRM, 1,
    devId2, msgBR, ftdf.FTDF_BEACON_CONFIRM, 1,

    devId1, counter_msg, ftdf.FTDF_GET_CONFIRM, 0,
)


idx = 0
while( idx < len( msgFlow ) ):
    # Send message
    DTS_sndMsg( msgFlow[idx], msgFlow[idx+1] )

    # Get message confirm
    res, ret = DTS_getMsg( msgFlow[idx],responseTimeout )

    # Check received expected confirm
    if( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    elif( ret['msgId'] != msgFlow[idx+2] ):
        logstr = ( 'SCRIPT: ERROR: Expected ', msgFlow[idx+2], ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
        raise StopScript( ''.join( map( str, logstr ) ) )
    elif( ret['status'] != ftdf.FTDF_SUCCESS ):
        errStr = 'SCRIPT: ERROR: received status: ' + resultStr[ret['status']]
        raise StopScript( errStr )

    elif( ret['msgId'] == ftdf.FTDF_BEACON_CONFIRM ):
        # Check beacon received
        rxDevice = devId1
        if( msgFlow[idx] == devId1 ):
            rxDevice = devId2

        if( msgFlow[idx+3] == 1 ):
            # Beacon should not be received
            res, ret = DTS_getMsg( rxDevice, responseTimeout )
            if( res != False ):
                raise StopScript( 'SCRIPT: ERROR: Beacon should not be received' )
        else:
            # Beacon should be received
            res, ret = DTS_getMsg( rxDevice, responseTimeout )
            if( res == False ):
                raise StopScript( 'SCRIPT: ERROR: No response received from device' )
            elif ret['msgId'] != ftdf.FTDF_BEACON_NOTIFY_INDICATION:
                logstr = ( 'SCRIPT: ERROR: Expected FTDF_BEACON_NOTIFY_INDICATION, instead received ', msgNameStr[ ret['msgId'] -1 ])
                raise StopScript( ''.join( map( str, logstr ) ) )

    elif( ret['msgId'] == ftdf.FTDF_GET_CONFIRM ):
        if( ret['PIBAttributeValue']['rxBeaconFrmOkCnt'] != 2 ):
            logstr = ( 'SCRIPT: ERROR: Expected rxBeaconFrmOkCnt = ', 2,', instead received ', ret['PIBAttributeValue']['rxBeaconFrmOkCnt'] )
            raise StopScript( ''.join( map( str, logstr ) ) )
        elif( ret['PIBAttributeValue']['txBeaconFrmCnt'] != 2 ):
            logstr = ( 'SCRIPT: ERROR: Expected txBeaconFrmCnt = ', 2,', instead received ', ret['PIBAttributeValue']['txBeaconFrmCnt'] )
            raise StopScript( ''.join( map( str, logstr ) ) )
        elif( ret['PIBAttributeValue']['txCmdFrmCnt'] != 0 ):
            logstr = ( 'SCRIPT: ERROR: Expected txCmdFrmCnt = 0, instead received ', ret['PIBAttributeValue']['txCmdFrmCnt'] )
            raise StopScript( ''.join( map( str, logstr ) ) )

    elif( ret['msgId'] == ftdf.FTDF_SET_CONFIRM ):
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

    idx += 4