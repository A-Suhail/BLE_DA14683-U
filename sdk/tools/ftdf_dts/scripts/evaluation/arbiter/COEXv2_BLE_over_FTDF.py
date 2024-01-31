## Arbiter v2 behavior (Auto PTI, MAC-PTI pair vs MAC-PTI pair).
## BLE priority over FTDF 
## Script tests the loss caused on FTDF TX (PTI=1) and RX (PTI=2) by BLE active scanning (PTI=4).
## (Any BLE operation could be used, scanning is the easiest one to configure duty cycle)  
## 
## Steps
## ---------
## - 2< Set FTDF TX PTI=1, RX PTI=2
## - 2< Set Arbiter configuration 0=(BLE, 4), 1=(FTDF, 2)
## - 1,2< Perform FTDF PER test (DUT 1 Tx, DUT 2 Rx)
## - rxPktBLECycleZero = FTDFPERTest[RxPkt]
## - 2< Start BLE active scan
## - 1,2< Perform FTDF PER test (DUT 1 Tx, DUT 2 Rx)
## - rxPktBLEActiveScanHiPrio = = FTDFPERTest[RxPkt]
## - 2< Stop BLE active scan
## - Verify rxPktBLEActiveScanHiPrio < rxPktBLECycleZero
## - 2< Set Arbiter configuration 0=(FTDF,2), 1=(BLE, 4)
## - 2< Start BLE active scan
## - 1,2< Perform FTDF PER test (DUT 1 Tx, DUT 2 Rx)
## - rxPktBLEActiveScanLoPrio = = FTDFPERTest[RxPkt]
## - 2< Stop BLE active scan
## - Verify rxPktBLEActiveScanHiPrio < rxPktBLEActiveScanLoPrio
## - 2< Set Arbiter configuration 0=(BLE, 4), 1=(FTDF, 1)
## - 2< Start BLE active scan
## - 1,2< Perform FTDF PER test (DUT 2 Tx, DUT 1 Rx)
## - rxPktBLEActiveScanHiPrio = = FTDFPERTest[RxPkt]
## - 2< Stop BLE active scan
## - Verify rxPktBLEActiveScanHiPrio < rxPktBLECycleZero
## - 2< Set Arbiter configuration 0=(FTDF, 1), 1=(BLE, 4)
## - 2< Start BLE active scan
## - 1,2< Perform FTDF PER test (DUT 1 Tx, DUT 2 Rx)
## - rxPktBLEActiveScanLoPrio = = FTDFPERTest[RxPkt]
## - 2< Stop BLE active scan
## - Verify rxPktBLEActiveScanHiPrio < rxPktBLEActiveScanLoPrio


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
            'ackTX': True,
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

msgSET_PtiConfig = { 'msgId': ftdf.FTDF_SET_REQUEST,
            'PIBAttribute': ftdf.FTDF_PIB_PTI_CONFIG,
            'PIBAttributeValue': [2, 1, 3, 4, 5, 6, 7, 8] }


msgCoex_StatsReq = { 'msgId': ftdf.DTS_MSG_ID_COEX_STATS
                    }

# Prepare test messages
msgFlow = ( devId1, msgRESET, ftdf.FTDF_RESET_CONFIRM,
            devId2, msgRESET, ftdf.FTDF_RESET_CONFIRM,
            
            devId1, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
            
            devId1, msgSET_Dev1_ShortAddress, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_Dev2_ShortAddress, ftdf.FTDF_SET_CONFIRM,
            
            # devId1, msgSET_PtiConfig, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_PtiConfig, ftdf.FTDF_SET_CONFIRM,
            )


msgDbgModeSetRequest = {
           'msgId'  : ftdf.FTDF_DBG_MODE_SET_REQUEST,
           'dbgMode': 0x1,
}

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


# time.sleep(5)
# =================================================================================================#
# Reset arbiter
DTS_ArbiterReset(devId2)
  
# Set arbiter configuration BLE active scanning above FTDF Rx
DTS_ArbiterSetConfig(devId2, 0x07f0, 0, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_BLE, 4,
                     ftdf.DTS_COEX_MAC_TYPE_FTDF, 2,
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

# Measure resident PER (without BLE interferece)
status, reason, txPkt, rxPktBLECycleZero, duration = DTS_FTDFPERTest(devId1, devId2, msgDATA, 
                                                                     nrOfFrames, 0, 
                                                                     responseTimeout, 
                                                                     msgRxEnable_On, 
                                                                     msgRxEnable_Off)
if ( status != ftdf.DTS_BLE_FUNC_STATUS_OK):
    logstr = ( 'SCRIPT: ERROR: Expected status ', ftdf.DTS_BLE_FUNC_STATUS_OK, ' instead received ', 
               status )
    raise StopScript( ''.join( map( str, logstr ) ) )

#######################################################
# Now make the same test with BLE active scanning
#########################################################

DTS_BLEMsgLogEnable(devId2)

# Start central
DTS_BLEScan( devId2, ftdf.DTS_BLE_GAP_SCAN_ACTIVE, 160, 80 )
# Expect OK
res, ret = DTS_getMsg( devId2, responseTimeout)
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_BLE_OK, 
               ' confirm, instead received ', ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

# Measure PER with BLE active scanning on priority
status, reason, txPkt, rxPktBLEActiveScanHiPrio, duration = DTS_FTDFPERTest(devId1, devId2, msgDATA, 
                                                                     nrOfFrames, 0, 
                                                                     responseTimeout, 
                                                                     msgRxEnable_On, 
                                                                     msgRxEnable_Off)

if ( status != ftdf.DTS_BLE_FUNC_STATUS_OK):
    logstr = ( 'SCRIPT: ERROR: Expected status ', ftdf.DTS_BLE_FUNC_STATUS_OK, ' instead received ', 
               status )
    raise StopScript( ''.join( map( str, logstr ) ) )

# Disable log.
DTS_BLEMsgLogDisable(devId2)

# Expect log 
res, ret = DTS_getMsg( devId2, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_MSG_LOG:
    logstr = ( 'SCRIPT: ERROR: Expected msgId', ftdf.DTS_MSG_ID_BLE_MSG_LOG, 
               ' confirm, instead received ', ret['msgId'])
    raise StopScript( ''.join( map( str, logstr ) ) )

if rxPktBLEActiveScanHiPrio >= rxPktBLECycleZero:
    logstr = ( 'SCRIPT: ERROR: rxPktBLEActiveScanHiPrio = ', rxPktBLEActiveScanHiPrio, 
               ' is greater than  or equal to rxPktBLECycleZero = ', rxPktBLECycleZero )
    raise StopScript( ''.join( map( str, logstr ) ) )

# Change arbiter configuration and perform the same test
DTS_ArbiterSetConfig(devId2, 0x07f0, 0, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_FTDF, 2,
                     ftdf.DTS_COEX_MAC_TYPE_BLE, 4,
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

DTS_BLEMsgLogEnable(devId2)

# Start central
DTS_BLEScan( devId2, ftdf.DTS_BLE_GAP_SCAN_ACTIVE, 160, 80 )
# Expect OK
res, ret = DTS_getMsg( devId2, responseTimeout)
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_BLE_OK, 
               ' confirm, instead received ', ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

# Measure PER with BLE active scanning on priority
status, reason, txPkt, rxPktBLEActiveScanLoPrio, duration = DTS_FTDFPERTest(devId1, devId2, msgDATA, 
                                                                     nrOfFrames, 0, 
                                                                     responseTimeout, 
                                                                     msgRxEnable_On, 
                                                                     msgRxEnable_Off)

if ( status != ftdf.DTS_BLE_FUNC_STATUS_OK):
    logstr = ( 'SCRIPT: ERROR: Expected status ', ftdf.DTS_BLE_FUNC_STATUS_OK, ' instead received ', 
               status )
    raise StopScript( ''.join( map( str, logstr ) ) )

# Disable log.
DTS_BLEMsgLogDisable(devId2)

# Expect log 
res, ret = DTS_getMsg( devId2, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_MSG_LOG:
    logstr = ( 'SCRIPT: ERROR: Expected msgId', ftdf.DTS_MSG_ID_BLE_MSG_LOG, 
               ' confirm, instead received ', ret['msgId'])
    raise StopScript( ''.join( map( str, logstr ) ) )

if rxPktBLEActiveScanHiPrio >= rxPktBLEActiveScanLoPrio:
    logstr = ( 'SCRIPT: ERROR: rxPktBLEActiveScanHiPrio = ', rxPktBLEActiveScanHiPrio, 
               ' is greater than  or equal to rxPktBLEActiveScanLoPrio = ', rxPktBLEActiveScanLoPrio )
    raise StopScript( ''.join( map( str, logstr ) ) )

# Reset arbiter
DTS_ArbiterReset(devId1)
DTS_ArbiterReset(devId2)

##############################################################################
# Check with BLE active scanning over FTDF Tx
##############################################################################
  
# Set arbiter configuration BLE active scanning above FTDF Tx
DTS_ArbiterSetConfig(devId2, 0x07f0, 0, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_BLE, 4,
                     ftdf.DTS_COEX_MAC_TYPE_FTDF, 1,
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

DTS_BLEMsgLogEnable(devId2)
 
# Start central
DTS_BLEScan( devId2, ftdf.DTS_BLE_GAP_SCAN_ACTIVE, 160, 80 )
# Expect OK
res, ret = DTS_getMsg( devId2, responseTimeout)
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_BLE_OK, 
               ' confirm, instead received ', ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

msgDATA['dstAddr'] = 0x0010

# Measure PER with BLE active scanning on priority
status, reason, txPkt, rxPktBLEActiveScanHiPrio, duration = DTS_FTDFPERTest(devId2, devId1, msgDATA, 
                                                                     nrOfFrames, 0, 
                                                                     responseTimeout, 
                                                                     msgRxEnable_On, 
                                                                     msgRxEnable_Off)

if ( status != ftdf.DTS_BLE_FUNC_STATUS_OK):
    logstr = ( 'SCRIPT: ERROR: Expected status ', ftdf.DTS_BLE_FUNC_STATUS_OK, ' instead received ', 
               status )
    raise StopScript( ''.join( map( str, logstr ) ) )

# Disable log.
DTS_BLEMsgLogDisable(devId2)

# Expect log 
res, ret = DTS_getMsg( devId2, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_MSG_LOG:
    logstr = ( 'SCRIPT: ERROR: Expected msgId', ftdf.DTS_MSG_ID_BLE_MSG_LOG, 
               ' confirm, instead received ', ret['msgId'])
    raise StopScript( ''.join( map( str, logstr ) ) )
 
 
if rxPktBLEActiveScanHiPrio >= rxPktBLECycleZero:
    logstr = ( 'SCRIPT: ERROR: rxPktBLEActiveScanHiPrio = ', rxPktBLEActiveScanHiPrio, 
               ' is greater than  or equal to rxPktBLECycleZero = ', rxPktBLECycleZero )
    raise StopScript( ''.join( map( str, logstr ) ) )

# Change arbiter configuration and perform the same test
DTS_ArbiterSetConfig(devId2, 0x07f0, 0, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_FTDF, 1,
                     ftdf.DTS_COEX_MAC_TYPE_BLE, 4,
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

DTS_BLEMsgLogEnable(devId2)
 
# Start central
DTS_BLEScan( devId2, ftdf.DTS_BLE_GAP_SCAN_ACTIVE, 160, 80 )
# Expect OK
res, ret = DTS_getMsg( devId2, responseTimeout)
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_BLE_OK, 
               ' confirm, instead received ', ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

# Measure PER with BLE active scanning on priority
status, reason, txPkt, rxPktBLEActiveScanLoPrio, duration = DTS_FTDFPERTest(devId2, devId1, msgDATA, 
                                                                     nrOfFrames, 0, 
                                                                     responseTimeout, 
                                                                     msgRxEnable_On, 
                                                                     msgRxEnable_Off)

if ( status != ftdf.DTS_BLE_FUNC_STATUS_OK):
    logstr = ( 'SCRIPT: ERROR: Expected status ', ftdf.DTS_BLE_FUNC_STATUS_OK, ' instead received ', 
               status )
    raise StopScript( ''.join( map( str, logstr ) ) )

# Disable log.
DTS_BLEMsgLogDisable(devId2)
 
# Expect log 
res, ret = DTS_getMsg( devId2, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_MSG_LOG:
    logstr = ( 'SCRIPT: ERROR: Expected msgId', ftdf.DTS_MSG_ID_BLE_MSG_LOG, 
               ' confirm, instead received ', ret['msgId'])
    raise StopScript( ''.join( map( str, logstr ) ) )
 
 
if rxPktBLEActiveScanHiPrio >= rxPktBLEActiveScanLoPrio:
    logstr = ( 'SCRIPT: ERROR: rxPktBLEActiveScanHiPrio = ', rxPktBLEActiveScanHiPrio, 
               ' is greater than  or equal to rxPktBLEActiveScanLoPrio = ', rxPktBLEActiveScanLoPrio )
    raise StopScript( ''.join( map( str, logstr ) ) )

# Reset arbiter
DTS_ArbiterReset(devId1)
DTS_ArbiterReset(devId2)
