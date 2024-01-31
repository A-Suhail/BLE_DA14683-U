import sys    #cli arguments
import time    #sleep

from scriptIncludes import *

DTS_getReleaseInfo(devId1)
DTS_getReleaseInfo(devId2)

res, ret = DTS_getMsg( devId1, responseTimeout )
res, ret = DTS_getMsg( devId2, responseTimeout )

# Data frame
msdu = [0x1, 0x2, 0x3, 0x4, 0x5]
keySource = [0x0, 0x0, 0x0, 0x0,
             0x0, 0x0, 0x0, 0x0]
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
            'keySource': keySource,
            'keyIndex': 0,
            'frameControlOptions': 2,
            'headerIEList': 0,
            'payloadIEList': {'nrOfIEs': 1, 'IEs': [{'ID': 1, 'length': 4, 'content': {'nrOfSubIEs': 1, 'subIEs': [{'type': 1, 'subID': 1, 'length': 3, 'subContent': [0,1,2]}]}}]},
            'sendMultiPurpose': False }

# Message order
msgFlow = ( devId1, msgRESET, ftdf.FTDF_RESET_CONFIRM,
            devId2, msgRESET, ftdf.FTDF_RESET_CONFIRM,
            
            devId1, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
            
            devId1, msgSET_Dev1_ShortAddress, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_Dev2_ShortAddress, ftdf.FTDF_SET_CONFIRM,
            
            devId2, msgRxEnable_On, ftdf.FTDF_RX_ENABLE_CONFIRM,
            
            devId1, msgDATA, ftdf.FTDF_DATA_CONFIRM )

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
            res2, ret2 = DTS_getMsg( devId2, responseTimeout )

            if( res2 == False ):
                raise StopScript( 'SCRIPT: ERROR: No response received from device' )
                break
            elif ret2['msgId'] != ftdf.FTDF_DATA_INDICATION:
                logstr = ( 'SCRIPT: ERROR: Expected FTDF_DATA_INDICATION confirm, instead received ', ret2['msgId'] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                break
            else:
                dataFrameValid = True
                if( msgDATA['srcAddrMode'] != ret2['srcAddrMode'] ):
                    dataFrameValid = False
                    logstr = ( 'SCRIPT: ERROR: Data Frame: srcAddrMode: ', msgDATA['srcAddrMode'], ' / ', ret2['srcAddrMode'], ' (TX/RX)' )
                    raise StopScript( ''.join( map( str, logstr ) ) )
                if( msgDATA['dstAddrMode'] != ret2['dstAddrMode'] ):
                    dataFrameValid = False
                    logstr = ( 'SCRIPT: ERROR: Data Frame: dstAddrMode: ', msgDATA['dstAddrMode'], ' / ', ret2['dstAddrMode'], ' (TX/RX)' )
                    raise StopScript( ''.join( map( str, logstr ) ) )
                if( msgDATA['dstPANId'] != ret2['dstPANId'] ):
                    dataFrameValid = False
                    logstr = ( 'SCRIPT: ERROR: Data Frame: dstPANId: ', msgDATA['dstPANId'], ' / ', ret2['dstPANId'], ' (TX/RX)' )
                    raise StopScript( ''.join( map( str, logstr ) ) )
                if( msgDATA['dstAddr'] != ret2['dstAddr'] ):
                    dataFrameValid = False
                    logstr = ( 'SCRIPT: ERROR: Data Frame: dstAddr: ', msgDATA['dstAddr'], ' / ', ret2['dstAddr'], ' (TX/RX)' )
                    raise StopScript( ''.join( map( str, logstr ) ) )
                if( msgDATA['msduLength'] != ret2['msduLength'] ):
                    dataFrameValid = False
                    logstr = ( 'SCRIPT: ERROR: Data Frame: msduLength: ', msgDATA['msduLength'], ' / ', ret2['msduLength'], ' (TX/RX)' )
                    raise StopScript( ''.join( map( str, logstr ) ) )
                if( msgDATA['msdu'] != ret2['msdu'] ):
                    dataFrameValid = False
                    logstr = ( 'SCRIPT: ERROR: Data Frame: msdu: ', msgDATA['msdu'], ' / ', ret2['msdu'], ' (TX/RX)' )
                    raise StopScript( ''.join( map( str, logstr ) ) )
                if( msgDATA['securityLevel'] != ret2['securityLevel'] ):
                    dataFrameValid = False
                    logstr = ( 'SCRIPT: ERROR: Data Frame: securityLevel: ', msgDATA['securityLevel'], ' / ', ret2['securityLevel'], ' (TX/RX)' )
                    raise StopScript( ''.join( map( str, logstr ) ) )
                if ( msgDATA['securityLevel'] ):
                    if( msgDATA['keyIdMode'] != ret2['keyIdMode'] ):
                        dataFrameValid = False
                        logstr = ( 'SCRIPT: ERROR: Data Frame: keyIdMode: ', msgDATA['keyIdMode'], ' / ', ret2['keyIdMode'], ' (TX/RX)' )
                        raise StopScript( ''.join( map( str, logstr ) ) )
                    if( msgDATA['keySource'] != ret2['keySource'] ):
                        dataFrameValid = False
                        logstr = ( 'SCRIPT: ERROR: Data Frame: keySource: ', msgDATA['keySource'], ' / ', ret2['keySource'], ' (TX/RX)' )
                        raise StopScript( ''.join( map( str, logstr ) ) )
                    if( msgDATA['keyIndex'] != ret2['keyIndex'] ):
                        dataFrameValid = False
                        logstr = ( 'SCRIPT: ERROR: Data Frame: keyIndex: ', msgDATA['keyIndex'], ' / ', ret2['keyIndex'], ' (TX/RX)' )
                        raise StopScript( ''.join( map( str, logstr ) ) )

                if( not dataFrameValid ):
                    raise StopScript('SCRIPT: FAILED')

        elif ret['msgId'] == ftdf.FTDF_SET_CONFIRM:
            if( ret['status'] != ftdf.FTDF_SUCCESS ):
                break
            # Check set request with get request
            msgGet['PIBAttribute'] = msgFlow[idx+1]['PIBAttribute']

            DTS_sndMsg( msgFlow[idx], msgGet )

            res2, ret2 = DTS_getMsg( msgFlow[idx], responseTimeout )

            if( res2 == False ):
                raise StopScript( 'SCRIPT: ERROR: No response received from device' )
                break
            elif ret2['msgId'] != ftdf.FTDF_GET_CONFIRM:
                logstr = ( 'SCRIPT: ERROR: Expected GET_CONFIRM, instead received ', ret2['msgId'] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                break
            elif ret2['PIBAttributeValue'] != msgFlow[idx+1]['PIBAttributeValue']:
                logstr = ( 'SCRIPT: ERROR: Incorrect set PIBAttribute: ', msgGet['PIBAttribute'] );
                raise StopScript( ''.join( map( str, logstr ) ) )
                break
        else:
            if( ret['status'] != ftdf.FTDF_SUCCESS ):
                break

    idx += 3
