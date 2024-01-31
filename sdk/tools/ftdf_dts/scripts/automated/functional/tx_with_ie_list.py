import sys    #cli arguments

from scriptIncludes import *


# Data frame
msdu = [0x1, 0x2, 0x3, 0x4, 0x5]

ieSubCon1 = [0xAB,0xAB,0xAB,0xAB,0xAB]
ieSubCon2 = [0xCD,0xCD,0xCD,0xCD,0xCD,0xCD]
ieSubCon3 = [0xEF,0xEF,0xEF,0xEF]
ieSubCon4 = [0x89,0x89,0x89,0x89,0x89,0x89,0x89]

iEList = {
    'nrOfIEs': 3,
    'IEs': [
        {
            'ID': 2,
            'length': len(ieSubCon3),
            'content': ieSubCon3
        },
        {
            'ID': 1,
            'length': 0,
            'content': {
                'nrOfSubIEs': 4,
                'subIEs': [
                    {
                        'type': 0,
                        'subID': 11,
                        'length': len(ieSubCon1),
                        'subContent': ieSubCon1
                    },
                    {
                        'type': 0,
                        'subID': 12,
                        'length': len(ieSubCon2),
                        'subContent': ieSubCon2
                    },
                    {
                        'type': 0,
                        'subID': 13,
                        'length': len(ieSubCon3),
                        'subContent': ieSubCon3
                    },
                    {
                        'type': 0,
                        'subID': 14,
                        'length': len(ieSubCon4),
                        'subContent': ieSubCon4
                    }
                ]
            }
        },
        {
            'ID': 2,
            'length': len(ieSubCon1),
            'content': ieSubCon1
        }
    ]
}

msgDATA = { 'msgId': ftdf.FTDF_DATA_REQUEST,
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
            'keySource': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
            'keyIndex': 0,
            'frameControlOptions': 2,
            'headerIEList': 0,
            'payloadIEList': iEList,
            'sendMultiPurpose': False }

# Message order
msgFlow = (
    devId1, msgRESET, ftdf.FTDF_RESET_CONFIRM,
    devId2, msgRESET, ftdf.FTDF_RESET_CONFIRM,

    devId1, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
    devId2, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,

    devId1, msgSET_Dev1_ShortAddress, ftdf.FTDF_SET_CONFIRM,
    devId2, msgSET_Dev2_ShortAddress, ftdf.FTDF_SET_CONFIRM,

    devId2, msgRxEnable_On, ftdf.FTDF_RX_ENABLE_CONFIRM,

    devId1, msgDATA, ftdf.FTDF_DATA_CONFIRM
)

idx = 0
res = True

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
        if( ret['msgId'] == ftdf.FTDF_DATA_CONFIRM ):
            if( ret['status'] != ftdf.FTDF_SUCCESS ):
                break

            # Check data frame received correctly
            res, ret = DTS_getMsg( devId2, responseTimeout )

            if( res == False ):
                raise StopScript( 'SCRIPT: ERROR: No response received from device' )
                break
            elif ret['msgId'] != ftdf.FTDF_DATA_INDICATION:
                logstr = ( 'SCRIPT: ERROR: Expected FTDF_DATA_INDICATION confirm, instead received ', ret['msgId'] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                break
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

                # IE
                if( ret['payloadIEList']['nrOfIEs'] != 3 ):
                    logstr = ( 'SCRIPT: ERROR: expected nrOfIEs = 3 received:', ret['payloadIEList']['nrOfIEs'] )
                    raise StopScript( ''.join( map( str, logstr ) ) )
                if( ret['payloadIEList']['IEs'][1]['content']['nrOfSubIEs'] != 4 ):
                    logstr = ( 'SCRIPT: ERROR: expected nrOfSubIEs = 4 received:', ret['payloadIEList']['IEs'][1]['content']['nrOfSubIEs'] )
                    raise StopScript( ''.join( map( str, logstr ) ) )

                # IE 1
                if( ret['payloadIEList']['IEs'][0]['content'] != ieSubCon3 ):
                    logstr = ( 'SCRIPT: ERROR: expected IE 1 content =', ieSubCon3, ' received:', ret['payloadIEList']['IEs'][0]['content'] )
                    raise StopScript( ''.join( map( str, logstr ) ) )

                # IE 2 with sub IE's
                if( ret['payloadIEList']['IEs'][1]['content']['subIEs'][0]['subID'] != 11 ):
                    logstr = ( 'SCRIPT: ERROR: expected SubIE 1 subID=', 11, 'received:', ret['payloadIEList']['IEs'][1]['content']['subIEs'][0]['subID'] )
                    raise StopScriptieSubCon1
                if( ret['payloadIEList']['IEs'][1]['content']['subIEs'][0]['content'] != ieSubCon1 ):
                    logstr = ( 'SCRIPT: ERROR: expected SubIE 1 content=', ieSubCon1, 'received:', ret['payloadIEList']['IEs'][1]['content']['subIEs'][0]['content'] )
                    raise StopScript( ''.join( map( str, logstr ) ) )
                if( ret['payloadIEList']['IEs'][1]['content']['subIEs'][0]['type'] != 0 ):
                    logstr = ( 'SCRIPT: ERROR: expected type 0 received:', ret['payloadIEList']['IEs'][1]['content']['subIEs'][0]['type'] )
                    raise StopScript( ''.join( map( str, logstr ) ) )

                if( ret['payloadIEList']['IEs'][1]['content']['subIEs'][1]['subID'] != 12 ):
                    logstr = ( 'SCRIPT: ERROR: expected SubIE 1 subID=', 12, 'received:', ret['payloadIEList']['IEs'][1]['content']['subIEs'][1]['subID'] )
                    raise StopScriptieSubCon1
                if( ret['payloadIEList']['IEs'][1]['content']['subIEs'][1]['content'] != ieSubCon2):
                    logstr = ( 'SCRIPT: ERROR: expected SubIE 1 content=', ieSubCon2, 'received:', ret['payloadIEList']['IEs'][1]['content']['subIEs'][1]['content'] )
                    raise StopScript( ''.join( map( str, logstr ) ) )
                if( ret['payloadIEList']['IEs'][1]['content']['subIEs'][1]['type'] != 0 ):
                    logstr = ( 'SCRIPT: ERROR: expected type 0 received:', ret['payloadIEList']['IEs'][1]['content']['subIEs'][1]['type'] )
                    raise StopScript( ''.join( map( str, logstr ) ) )

                if( ret['payloadIEList']['IEs'][1]['content']['subIEs'][2]['subID'] != 13 ):
                    logstr = ( 'SCRIPT: ERROR: expected SubIE 1 subID=', 13, 'received:', ret['payloadIEList']['IEs'][1]['content']['subIEs'][2]['subID'] )
                    raise StopScriptieSubCon1
                if( ret['payloadIEList']['IEs'][1]['content']['subIEs'][2]['content'] != ieSubCon3 ):
                    logstr = ( 'SCRIPT: ERROR: expected SubIE 1 content=', ieSubCon3, 'received:', ret['payloadIEList']['IEs'][1]['content']['subIEs'][2]['content'] )
                    raise StopScript( ''.join( map( str, logstr ) ) )
                if( ret['payloadIEList']['IEs'][1]['content']['subIEs'][2]['type'] != 0 ):
                    logstr = ( 'SCRIPT: ERROR: expected type 0 received:', ret['payloadIEList']['IEs'][1]['content']['subIEs'][2]['type'] )
                    raise StopScript( ''.join( map( str, logstr ) ) )

                if( ret['payloadIEList']['IEs'][1]['content']['subIEs'][3]['subID'] != 14 ):
                    logstr = ( 'SCRIPT: ERROR: expected SubIE 1 subID=', 14, 'received:', ret['payloadIEList']['IEs'][1]['content']['subIEs'][3]['subID'] )
                    raise StopScriptieSubCon1
                if( ret['payloadIEList']['IEs'][1]['content']['subIEs'][3]['content'] != ieSubCon4 ):
                    logstr = ( 'SCRIPT: ERROR: expected SubIE 1 content=', ieSubCon4, 'received:', ret['payloadIEList']['IEs'][1]['content']['subIEs'][3]['content'] )
                    raise StopScript( ''.join( map( str, logstr ) ) )
                if( ret['payloadIEList']['IEs'][1]['content']['subIEs'][3]['type'] != 0 ):
                    logstr = ( 'SCRIPT: ERROR: expected type 0 received:', ret['payloadIEList']['IEs'][1]['content']['subIEs'][3]['type'] )
                    raise StopScript( ''.join( map( str, logstr ) ) )

                # IE 3
                if( ret['payloadIEList']['IEs'][2]['content'] != ieSubCon1 ):
                    logstr = ( 'SCRIPT: ERROR: expected IE 3 content =', ieSubCon1, ' received:', ret['payloadIEList']['IEs'][2]['content'] )
                    raise StopScript( ''.join( map( str, logstr ) ) )

        elif ret['msgId'] == ftdf.FTDF_SET_CONFIRM:
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
        else:
            if( ret['status'] != ftdf.FTDF_SUCCESS ):
                break

    idx += 3
