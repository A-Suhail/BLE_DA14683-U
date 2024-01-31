# Test BLE-only functions. This is a preparation for true arbiter tests. 

import sys    #cli arguments
import time    #sleep

from scriptIncludes import *
i = 0
meas = []
DTS_BLEReset(devId1)
# Expect OK
res, ret = DTS_getMsg( devId1, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_BLE_OK, 
               ' confirm, instead received ', ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

DTS_BLEReset(devId2)
# Expect OK
res, ret = DTS_getMsg( devId2, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_BLE_OK, 
               ' confirm, instead received ', ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

nrOfFrames = 1000
sduLength = 52

# Data frame
msdu = []
for i in range( sduLength ):
    msdu.append( i )

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
            'ackTX': False,
            'GTSTX': False,
            'indirectTX': False,
            'securityLevel': 0,
            'keyIdMode': 0,
            'keySource': keySource,
            'keyIndex': 0,
            'frameControlOptions': 0,
            'headerIEList': 0,
            'payloadIEList': 0,
            'sendMultiPurpose': False }



msgSET_macMaxFrameRetries = { 'msgId': ftdf.FTDF_SET_REQUEST,
                             'PIBAttribute': ftdf.FTDF_PIB_MAX_FRAME_RETRIES,
                             'PIBAttributeValue': 7 }

msgDbgModeSetRequest = {
    'msgId': ftdf.FTDF_DBG_MODE_SET_REQUEST,
    'dbgMode': 0x1,
}

# Prepare test messages
msgFlow = ( devId1, msgRESET, ftdf.FTDF_RESET_CONFIRM,
            devId2, msgRESET, ftdf.FTDF_RESET_CONFIRM,
            
            devId1, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
            
            devId1, msgSET_Dev1_ShortAddress, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_Dev2_ShortAddress, ftdf.FTDF_SET_CONFIRM,
            
            devId1, msgSET_macMaxFrameRetries, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_macMaxFrameRetries, ftdf.FTDF_SET_CONFIRM,
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
        logstr = ( 'SCRIPT: ERROR: Expected ', msgFlow[idx+2], ' confirm, instead received ', 
                   msgNameStr[ ret['msgId'] -1 ])
        raise StopScript( ''.join( map( str, logstr ) ) )
        break
    else:
        if ret['msgId'] == ftdf.FTDF_SET_CONFIRM:
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


# DTS_sndMsg(devId1,msgDbgModeSetRequest);
# DTS_sndMsg(devId2,msgDbgModeSetRequest);

# Reset arbiter
DTS_ArbiterReset(devId1)
DTS_ArbiterReset(devId2)

# =================================================================================================#


bleParams = []
bleParams.append({'interval_min': 20, 'interval_max': 24, 'slave_latency': 0, 'sup_timeout': 15})
bleParams.append({'interval_min': 40, 'interval_max': 48, 'slave_latency': 0, 'sup_timeout': 30})
bleParams.append({'interval_min': 67, 'interval_max': 80, 'slave_latency': 0, 'sup_timeout': 50})
bleParams.append({'interval_min': 133, 'interval_max': 160, 'slave_latency': 0, 'sup_timeout': 100})

meas = []

J = len(bleParams)

ftdfRateFtdfOverBle = []
ftdfRateNoAckNoCoexCca = []
ftdfRateWithAckNoCoexCca = []
ftdfRateNoAckCoexCca = []
ftdfRateWithAckCoexCca = []

partA = False
partB = True

# ##################################################################################################
# # Measurements Part A: BLE over FTDF
# ##################################################################################################
    
if (partA):
    # Set arbiter configuration FTDF priority BLE
    DTS_ArbiterSetConfig(devId1, 0, 0, 0, 
                         ftdf.DTS_COEX_MAC_TYPE_BLE, 0,
                         ftdf.DTS_COEX_MAC_TYPE_FTDF, 0,
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0 )
       
       
    msgDATA['ackTX'] = False
       
    for j in range(J):
        # Start the connection 
        status, reason = DTS_BLEConnectionOpen( devId1, devId2, 100, bleParams[j]['interval_min'], 
                                         bleParams[j]['interval_max'], bleParams[j]['slave_latency'], 
                                         bleParams[j]['sup_timeout'])
           
        # Enable BLE message log on both devices
        DTS_BLEMsgLogEnable(devId1)
        DTS_BLEMsgLogEnable(devId2)
       
        # Start FTDF traffic
        status, reason, txPkt, rxPkt, duration = DTS_FTDFPERTest(devId1, devId2, msgDATA, nrOfFrames, 0, 
                                                       responseTimeout, msgRxEnable_On, msgRxEnable_Off)
               
        ftdfRateNoAckNoCoexCca.append({'txPkt': txPkt, 'rxPkt': rxPkt, 'duration': duration, 
                                       'pps': rxPkt * 1000000 / duration})
           
        # Disable log.
        DTS_BLEMsgLogDisable(devId1)
           
        # Expect log with zero entries
        res, ret = DTS_getMsg( devId1, responseTimeout )
        if( res == False ):
            raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_MSG_LOG:
            logstr = ( 'SCRIPT: ERROR: Expected msgId', ftdf.DTS_MSG_ID_BLE_MSG_LOG, 
                       ' confirm, instead received ', ret['msgId'])
            raise StopScript( ''.join( map( str, logstr ) ) )
        elif ret['msgIdx'] != 0:
            logstr = ( 'SCRIPT: ERROR: Expected log with 0 entries, instead received', ret['msgIdx'])
            raise StopScript( ''.join( map( str, logstr ) ) )
           
        # Disable log.
        DTS_BLEMsgLogDisable(devId2)
           
        # Expect log with zero entries
        res, ret = DTS_getMsg( devId2, responseTimeout )
        if( res == False ):
            raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_MSG_LOG:
            logstr = ( 'SCRIPT: ERROR: Expected msgId', ftdf.DTS_MSG_ID_BLE_MSG_LOG, 
                       ' confirm, instead received ', ret['msgId'])
            raise StopScript( ''.join( map( str, logstr ) ) )
        elif ret['msgIdx'] != 0:
            logstr = ( 'SCRIPT: ERROR: Expected log with 0 entries, instead received', ret['msgIdx'])
            raise StopScript( ''.join( map( str, logstr ) ) )
           
        status, reason = DTS_BLEConnectionClose(devId1, devId2, responseTimeout)
             
        if ( status == ftdf.DTS_BLE_FUNC_STATUS_NO_RSP ):
            raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        elif ( status == ftdf.DTS_BLE_FUNC_STATUS_MSG_ID):
            logstr = ( 'SCRIPT: ERROR: Expected msgId ', reason['expected'], ' instead received ', 
                       reason['received'] )
            raise StopScript( ''.join( map( str, logstr ) ) )
        elif ( status == ftdf.DTS_BLE_FUNC_STATUS_BLE_EVT):
            logstr = ( 'SCRIPT: ERROR: Expected evt_code ', reason['expected'], ' instead received ', 
                       reason['received'] )
            raise StopScript( ''.join( map( str, logstr ) ) )
           
       
    msgDATA['ackTX'] = True
       
    for j in range(J):
        # Start the connection 
        status, reason = DTS_BLEConnectionOpen( devId1, devId2, 100, bleParams[j]['interval_min'], 
                                         bleParams[j]['interval_max'], bleParams[j]['slave_latency'], 
                                         bleParams[j]['sup_timeout'])
           
        # Enable BLE message log on both devices
        DTS_BLEMsgLogEnable(devId1)
        DTS_BLEMsgLogEnable(devId2)
       
        # Start FTDF traffic
        status, reason, txPkt, rxPkt, duration = DTS_FTDFPERTest(devId1, devId2, msgDATA, nrOfFrames, 0, 
                                                       responseTimeout, msgRxEnable_On, msgRxEnable_Off)
               
        ftdfRateWithAckNoCoexCca.append({'txPkt': txPkt, 'rxPkt': rxPkt, 'duration': duration, 
                                         'pps': rxPkt * 1000000 / duration})
           
        # Disable log.
        DTS_BLEMsgLogDisable(devId1)
           
        # Expect log with zero entries
        res, ret = DTS_getMsg( devId1, responseTimeout )
        if( res == False ):
            raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_MSG_LOG:
            logstr = ( 'SCRIPT: ERROR: Expected msgId', ftdf.DTS_MSG_ID_BLE_MSG_LOG, 
                       ' confirm, instead received ', ret['msgId'])
            raise StopScript( ''.join( map( str, logstr ) ) )
        elif ret['msgIdx'] != 0:
            logstr = ( 'SCRIPT: ERROR: Expected log with 0 entries, instead received', ret['msgIdx'])
            raise StopScript( ''.join( map( str, logstr ) ) )
           
        # Disable log.
        DTS_BLEMsgLogDisable(devId2)
           
        # Expect log with zero entries
        res, ret = DTS_getMsg( devId2, responseTimeout )
        if( res == False ):
            raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_MSG_LOG:
            logstr = ( 'SCRIPT: ERROR: Expected msgId', ftdf.DTS_MSG_ID_BLE_MSG_LOG, 
                       ' confirm, instead received ', ret['msgId'])
            raise StopScript( ''.join( map( str, logstr ) ) )
        elif ret['msgIdx'] != 0:
            logstr = ( 'SCRIPT: ERROR: Expected log with 0 entries, instead received', ret['msgIdx'])
            raise StopScript( ''.join( map( str, logstr ) ) )
           
        status, reason = DTS_BLEConnectionClose(devId1, devId2, responseTimeout)
             
        if ( status == ftdf.DTS_BLE_FUNC_STATUS_NO_RSP ):
            raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        elif ( status == ftdf.DTS_BLE_FUNC_STATUS_MSG_ID):
            logstr = ( 'SCRIPT: ERROR: Expected msgId ', reason['expected'], ' instead received ', 
                       reason['received'] )
            raise StopScript( ''.join( map( str, logstr ) ) )
        elif ( status == ftdf.DTS_BLE_FUNC_STATUS_BLE_EVT):
            logstr = ( 'SCRIPT: ERROR: Expected evt_code ', reason['expected'], ' instead received ', 
                       reason['received'] )
            raise StopScript( ''.join( map( str, logstr ) ) )
       
    # Set arbiter configuration FTDF priority BLE
    DTS_ArbiterSetConfig(devId1, 0, 0, 0, 
                         ftdf.DTS_COEX_MAC_TYPE_BLE, 0,
                         ftdf.DTS_COEX_MAC_TYPE_FTDF, 0,
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0 )
       
       
    msgDATA['ackTX'] = False
       
    for j in range(J):
        # Start the connection 
        status, reason = DTS_BLEConnectionOpen( devId1, devId2, 100, bleParams[j]['interval_min'], 
                                         bleParams[j]['interval_max'], bleParams[j]['slave_latency'], 
                                         bleParams[j]['sup_timeout'])
           
        # Enable BLE message log on both devices
        DTS_BLEMsgLogEnable(devId1)
        DTS_BLEMsgLogEnable(devId2)
       
        # Start FTDF traffic
        status, reason, txPkt, rxPkt, duration = DTS_FTDFPERTest(devId1, devId2, msgDATA, nrOfFrames, 0, 
                                                       responseTimeout, msgRxEnable_On, msgRxEnable_Off)
               
        ftdfRateNoAckCoexCca.append({'txPkt': txPkt, 'rxPkt': rxPkt, 'duration': duration, 
                                     'pps': rxPkt * 1000000 / duration})
           
        # Disable log.
        DTS_BLEMsgLogDisable(devId1)
           
        # Expect log with zero entries
        res, ret = DTS_getMsg( devId1, responseTimeout )
        if( res == False ):
            raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_MSG_LOG:
            logstr = ( 'SCRIPT: ERROR: Expected msgId', ftdf.DTS_MSG_ID_BLE_MSG_LOG, 
                       ' confirm, instead received ', ret['msgId'])
            raise StopScript( ''.join( map( str, logstr ) ) )
        elif ret['msgIdx'] != 0:
            logstr = ( 'SCRIPT: ERROR: Expected log with 0 entries, instead received', ret['msgIdx'])
            raise StopScript( ''.join( map( str, logstr ) ) )
           
        # Disable log.
        DTS_BLEMsgLogDisable(devId2)
           
        # Expect log with zero entries
        res, ret = DTS_getMsg( devId2, responseTimeout )
        if( res == False ):
            raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_MSG_LOG:
            logstr = ( 'SCRIPT: ERROR: Expected msgId', ftdf.DTS_MSG_ID_BLE_MSG_LOG, 
                       ' confirm, instead received ', ret['msgId'])
            raise StopScript( ''.join( map( str, logstr ) ) )
        elif ret['msgIdx'] != 0:
            logstr = ( 'SCRIPT: ERROR: Expected log with 0 entries, instead received', ret['msgIdx'])
            raise StopScript( ''.join( map( str, logstr ) ) )
           
        status, reason = DTS_BLEConnectionClose(devId1, devId2, responseTimeout)
             
        if ( status == ftdf.DTS_BLE_FUNC_STATUS_NO_RSP ):
            raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        elif ( status == ftdf.DTS_BLE_FUNC_STATUS_MSG_ID):
            logstr = ( 'SCRIPT: ERROR: Expected msgId ', reason['expected'], ' instead received ', 
                       reason['received'] )
            raise StopScript( ''.join( map( str, logstr ) ) )
        elif ( status == ftdf.DTS_BLE_FUNC_STATUS_BLE_EVT):
            logstr = ( 'SCRIPT: ERROR: Expected evt_code ', reason['expected'], ' instead received ', 
                       reason['received'] )
            raise StopScript( ''.join( map( str, logstr ) ) )
           
       
    msgDATA['ackTX'] = True
       
    for j in range(J):
        # Start the connection 
        status, reason = DTS_BLEConnectionOpen( devId1, devId2, 100, bleParams[j]['interval_min'], 
                                         bleParams[j]['interval_max'], bleParams[j]['slave_latency'], 
                                         bleParams[j]['sup_timeout'])
           
        # Enable BLE message log on both devices
        DTS_BLEMsgLogEnable(devId1)
        DTS_BLEMsgLogEnable(devId2)
       
        # Start FTDF traffic
        status, reason, txPkt, rxPkt, duration = DTS_FTDFPERTest(devId1, devId2, msgDATA, nrOfFrames, 0, 
                                                       responseTimeout, msgRxEnable_On, msgRxEnable_Off)
               
        ftdfRateWithAckCoexCca.append({'txPkt': txPkt, 'rxPkt': rxPkt, 'duration': duration, 
                                       'pps': rxPkt * 1000000 / duration})
           
        # Disable log.
        DTS_BLEMsgLogDisable(devId1)
           
        # Expect log with zero entries
        res, ret = DTS_getMsg( devId1, responseTimeout )
        if( res == False ):
            raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_MSG_LOG:
            logstr = ( 'SCRIPT: ERROR: Expected msgId', ftdf.DTS_MSG_ID_BLE_MSG_LOG, 
                       ' confirm, instead received ', ret['msgId'])
            raise StopScript( ''.join( map( str, logstr ) ) )
        elif ret['msgIdx'] != 0:
            logstr = ( 'SCRIPT: ERROR: Expected log with 0 entries, instead received', ret['msgIdx'])
            raise StopScript( ''.join( map( str, logstr ) ) )
           
        # Disable log.
        DTS_BLEMsgLogDisable(devId2)
           
        # Expect log with zero entries
        res, ret = DTS_getMsg( devId2, responseTimeout )
        if( res == False ):
            raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_MSG_LOG:
            logstr = ( 'SCRIPT: ERROR: Expected msgId', ftdf.DTS_MSG_ID_BLE_MSG_LOG, 
                       ' confirm, instead received ', ret['msgId'])
            raise StopScript( ''.join( map( str, logstr ) ) )
        elif ret['msgIdx'] != 0:
            logstr = ( 'SCRIPT: ERROR: Expected log with 0 entries, instead received', ret['msgIdx'])
            raise StopScript( ''.join( map( str, logstr ) ) )
           
        status, reason = DTS_BLEConnectionClose(devId1, devId2, responseTimeout)
             
        if ( status == ftdf.DTS_BLE_FUNC_STATUS_NO_RSP ):
            raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        elif ( status == ftdf.DTS_BLE_FUNC_STATUS_MSG_ID):
            logstr = ( 'SCRIPT: ERROR: Expected msgId ', reason['expected'], ' instead received ', 
                       reason['received'] )
            raise StopScript( ''.join( map( str, logstr ) ) )
        elif ( status == ftdf.DTS_BLE_FUNC_STATUS_BLE_EVT):
            logstr = ( 'SCRIPT: ERROR: Expected evt_code ', reason['expected'], ' instead received ', 
                       reason['received'] )
            raise StopScript( ''.join( map( str, logstr ) ) )

####################################################################################################
# Measurements Part B: FTDF over BLE
####################################################################################################
if (partB):
    # Set arbiter configuration FTDF priority BLE
    DTS_ArbiterSetConfig(devId1, 0, 0, 0, 
                         ftdf.DTS_COEX_MAC_TYPE_FTDF, 0,
                         ftdf.DTS_COEX_MAC_TYPE_BLE, 0,
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                         ftdf.DTS_COEX_MAC_TYPE_NONE, 0 )
    
    
    msgDATA['ackTX'] = False
    
    
    for j in range(J):
        i_min = 5000
        i_max = 15000
        i_best = i_max
#         i_step = (i_max - i_min) / 2
        i_step = (i_max - i_min) / 5
        i = i_min + i_step
        i_found = False
        repetitions = 10
        max_errors = 2
#         while (i_step > 1):
        while (i <= i_max):
            for k in range(repetitions):
                errors_rem = max_errors
                while (1): 
                    res = True
                    while (res):
                        res, ret = DTS_getMsg( devId1, 1 )
                    res = True
                    while (res):
                        res, ret = DTS_getMsg( devId2, 1 )
                        
                    DTS_BLEReset(devId1)
                    # Expect OK
                    res, ret = DTS_getMsg( devId1, responseTimeout )
                    if( res == False ):
                        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
                    elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
                        logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_BLE_OK, 
                                   ' confirm, instead received ', ret['msgId'] )
                        raise StopScript( ''.join( map( str, logstr ) ) )
                
                    DTS_BLEReset(devId2)
                    # Expect OK
                    res, ret = DTS_getMsg( devId2, responseTimeout )
                    if( res == False ):
                        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
                    elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
                        logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_BLE_OK, 
                                   ' confirm, instead received ', ret['msgId'] )
                        raise StopScript( ''.join( map( str, logstr ) ) )

                
                    # Start the connection 
                    status, reason = DTS_BLEConnectionOpen( devId1, devId2, 200, bleParams[j]['interval_min'], 
                                                 bleParams[j]['interval_max'], 
                                                 bleParams[j]['slave_latency'], 
                                                 bleParams[j]['sup_timeout'])
                
                    if (status != ftdf.DTS_BLE_FUNC_STATUS_OK):
                        if (errors_rem > 0):
                            dtsLog.warning('BLE connection failed without FTDF interference. Repeating...')
                            errors_rem -= 1
                            continue
                        else:
                            logstr = ( 'SCRIPT: ERROR: BLE connection failed without FTDF interference.')
                            raise StopScript( ''.join( map( str, logstr ) ) )
                
                    # Enable BLE message log on both devices
                    DTS_BLEMsgLogEnable(devId1)
                    # Check for any pending events 
                    res, ret = DTS_getMsg( devId1, 2 )
                    if (res == True):
                        if ret['msgId'] == ftdf.DTS_MSG_ID_BLE_EVT:
                            if ret['evt_code'] == ftdf.DTS_BLE_EVT_CODE_GAP_DISCONNECTED:
                                if (errors_rem > 0):
                                    dtsLog.warning('BLE connection dropped without FTDF interference. Repeating...')
                                    errors_rem -= 1
                                    continue
                                else:
                                    logstr = ( 'SCRIPT: ERROR: BLE connection dropped without FTDF interference.')
                                    raise StopScript( ''.join( map( str, logstr ) ) )
                
                    DTS_BLEMsgLogEnable(devId2)
                    # Check for any pending events 
                    res, ret = DTS_getMsg( devId1, 2 )
                    if (res == True):
                        if ret['msgId'] == ftdf.DTS_MSG_ID_BLE_EVT:
                            if ret['evt_code'] == ftdf.DTS_BLE_EVT_CODE_GAP_DISCONNECTED:
                                if (errors_rem > 0):
                                    dtsLog.warning('BLE connection dropped without FTDF interference. Repeating...')
                                    errors_rem -= 1
                                    continue
                                else:
                                    logstr = ( 'SCRIPT: ERROR: BLE connection dropped without FTDF interference')
                                    raise StopScript( ''.join( map( str, logstr ) ) )
    
                    # Start FTDF traffic
                    status, reason, txPkt, rxPkt, duration = DTS_FTDFPERTest(devId1, devId2, msgDATA, 
                                                                         nrOfFrames, int(i), responseTimeout, 
                                                                         msgRxEnable_On, msgRxEnable_Off)
                    
                    if (status != ftdf.DTS_BLE_FUNC_STATUS_OK):
                        logstr = ( 'SCRIPT: ERROR: FTDF PER test failed with status ', status)
                        raise StopScript( ''.join( map( str, logstr ) ) )
                    
                    
                    DTS_BleStatsReq(devId1)
    
                    res, ret = DTS_getMsg( devId1, responseTimeout )
                    if( res == False ):
                        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
                    elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_STATS:
                        logstr = ( 'SCRIPT: ERROR: Expected msgId', ftdf.DTS_MSG_ID_BLE_STATS, 
                                   ' confirm, instead received ', ret['msgId'])
                        raise StopScript( ''.join( map( str, logstr ) ) )
                    
                    time.sleep(1 * bleParams[j]['sup_timeout'] * 10 / 1000)
                    
                    blePER = ret['bleDataPacketErrors'] / ret['bleTotalDataPackets']
                    
                    # Check if BLE connection has dropped
                    bleConnIsLost = False
                    # Disable log.
                    DTS_BLEMsgLogDisable(devId1)
                
                    # Check log etries
                    res, ret = DTS_getMsg( devId1, responseTimeout )
                    if( res == False ):
                        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
                    elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_MSG_LOG:
                        logstr = ( 'SCRIPT: ERROR: Expected msgId', ftdf.DTS_MSG_ID_BLE_MSG_LOG, 
                                   ' confirm, instead received ', ret['msgId'])
                        raise StopScript( ''.join( map( str, logstr ) ) )
                    elif ret['msgIdx'] == 0:
                        # No messages. BLE connection is OK
                        bleConnIsLost = False
                    else:
                        bleConnIsLost = True
                        # Strict checking
                        if ret['msgIdx'] != 1:
                            logstr = ( 'SCRIPT: ERROR: Expected log with 1 entry, instead received', 
                                       ret['msgIdx'])
                            raise StopScript( ''.join( map( str, logstr ) ) )
                        elif ret['evtCode0'] != ftdf.DTS_BLE_EVT_CODE_GAP_DISCONNECTED:
                            logstr = ( 'SCRIPT: ERROR: Expected log with 1 entry and evtCode ', 
                                       ftdf.DTS_BLE_EVT_CODE_GAP_DISCONNECTED, ' instead received ', 
                                       ret['evtCode0'])
                            raise StopScript( ''.join( map( str, logstr ) ) )
                
                    # Disable log.
                    DTS_BLEMsgLogDisable(devId2)
                
                    # Strict checking on central
                    if (bleConnIsLost):
                        # Expect log with one entry
                        res, ret = DTS_getMsg( devId2, responseTimeout )
                        if( res == False ):
                            raise StopScript( 'SCRIPT: ERROR: No response received from device' )
                        elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_MSG_LOG:
                            logstr = ( 'SCRIPT: ERROR: Expected msgId', ftdf.DTS_MSG_ID_BLE_MSG_LOG, 
                                   ' confirm, instead received ', ret['msgId'])
                            raise StopScript( ''.join( map( str, logstr ) ) )
                        elif ret['msgIdx'] != 1:
                            logstr = ( 'SCRIPT: ERROR: Expected log with 1 entry, instead received', ret['msgIdx'])
                            raise StopScript( ''.join( map( str, logstr ) ) )
                        elif ret['evtCode0'] != ftdf.DTS_BLE_EVT_CODE_GAP_DISCONNECTED:
                            logstr = ( 'SCRIPT: ERROR: Expected log with 1 entry and evtCode ', 
                                   ftdf.DTS_BLE_EVT_CODE_GAP_DISCONNECTED, ' instead received ', ret['evtCode0'])
                            raise StopScript( ''.join( map( str, logstr ) ) )
                    else:
                        # Expect log with zero entries
                        res, ret = DTS_getMsg( devId2, responseTimeout )
                        if( res == False ):
                            raise StopScript( 'SCRIPT: ERROR: No response received from device' )
                        elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_MSG_LOG:
                            logstr = ( 'SCRIPT: ERROR: Expected msgId', ftdf.DTS_MSG_ID_BLE_MSG_LOG, 
                                   ' confirm, instead received ', ret['msgId'])
                            raise StopScript( ''.join( map( str, logstr ) ) )
                        elif ret['msgIdx'] != 0:
                            logstr = ( 'SCRIPT: ERROR: Expected log with 0 entries, instead received', ret['msgIdx'])
                            raise StopScript( ''.join( map( str, logstr ) ) )
                
                    # Disconnect if needed
                    if (bleConnIsLost == False):
                        status, reason = DTS_BLEConnectionClose(devId1, devId2, responseTimeout)
                        if ( status == ftdf.DTS_BLE_FUNC_STATUS_NO_RSP ):
                            raise StopScript( 'SCRIPT: ERROR: No response received from device' )
                        elif ( status == ftdf.DTS_BLE_FUNC_STATUS_MSG_ID):
                            logstr = ( 'SCRIPT: ERROR: Expected msgId ', reason['expected'], ' instead received ', 
                                   reason['received'] )
                            raise StopScript( ''.join( map( str, logstr ) ) )
                        elif ( status == ftdf.DTS_BLE_FUNC_STATUS_BLE_EVT):
                            logstr = ( 'SCRIPT: ERROR: Expected evt_code ', reason['expected'], ' instead received ', 
                                   reason['received'] )
                            raise StopScript( ''.join( map( str, logstr ) ) )
                

                    break
                    
                meas.append({'repetition': k, 'ble_params': j, 'interval': i, 'ble_lost': bleConnIsLost, 'blePER': blePER})
            i += i_step

dtsLog.info('measurements')
for j in range(len(meas)):
    dtsLog.info(repr(meas[j]))
    
dtsLog.info('bleParams')
for j in range(J):
    dtsLog.info(repr(bleParams[j]))

if (partA):
    dtsLog.info('ftdfRateNoAckNoCoexCca')
    for j in range(J):
        dtsLog.info(repr(ftdfRateNoAckNoCoexCca[j]))
               
    dtsLog.info('ftdfRateWithAckNoCoexCca')
    for j in range(J):
        dtsLog.info(repr(ftdfRateWithAckNoCoexCca[j]))
     
    dtsLog.info('ftdfRateNoAckCoexCca')
    for j in range(J):
        dtsLog.info(repr(ftdfRateNoAckCoexCca[j]))
     
    dtsLog.info('ftdfRateWithAckCoexCca')          
    for j in range(J):
        dtsLog.info(repr(ftdfRateWithAckCoexCca[j]))





