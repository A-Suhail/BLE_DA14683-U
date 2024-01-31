import sys     #cli arguments

from scriptIncludes import *


msdu = [0xFF]
msgDATA_DUT1 = {
    'msgId': ftdf.FTDF_DATA_REQUEST,
    'srcAddrMode': ftdf.FTDF_SHORT_ADDRESS,
    'dstAddrMode': ftdf.FTDF_SHORT_ADDRESS,
    'dstPANId': 0x0001,
    'dstAddr': 0x0020,
    'msduLength': len( msdu ),
    'msdu': msdu,
    'msduHandle': 0,
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
msgDATA_DUT2 = {
    'msgId': ftdf.FTDF_DATA_REQUEST,
    'srcAddrMode': ftdf.FTDF_SHORT_ADDRESS,
    'dstAddrMode': ftdf.FTDF_SHORT_ADDRESS,
    'dstPANId': 0x0001,
    'dstAddr': 0x0010,
    'msduLength': len( msdu ),
    'msdu': msdu,
    'msduHandle': 0,
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

set_csl_period_msg =         { 'msgId': ftdf.FTDF_SET_REQUEST,
                               'PIBAttribute': ftdf.FTDF_PIB_CSL_PERIOD,
                               'PIBAttributeValue': 80 }

set_csl_period_max_msg =     { 'msgId': ftdf.FTDF_SET_REQUEST,
                               'PIBAttribute': ftdf.FTDF_PIB_CSL_MAX_PERIOD,
                               'PIBAttributeValue': 65535 }

set_csl_sync_tx_margin_msg = { 'msgId': ftdf.FTDF_SET_REQUEST,
                               'PIBAttribute': ftdf.FTDF_PIB_CSL_SYNC_TX_MARGIN,
                               'PIBAttributeValue': 80 }

set_csl_max_age_msg =        { 'msgId': ftdf.FTDF_SET_REQUEST,
                               'PIBAttribute': ftdf.FTDF_PIB_CSL_MAX_AGE_REMOTE_INFO,
                               'PIBAttributeValue': 40000 }

set_le_ena_msg =             { 'msgId': ftdf.FTDF_SET_REQUEST,
                               'PIBAttribute': ftdf.FTDF_PIB_LE_ENABLED,
                               'PIBAttributeValue': True }

set_le_dis_msg =             { 'msgId': ftdf.FTDF_SET_REQUEST,
                               'PIBAttribute': ftdf.FTDF_PIB_LE_ENABLED,
                               'PIBAttributeValue': False }

# Message order
msgFlow = (
    devId1, msgRESET, ftdf.FTDF_RESET_CONFIRM,
    devId2, msgRESET, ftdf.FTDF_RESET_CONFIRM,

    devId1, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
    devId2, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,

    devId1, msgSET_Dev1_ShortAddress, ftdf.FTDF_SET_CONFIRM,
    devId2, msgSET_Dev2_ShortAddress, ftdf.FTDF_SET_CONFIRM,

    # Check DUT 2 FTDF is functioning correctly
    devId1, msgRxEnable_On, ftdf.FTDF_RX_ENABLE_CONFIRM,
    devId2, msgDATA_DUT2, ftdf.FTDF_DATA_CONFIRM,

    devId2, msgRxEnable_On, ftdf.FTDF_RX_ENABLE_CONFIRM,

    # Configure CSL for transmitting DUT
    devId1, set_csl_period_msg, ftdf.FTDF_SET_CONFIRM,
    devId1, set_csl_period_max_msg, ftdf.FTDF_SET_CONFIRM,
    devId1, set_csl_sync_tx_margin_msg, ftdf.FTDF_SET_CONFIRM,
    devId1, set_csl_max_age_msg, ftdf.FTDF_SET_CONFIRM,
    devId1, set_le_ena_msg, ftdf.FTDF_SET_CONFIRM,
    devId1, msgDATA_DUT1, ftdf.FTDF_DATA_CONFIRM,

    # Check DUT 2 FTDF is still functioning correctly
    devId1, set_le_dis_msg, ftdf.FTDF_SET_CONFIRM,
    devId1, msgRxEnable_On, ftdf.FTDF_RX_ENABLE_CONFIRM,
    devId2, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,            # Check PIB provisioning
    devId2, msgDATA_DUT2, ftdf.FTDF_DATA_CONFIRM,           # Check frame transmitting
    devId2, msgRxEnable_On, ftdf.FTDF_RX_ENABLE_CONFIRM,    # Check frame receiving
    devId1, msgDATA_DUT1, ftdf.FTDF_DATA_CONFIRM,
)


idx = 0
while( idx < len( msgFlow ) ):
    DTS_sndMsg( msgFlow[idx], msgFlow[idx+1] )

    res, ret = DTS_getMsg( msgFlow[idx],100 )
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

        res, ret = DTS_getMsg( msgFlow[idx], 100 )
        if( res == False ):
            raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        elif ret['msgId'] != ftdf.FTDF_GET_CONFIRM:
            logstr = ( 'SCRIPT: ERROR: Expected GET_CONFIRM, instead received ', ret['msgId'] )
            raise StopScript( ''.join( map( str, logstr ) ) )
        elif ret['PIBAttributeValue'] != msgFlow[idx+1]['PIBAttributeValue']:
            logstr = ( 'SCRIPT: ERROR: Incorrect set PIBAttribute: ', msgGet['PIBAttribute'] );
            raise StopScript( ''.join( map( str, logstr ) ) )

    elif( ret['msgId'] == ftdf.FTDF_DATA_CONFIRM ):
        dutId = devId1
        if( msgFlow[idx] == devId1 ):
            dutId = devId2

        res, ret = DTS_getMsg( dutId, 100 )
        if( res == False ):
            raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        elif ret['msgId'] != ftdf.FTDF_DATA_INDICATION:
            logstr = ( 'SCRIPT: ERROR: Expected DATA_INDICATION, instead received ', ret['msgId'] )
            raise StopScript( ''.join( map( str, logstr ) ) )

    idx += 3