## Arbiter v1 behavior (PTI set 0, MAC vs MAC tests).
## FTDF priority set over BLE
## Script tests the increasing loss caused on BLE traffic by increasing FTDF duty cycle. 
##  
## Steps
## ---------
## - 1< Set arbiter configuration FTDF priority over BLE
## - 1,2< Open BLE connection (DUT 1 peripheral, DUT 2 central) with strict supervision timeout
## - 1,2< Verify BLE connection
## - Wait a few seconds
## - 1,2< Verify BLE connection
## - 1,2< Close BLE connection
## - 1,2< Open BLE connection (DUT 1 peripheral, DUT 2 central) with strict supervision timeout
## - 1,2< Verify BLE connection
## - 1,2< Perform FTDF PER test (DUT 1 Tx, DUT 2 Rx)
## - 1,2< Verify BLE connection drop
## - 1,2< Open BLE connection (DUT 1 peripheral, DUT 2 central) with relaxed supervision timeout
## - 1,2< Verify BLE connection 
## - Wait a few seconds
## - 1,2< Verify BLE connection
## - 1,2< Close BLE connection
## - 1< Calculate BLE PER blePERFTDFCycleZero
## - 1,2< Open BLE connection (DUT 1 peripheral, DUT 2 central) with relaxed supervision timeout
## - 1,2< Verify BLE connection 
## - 1,2< Perform FTDF PER test (DUT 1 Tx, DUT 2 Rx) with low duty cycle
## - 1,2< Verify BLE connection
## - 1,2< Close BLE connection
## - 1< Calculate BLE PER blePERFTDFCycleLo
## - 1,2< Open BLE connection (DUT 1 peripheral, DUT 2 central) with relaxed supervision timeout
## - 1,2< Verify BLE connection 
## - 1,2< Perform FTDF PER test (DUT 1 Tx, DUT 2 Rx) with high duty cycle
## - 1,2< Verify BLE connection
## - 1,2< Close BLE connection
## - 1< Calculate BLE PER blePERFTDFCycleHi
## - Verify blePERFTDFCycleZero < blePERFTDFCycleLo
## - Verify blePERFTDFCycleLo < blePERFTDFCycleHi

import sys    #cli arguments
import time    #sleep

from scriptIncludes import *

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

# time.sleep(4)

nrOfFrames = 1000
sduLength = 100
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

# Prepare test messages
msgFlow = ( devId1, msgRESET, ftdf.FTDF_RESET_CONFIRM,
            devId2, msgRESET, ftdf.FTDF_RESET_CONFIRM,
            
            devId1, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
            
            devId1, msgSET_Dev1_ShortAddress, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_Dev2_ShortAddress, ftdf.FTDF_SET_CONFIRM)

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

# =================================================================================================#

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

# Start the connection 
status, reason = DTS_BLEConnectionOpen( devId1, devId2, 100, 40, 56, 0, 42)

# Enable BLE message log on both devices
DTS_BLEMsgLogEnable(devId1)
DTS_BLEMsgLogEnable(devId2)

# Wait for 7 seconds
time.sleep(7)

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

# Get stats for calculating PER
DTS_BleStatsReq(devId1)

res, ret = DTS_getMsg( devId1, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_STATS:
    logstr = ( 'SCRIPT: ERROR: Expected msgId', ftdf.DTS_MSG_ID_BLE_STATS, 
               ' confirm, instead received ', ret['msgId'])
    raise StopScript( ''.join( map( str, logstr ) ) )

#######################################################
# Now make the same test with FTDF traffic
#########################################################

# Start the connection 
status, reason = DTS_BLEConnectionOpen( devId1, devId2, 100, 40, 56, 0, 42)

# Enable BLE message log on both devices
DTS_BLEMsgLogEnable(devId1)
DTS_BLEMsgLogEnable(devId2)

# Start FTDF traffic
status, reason, txPkt, rxPkt, duration = DTS_FTDFPERTest(devId1, devId2, msgDATA, nrOfFrames, 0, 
                                               responseTimeout, msgRxEnable_On, msgRxEnable_Off)
if ( status != ftdf.DTS_BLE_FUNC_STATUS_OK):
    logstr = ( 'SCRIPT: ERROR: Expected status ', ftdf.DTS_BLE_FUNC_STATUS_OK, ' instead received ', 
               status )
    raise StopScript( ''.join( map( str, logstr ) ) )

# Disable log.
DTS_BLEMsgLogDisable(devId1)

# Expect log with one entry
res, ret = DTS_getMsg( devId1, responseTimeout )
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

# Disable log.
DTS_BLEMsgLogDisable(devId2)

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

DTS_BleStatsReq(devId1)

res, ret = DTS_getMsg( devId1, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_STATS:
    logstr = ( 'SCRIPT: ERROR: Expected msgId', ftdf.DTS_MSG_ID_BLE_STATS, 
               ' confirm, instead received ', ret['msgId'])
    raise StopScript( ''.join( map( str, logstr ) ) )

####################################################################################################
# BLE PER tests

# Start the connection 
status, reason = DTS_BLEConnectionOpen( devId1, devId2, 10, 10, 10, 0, 400)

# Enable BLE message log on both devices
DTS_BLEMsgLogEnable(devId1)
DTS_BLEMsgLogEnable(devId2)

# Wait for 7 seconds
time.sleep(7)

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

# Get stats for calculating PER
DTS_BleStatsReq(devId1)

res, ret = DTS_getMsg( devId1, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_STATS:
    logstr = ( 'SCRIPT: ERROR: Expected msgId', ftdf.DTS_MSG_ID_BLE_STATS, 
               ' confirm, instead received ', ret['msgId'])
    raise StopScript( ''.join( map( str, logstr ) ) )

blePERFTDFCycleZero = ret['bleDataPacketErrors'] / ret['bleTotalDataPackets']

#######################################################
# Now make the same test with low FTDF traffic
#########################################################

# Start the connection 
status, reason = DTS_BLEConnectionOpen( devId1, devId2, 10, 10, 10, 0, 400)

# Enable BLE message log on both devices
DTS_BLEMsgLogEnable(devId1)
DTS_BLEMsgLogEnable(devId2)

# Start low-rate FTDF traffic
status, reason, txPkt, rxPkt, duration = DTS_FTDFPERTest(devId1, devId2, msgDATA, nrOfFrames, 30000, 
                                               responseTimeout, msgRxEnable_On, msgRxEnable_Off)
if ( status != ftdf.DTS_BLE_FUNC_STATUS_OK):
    logstr = ( 'SCRIPT: ERROR: Expected status ', ftdf.DTS_BLE_FUNC_STATUS_OK, ' instead received ', 
               status )
    raise StopScript( ''.join( map( str, logstr ) ) )

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

# Get stats for calculating PER
DTS_BleStatsReq(devId1)

res, ret = DTS_getMsg( devId1, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_STATS:
    logstr = ( 'SCRIPT: ERROR: Expected msgId', ftdf.DTS_MSG_ID_BLE_STATS, 
               ' confirm, instead received ', ret['msgId'])
    raise StopScript( ''.join( map( str, logstr ) ) )

blePERFTDFCycleLo = ret['bleDataPacketErrors'] / ret['bleTotalDataPackets']

#######################################################
# Now make the same test with low FTDF traffic
#########################################################

# Start the connection 
status, reason = DTS_BLEConnectionOpen( devId1, devId2, 10, 10, 10, 0, 400)

# Enable BLE message log on both devices
DTS_BLEMsgLogEnable(devId1)
DTS_BLEMsgLogEnable(devId2)

# Start low-rate FTDF traffic
status, reason, txPkt, rxPkt, duration = DTS_FTDFPERTest(devId1, devId2, msgDATA, nrOfFrames, 15000, 
                                               responseTimeout, msgRxEnable_On, msgRxEnable_Off)
if ( status != ftdf.DTS_BLE_FUNC_STATUS_OK):
    logstr = ( 'SCRIPT: ERROR: Expected status ', ftdf.DTS_BLE_FUNC_STATUS_OK, ' instead received ', 
               status )
    raise StopScript( ''.join( map( str, logstr ) ) )

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

# Get stats for calculating PER
DTS_BleStatsReq(devId1)

res, ret = DTS_getMsg( devId1, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_STATS:
    logstr = ( 'SCRIPT: ERROR: Expected msgId', ftdf.DTS_MSG_ID_BLE_STATS, 
               ' confirm, instead received ', ret['msgId'])
    raise StopScript( ''.join( map( str, logstr ) ) )

blePERFTDFCycleHi = ret['bleDataPacketErrors'] / ret['bleTotalDataPackets']

if (blePERFTDFCycleZero >= blePERFTDFCycleLo):
    logstr = ( 'SCRIPT: ERROR: BLE PER with zero FTDF duty cycle ', blePERFTDFCycleZero, 
               ' is expected to be less than PER on low FTDF cycle ', 
               blePERFTDFCycleLo)
    raise StopScript( ''.join( map( str, logstr ) ) )

if (blePERFTDFCycleLo >= blePERFTDFCycleHi):
    logstr = ( 'SCRIPT: ERROR: BLE PER on low FTDF duty cycle ', blePERFTDFCycleLo, 
               ' are expected to be less than PER on high FTDF cycle ', 
               blePERFTDFCycleHi)
    raise StopScript( ''.join( map( str, logstr ) ) )

# All OK
# =================================================================================================#



