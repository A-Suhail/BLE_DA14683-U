## Arbiter v2 behavior (Auto PTI, MAC-PTI pair vs MAC-PTI pair).
## Arbiter interrupts/statistics tests, including overvlow feature
##
## Steps
## ---------
## - 1< Set FTDF TX PTI=1, RX PTI=2
## - 1< Reset Arbiter
## - 1< Set Arbiter configuration 0=(BLE, 4), 1=(FTDF, 2)
## - 1< Enable FTDF Rx
## - 1< Start BLE active scanning
## - 1< Stop BLE active scanning
## - 1< Disable FTDF Rx
## - 1< Get arbiter stats and verify them: 
##   txpass1 == 0, rxpass1 != 0, txmask1 == 0, rxmask1 == 0, 
##   txpass2 == 0, rxpass2 == 0, txmask2 == 0, rxmask2 == 1
## - 1< Reset Arbiter  
## - 1< Set Arbiter configuration 0=(FTDF, 2), 1=(BLE, 4)
## - 1< Enable FTDF Rx
## - 1< Start BLE active scanning
## - 1< Stop BLE active scanning
## - 1< Disable FTDF Rx
## - 1< Get arbiter stats and verify them: 
##   txpass1 == 0, rxpass1 == 1, txmask1 == 0, rxmask1 == 0, 
##   txpass2 == 0, rxpass2 == 0, txmask2 == 0, rxmask2 != 0
## - 1< Reset Arbiter  
## - 1< Set Arbiter configuration 0=(FTDF, 2), 1=(BLE, 4)
## - 1< Disable COEX IRQ  
## - 1< Enable FTDF Rx
## - 1< Start BLE active scanning
## - 1< Stop BLE active scanning
## - 1< Enable COEX IRQ  
## - 1< Get arbiter stats and verify overflow != 0
## - 1< Disable FTDF Rx
## - 1< Reset Arbiter  
## - 1< Set Arbiter configuration 0=(FTDF, 2), 1=(BLE, 5)
## - 1< Enable FTDF Rx
## - 1< Start BLE connectable advertising
## - 1< Stop BLE connectable advertising
## - 1< Disable FTDF Rx
## - 1< Get arbiter stats and verify them: 
##   txpass1 == 0, rxpass1 == 1, txmask1 == 0, rxmask1 == 0, 
##   txpass2 == 0, rxpass2 == 0, txmask2 != 0, rxmask2 != 0
## - 1< Reset Arbiter  
## - 1< Set Arbiter configuration 0=(BLE, 5), 1=(FTDF, 2)
## - 1< Enable FTDF Rx
## - 1< Start BLE connectable advertising
## - 1< Stop BLE connectable advertising
## - 1< Disable FTDF Rx
## - 1< Get arbiter stats and verify them: 
##   txpass1 != 0, rxpass1 != 0, txmask1 == 0, rxmask1 == 0, 
##   txpass2 == 0, rxpass2 == 0, txmask2 == 0, rxmask2 == 1
## - 1< Reset Arbiter  
## - 1< Set Arbiter configuration 0=(BLE, 5), 1=(FTDF, 1)
## - 1< Start BLE connectable advertising
## - 1,2< Perform FTDF PER test (DUT 1 Tx, DUT 2 Rx)
## - 1< Stop BLE connectable advertising
## - 1< Get arbiter stats and verify them: 
##   txpass1 != 0, rxpass1 != 0, txmask1 == 0, rxmask1 == 0, 
##   txmask2 != 0, rxmask2 != 0
## - 1< Reset Arbiter  
## - 1< Set Arbiter configuration 0=(FTDF, 1), 1=(BLE, 5)
## - 1< Start BLE connectable advertising
## - 1,2< Perform FTDF PER test (DUT 1 Tx, DUT 2 Rx)
## - 1< Stop BLE connectable advertising
## - 1< Get arbiter stats and verify them: 
##   txpass1 != 0, rxpass1 != 0, txmask1 == 0, rxmask1 == 0, 
##   txmask2 != 0, rxmask2 != 0
 


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
            
            devId1, msgSET_PtiConfig, ftdf.FTDF_SET_CONFIRM,
            )


msgDbgModeSetRequest = {
    'msgId': ftdf.FTDF_DBG_MODE_SET_REQUEST,
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
DTS_ArbiterReset(devId1)
DTS_ArbiterReset(devId2)
  
# Set arbiter configuration so that BLE active scanning is above FTDF Rx
DTS_ArbiterSetConfig(devId1, 0x07f0, 0, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_BLE, 4,
                     ftdf.DTS_COEX_MAC_TYPE_FTDF, 2,
                     ftdf.DTS_COEX_MAC_TYPE_EXT, 0,
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

# Turn Rx on 
DTS_sndMsg(devId1, msgRxEnable_On)
    
# Expect confirm
res, ret = DTS_getMsg(devId1, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM:
    logstr = ( 'SCRIPT: ERROR: Expected ', msgNameStr[ ftdf.FTDF_RX_ENABLE_CONFIRM - 1], 
               ', instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )


# Start scanning
DTS_BLEScan( devId1, ftdf.DTS_BLE_GAP_SCAN_ACTIVE, 160, 80 )
# Expect OK
res, ret = DTS_getMsg( devId1, responseTimeout)
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_BLE_OK, 
               ' confirm, instead received ', ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

# time.sleep(2)

DTS_BLEStop( devId1 )
# Get 0 or more reports
while 1:
    res, ret = DTS_getMsg( devId1, responseTimeout)
    if ( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    elif (ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK) and (ret['msgId'] != ftdf.DTS_MSG_ID_BLE_EVT):
        logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_BLE_OK, ' or ', ftdf.DTS_MSG_ID_BLE_EVT,
                   ' , instead received ', ret['msgId'] )
        raise StopScript( ''.join( map( str, logstr ) ) )
    
    if ret['msgId'] == ftdf.DTS_MSG_ID_BLE_OK:
        break;
    else:
        continue;
    
# Expect Scan complete 
res, ret = DTS_getMsg( devId1, responseTimeout)
if ( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_EVT:
    logstr = ( 'SCRIPT: ERROR: Expected msgId ', ftdf.DTS_MSG_ID_BLE_EVT, ' instead received ', 
               ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )
elif ret['evt_code'] != ftdf.DTS_BLE_EVT_CODE_GAP_SCAN_COMPLETED:
    logstr = ( 'SCRIPT: ERROR: Expected evt_code ', ftdf.DTS_BLE_EVT_CODE_GAP_SCAN_COMPLETED, 
               ' instead received ', ret['evt_code'] )
    raise StopScript( ''.join( map( str, logstr ) ) )


# Turn Rx off
DTS_sndMsg(devId1, msgRxEnable_Off)
    
# Expect confirm
res, ret = DTS_getMsg(devId1, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM:
    logstr = ( 'SCRIPT: ERROR: Expected ', msgNameStr[ ftdf.FTDF_RX_ENABLE_CONFIRM - 1], 
               ', instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )

DTS_CoexStatsReq(devId1)

# Expect arbiter stats
res, ret = DTS_getMsg( devId1, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_COEX_STATS:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_COEX_STATS, 
               ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )
 
if ret['txrxMonOverflow'] != 0:
    logstr = ( 'SCRIPT: ERROR: Expected 0 txrxMonOverflow, instead received ', 
               ret['txrxMonOverflow'] )
    raise StopScript( ''.join( map( str, logstr ) ) )   

# BLE TxMasked should be 0
if ret['txrxMonTxMasked1'] != 0:
    logstr = ( 'SCRIPT: ERROR: Expected 0 txrxMonTxMasked1, instead received ', 
               ret['txrxMonTxMasked1'] )
    raise StopScript( ''.join( map( str, logstr ) ) )   

# BLE RxMasked should be 0
if ret['txrxMonRxMasked1'] != 0:
    logstr = ( 'SCRIPT: ERROR: Expected 0 txrxMonRxMasked1, instead received ', 
               ret['txrxMonRxMasked1'] )
    raise StopScript( ''.join( map( str, logstr ) ) )   

# BLE RxPassed should be non-zero
if ret['txrxMonRxPassed1'] == 0:
    logstr = ( 'SCRIPT: ERROR: Expected non-zero txrxMonRxPassed1, instead received ', 
               ret['txrxMonRxPassed1'] )
    raise StopScript( ''.join( map( str, logstr ) ) )  

# FTDF Tx Masked should be 0
if ret['txrxMonTxMasked2'] != 0:
    logstr = ( 'SCRIPT: ERROR: Expected 0 txrxMonTxMasked2, instead received ', 
               ret['txrxMonTxMasked2'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

# FTDF Tx Passed should be 0
if ret['txrxMonTxPassed2'] != 0:
    logstr = ( 'SCRIPT: ERROR: Expected 0 txrxMonTxPassed2, instead received ', 
               ret['txrxMonTxPassed2'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

# FTDF Rx Masked should be 1
if ret['txrxMonRxMasked2'] != 1:
    logstr = ( 'SCRIPT: ERROR: Expected 1 txrxMonRxMasked2, instead received ', 
               ret['txrxMonRxMasked2'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

# FTDF Tx Passed should be 0
if ret['txrxMonRxPassed2'] != 0:
    logstr = ( 'SCRIPT: ERROR: Expected 0 txrxMonRxPassed2, instead received ', 
               ret['txrxMonRxPassed2'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

DTS_ArbiterReset(devId1)

# Set arbiter configuration so that FTDF Rx BLE is above active scanning 
DTS_ArbiterSetConfig(devId1, 0x07f0, 0, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_FTDF, 2,
                     ftdf.DTS_COEX_MAC_TYPE_BLE, 4,
                     ftdf.DTS_COEX_MAC_TYPE_EXT, 0,
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


# Turn Rx on 
DTS_sndMsg(devId1, msgRxEnable_On)
    
# Expect confirm
res, ret = DTS_getMsg(devId1, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM:
    logstr = ( 'SCRIPT: ERROR: Expected ', msgNameStr[ ftdf.FTDF_RX_ENABLE_CONFIRM - 1], 
               ', instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )


# Start scanning
DTS_BLEScan( devId1, ftdf.DTS_BLE_GAP_SCAN_ACTIVE, 160, 80 )
# Expect OK
res, ret = DTS_getMsg( devId1, responseTimeout)
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_BLE_OK, 
               ' confirm, instead received ', ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

# time.sleep(2)

DTS_BLEStop( devId1 )
# Get 0 or more reports
while 1:
    res, ret = DTS_getMsg( devId1, responseTimeout)
    if ( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    elif (ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK) and (ret['msgId'] != ftdf.DTS_MSG_ID_BLE_EVT):
        logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_BLE_OK, ' or ', ftdf.DTS_MSG_ID_BLE_EVT,
                   ' , instead received ', ret['msgId'] )
        raise StopScript( ''.join( map( str, logstr ) ) )
    
    if ret['msgId'] == ftdf.DTS_MSG_ID_BLE_OK:
        break;
    else:
        continue;
    
# Expect Scan complete 
res, ret = DTS_getMsg( devId1, responseTimeout)
if ( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_EVT:
    logstr = ( 'SCRIPT: ERROR: Expected msgId ', ftdf.DTS_MSG_ID_BLE_EVT, ' instead received ', 
               ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )
elif ret['evt_code'] != ftdf.DTS_BLE_EVT_CODE_GAP_SCAN_COMPLETED:
    logstr = ( 'SCRIPT: ERROR: Expected evt_code ', ftdf.DTS_BLE_EVT_CODE_GAP_SCAN_COMPLETED, 
               ' instead received ', ret['evt_code'] )
    raise StopScript( ''.join( map( str, logstr ) ) )


# Turn Rx off
DTS_sndMsg(devId1, msgRxEnable_Off)
    
# Expect confirm
res, ret = DTS_getMsg(devId1, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM:
    logstr = ( 'SCRIPT: ERROR: Expected ', msgNameStr[ ftdf.FTDF_RX_ENABLE_CONFIRM - 1], 
               ', instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )

DTS_CoexStatsReq(devId1)

# Expect arbiter stats
res, ret = DTS_getMsg( devId1, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_COEX_STATS:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_COEX_STATS, 
               ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )
 
if ret['txrxMonOverflow'] != 0:
    logstr = ( 'SCRIPT: ERROR: Expected 0 txrxMonOverflow, instead received ', 
               ret['txrxMonOverflow'] )
    raise StopScript( ''.join( map( str, logstr ) ) )   

# FTDF TxMasked should be 0
if ret['txrxMonTxMasked1'] != 0:
    logstr = ( 'SCRIPT: ERROR: Expected 0 txrxMonTxMasked1, instead received ', 
               ret['txrxMonTxMasked1'] )
    raise StopScript( ''.join( map( str, logstr ) ) )   

# FTDF RxMasked should be 0
if ret['txrxMonRxMasked1'] != 0:
    logstr = ( 'SCRIPT: ERROR: Expected 0 txrxMonRxMasked1, instead received ', 
               ret['txrxMonRxMasked1'] )
    raise StopScript( ''.join( map( str, logstr ) ) )   

# FTDF RxPassed should be one
if ret['txrxMonRxPassed1'] != 1:
    logstr = ( 'SCRIPT: ERROR: Expected non-zero txrxMonRxPassed1, instead received ', 
               ret['txrxMonRxPassed1'] )
    raise StopScript( ''.join( map( str, logstr ) ) )  

# BLE Tx Masked should be 0
if ret['txrxMonTxMasked2'] != 0:
    logstr = ( 'SCRIPT: ERROR: Expected 0 txrxMonTxMasked2, instead received ', 
               ret['txrxMonTxMasked2'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

# BLE Tx Passed should be 0
if ret['txrxMonTxPassed2'] != 0:
    logstr = ( 'SCRIPT: ERROR: Expected 0 txrxMonTxPassed2, instead received ', 
               ret['txrxMonTxPassed2'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

# BLE Rx Masked should be non-zero
if ret['txrxMonRxMasked2'] == 0:
    logstr = ( 'SCRIPT: ERROR: Expected non-zero txrxMonRxMasked2, instead received ', 
               ret['txrxMonRxMasked2'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

# BLE Tx Passed should be 0
if ret['txrxMonRxPassed2'] != 0:
    logstr = ( 'SCRIPT: ERROR: Expected 0 txrxMonRxPassed2, instead received ', 
               ret['txrxMonRxPassed2'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

########################################################################################
# Overflow

# Set everything as before, but disable interrupt so that we can get an over flow 

DTS_ArbiterReset(devId1)

# Set arbiter configuration so that FTDF Rx BLE is above active scanning 
DTS_ArbiterSetConfig(devId1, 0x07f0, 0, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_FTDF, 2,
                     ftdf.DTS_COEX_MAC_TYPE_BLE, 4,
                     ftdf.DTS_COEX_MAC_TYPE_EXT, 0,
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

# Disable COEX IRQ
DTS_setRegister(devId1, 0xE000E180, 4, 0x00000020)

# Turn Rx on 
DTS_sndMsg(devId1, msgRxEnable_On)
    
# Expect confirm
res, ret = DTS_getMsg(devId1, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM:
    logstr = ( 'SCRIPT: ERROR: Expected ', msgNameStr[ ftdf.FTDF_RX_ENABLE_CONFIRM - 1], 
               ', instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )


# Start scanning
DTS_BLEScan( devId1, ftdf.DTS_BLE_GAP_SCAN_ACTIVE, 160, 80 )
# Expect OK
res, ret = DTS_getMsg( devId1, responseTimeout)
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_BLE_OK, 
               ' confirm, instead received ', ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

time.sleep(2)

DTS_BLEStop( devId1 )
# Get 0 or more reports
while 1:
    res, ret = DTS_getMsg( devId1, responseTimeout)
    if ( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    elif (ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK) and (ret['msgId'] != ftdf.DTS_MSG_ID_BLE_EVT):
        logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_BLE_OK, ' or ', ftdf.DTS_MSG_ID_BLE_EVT,
                   ' , instead received ', ret['msgId'] )
        raise StopScript( ''.join( map( str, logstr ) ) )
    
    if ret['msgId'] == ftdf.DTS_MSG_ID_BLE_OK:
        break;
    else:
        continue;
    
# Expect Scan complete 
res, ret = DTS_getMsg( devId1, responseTimeout)
if ( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_EVT:
    logstr = ( 'SCRIPT: ERROR: Expected msgId ', ftdf.DTS_MSG_ID_BLE_EVT, ' instead received ', 
               ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )
elif ret['evt_code'] != ftdf.DTS_BLE_EVT_CODE_GAP_SCAN_COMPLETED:
    logstr = ( 'SCRIPT: ERROR: Expected evt_code ', ftdf.DTS_BLE_EVT_CODE_GAP_SCAN_COMPLETED, 
               ' instead received ', ret['evt_code'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

# Ensable COEX IRQ
DTS_setRegister(devId1, 0xE000E100, 4, 0x00000020)

DTS_CoexStatsReq(devId1)

# Expect arbiter stats
res, ret = DTS_getMsg( devId1, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_COEX_STATS:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_COEX_STATS, 
               ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )
 
if ret['txrxMonOverflow'] != 1:
    logstr = ( 'SCRIPT: ERROR: Expected 1 txrxMonOverflow, instead received ', 
               ret['txrxMonOverflow'] )
    raise StopScript( ''.join( map( str, logstr ) ) )   


# Turn Rx off
DTS_sndMsg(devId1, msgRxEnable_Off)
    
# Expect confirm
res, ret = DTS_getMsg(devId1, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM:
    logstr = ( 'SCRIPT: ERROR: Expected ', msgNameStr[ ftdf.FTDF_RX_ENABLE_CONFIRM - 1], 
               ', instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )

##########################################################################################
# Verify Tx masked for BLE 
##########################################################################################
DTS_ArbiterReset(devId1)

# Set arbiter configuration so that FTDF Rx is above BLE connectable advertising 
DTS_ArbiterSetConfig(devId1, 0x07f0, 0, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_FTDF, 2,
                     ftdf.DTS_COEX_MAC_TYPE_BLE, 5,
                     ftdf.DTS_COEX_MAC_TYPE_EXT, 0,
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

# Turn Rx on 
DTS_sndMsg(devId1, msgRxEnable_On)
    
# Expect confirm
res, ret = DTS_getMsg(devId1, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM:
    logstr = ( 'SCRIPT: ERROR: Expected ', msgNameStr[ ftdf.FTDF_RX_ENABLE_CONFIRM - 1], 
               ', instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )

# Start devId1
DTS_BLEAdvertise( devId1, ftdf.DTS_BLE_GAP_CONN_MODE_UNDIRECTED, 1100, 1100 )
# Expect OK
res, ret = DTS_getMsg( devId1, responseTimeout)
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_BLE_OK, 
               ' confirm, instead received ', ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

DTS_BLEStop( devId1 )

# Expect OK
res, ret = DTS_getMsg( devId1, responseTimeout)
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_BLE_OK, 
               ' confirm, instead received ', ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

# Expect DTS_BLE_EVT_CODE_GAP_ADV_COMPLETED on devId1
res, ret = DTS_getMsg( devId1, responseTimeout)
if ( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_EVT:
    logstr = ( 'SCRIPT: ERROR: Expected msgId ', ftdf.DTS_MSG_ID_BLE_EVT, ' instead received ', 
               ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )
elif ret['evt_code'] != ftdf.DTS_BLE_EVT_CODE_GAP_ADV_COMPLETED:
    logstr = ( 'SCRIPT: ERROR: Expected evt_code ', ftdf.DTS_BLE_EVT_CODE_GAP_ADV_COMPLETED, 
               ' instead received ', ret['evt_code'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

# Turn Rx off
DTS_sndMsg(devId1, msgRxEnable_Off)
    
# Expect confirm
res, ret = DTS_getMsg(devId1, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM:
    logstr = ( 'SCRIPT: ERROR: Expected ', msgNameStr[ ftdf.FTDF_RX_ENABLE_CONFIRM - 1], 
               ', instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )

DTS_CoexStatsReq(devId1)

# Expect arbiter stats
res, ret = DTS_getMsg( devId1, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_COEX_STATS:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_COEX_STATS, 
               ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )
 
if ret['txrxMonOverflow'] != 0:
    logstr = ( 'SCRIPT: ERROR: Expected 0 txrxMonOverflow, instead received ', 
               ret['txrxMonOverflow'] )
    raise StopScript( ''.join( map( str, logstr ) ) )  

if ret['txrxMonTxMasked1'] != 0:
    logstr = ( 'SCRIPT: ERROR: Expected 0 txrxMonTxMasked1, instead received ', 
               ret['txrxMonTxMasked1'] )
    raise StopScript( ''.join( map( str, logstr ) ) )   

if ret['txrxMonRxMasked1'] != 0:
    logstr = ( 'SCRIPT: ERROR: Expected 0 txrxMonRxMasked1, instead received ', 
               ret['txrxMonRxMasked1'] )
    raise StopScript( ''.join( map( str, logstr ) ) )   

if ret['txrxMonTxPassed1'] != 0:
    logstr = ( 'SCRIPT: ERROR: Expected 0 txrxMonRxPassed1, instead received ', 
               ret['txrxMonRxPassed1'] )
    raise StopScript( ''.join( map( str, logstr ) ) )  

if ret['txrxMonRxPassed1'] != 1:
    logstr = ( 'SCRIPT: ERROR: Expected 1 txrxMonRxPassed1, instead received ', 
               ret['txrxMonRxPassed1'] )
    raise StopScript( ''.join( map( str, logstr ) ) )  

if ret['txrxMonTxMasked2'] == 0:
    logstr = ( 'SCRIPT: ERROR: Expected non-zero txrxMonTxMasked2, instead received ', 
               ret['txrxMonTxMasked2'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

if ret['txrxMonTxPassed2'] != 0:
    logstr = ( 'SCRIPT: ERROR: Expected 0 txrxMonTxPassed2, instead received ', 
               ret['txrxMonTxPassed2'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

if ret['txrxMonRxMasked2'] == 0:
    logstr = ( 'SCRIPT: ERROR: Expected non-zero txrxMonRxMasked2, instead received ', 
               ret['txrxMonRxMasked2'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

if ret['txrxMonRxPassed2'] != 0:
    logstr = ( 'SCRIPT: ERROR: Expected 0 txrxMonRxPassed2, instead received ', 
               ret['txrxMonRxPassed2'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

##########################################################################################
# Verify Tx passed for BLE 
##########################################################################################

DTS_ArbiterReset(devId1)

# Set arbiter configuration so that FTDF Rx is above BLE connectable advertising 
DTS_ArbiterSetConfig(devId1, 0x07f0, 0, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_BLE, 5,
                     ftdf.DTS_COEX_MAC_TYPE_FTDF, 2,
                     ftdf.DTS_COEX_MAC_TYPE_EXT, 0,
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

# Turn Rx on 
DTS_sndMsg(devId1, msgRxEnable_On)
    
# Expect confirm
res, ret = DTS_getMsg(devId1, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM:
    logstr = ( 'SCRIPT: ERROR: Expected ', msgNameStr[ ftdf.FTDF_RX_ENABLE_CONFIRM - 1], 
               ', instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )

# Start devId1
DTS_BLEAdvertise( devId1, ftdf.DTS_BLE_GAP_CONN_MODE_UNDIRECTED, 1100, 1100 )
# Expect OK
res, ret = DTS_getMsg( devId1, responseTimeout)
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_BLE_OK, 
               ' confirm, instead received ', ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

DTS_BLEStop( devId1 )

# Expect OK
res, ret = DTS_getMsg( devId1, responseTimeout)
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_BLE_OK, 
               ' confirm, instead received ', ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

# Expect DTS_BLE_EVT_CODE_GAP_ADV_COMPLETED on devId1
res, ret = DTS_getMsg( devId1, responseTimeout)
if ( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_EVT:
    logstr = ( 'SCRIPT: ERROR: Expected msgId ', ftdf.DTS_MSG_ID_BLE_EVT, ' instead received ', 
               ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )
elif ret['evt_code'] != ftdf.DTS_BLE_EVT_CODE_GAP_ADV_COMPLETED:
    logstr = ( 'SCRIPT: ERROR: Expected evt_code ', ftdf.DTS_BLE_EVT_CODE_GAP_ADV_COMPLETED, 
               ' instead received ', ret['evt_code'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

# Turn Rx off
DTS_sndMsg(devId1, msgRxEnable_Off)
    
# Expect confirm
res, ret = DTS_getMsg(devId1, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM:
    logstr = ( 'SCRIPT: ERROR: Expected ', msgNameStr[ ftdf.FTDF_RX_ENABLE_CONFIRM - 1], 
               ', instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )

DTS_CoexStatsReq(devId1)

# Expect arbiter stats
res, ret = DTS_getMsg( devId1, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_COEX_STATS:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_COEX_STATS, 
               ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )
 
if ret['txrxMonOverflow'] != 0:
    logstr = ( 'SCRIPT: ERROR: Expected 0 txrxMonOverflow, instead received ', 
               ret['txrxMonOverflow'] )
    raise StopScript( ''.join( map( str, logstr ) ) )  

if ret['txrxMonTxMasked1'] != 0:
    logstr = ( 'SCRIPT: ERROR: Expected 0 txrxMonTxMasked1, instead received ', 
               ret['txrxMonTxMasked1'] )
    raise StopScript( ''.join( map( str, logstr ) ) )   

if ret['txrxMonRxMasked1'] != 0:
    logstr = ( 'SCRIPT: ERROR: Expected 0 txrxMonRxMasked1, instead received ', 
               ret['txrxMonRxMasked1'] )
    raise StopScript( ''.join( map( str, logstr ) ) )   

if ret['txrxMonTxPassed1'] == 0:
    logstr = ( 'SCRIPT: ERROR: Expected non-zero txrxMonTxPassed1, instead received ', 
               ret['txrxMonRxPassed1'] )
    raise StopScript( ''.join( map( str, logstr ) ) )  

if ret['txrxMonRxPassed1'] == 0:
    logstr = ( 'SCRIPT: ERROR: Expected non-zero txrxMonRxPassed1, instead received ', 
               ret['txrxMonRxPassed1'] )
    raise StopScript( ''.join( map( str, logstr ) ) )  

if ret['txrxMonTxMasked2'] != 0:
    logstr = ( 'SCRIPT: ERROR: Expected 0 txrxMonTxMasked2, instead received ', 
               ret['txrxMonTxMasked2'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

if ret['txrxMonTxPassed2'] != 0:
    logstr = ( 'SCRIPT: ERROR: Expected 0 txrxMonTxPassed2, instead received ', 
               ret['txrxMonTxPassed2'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

if ret['txrxMonRxMasked2'] != 1:
    logstr = ( 'SCRIPT: ERROR: Expected 1 txrxMonRxMasked2, instead received ', 
               ret['txrxMonRxMasked2'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

if ret['txrxMonRxPassed2'] != 0:
    logstr = ( 'SCRIPT: ERROR: Expected 0 txrxMonRxPassed2, instead received ', 
               ret['txrxMonRxPassed2'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

##########################################################################################
# Verify Tx masked for FTDF 
##########################################################################################

DTS_ArbiterReset(devId1)

# Set arbiter configuration so that FTDF Tx is above BLE scanning
DTS_ArbiterSetConfig(devId1, 0x07f0, 0, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_BLE, 5,
                     ftdf.DTS_COEX_MAC_TYPE_FTDF, 1,
                     ftdf.DTS_COEX_MAC_TYPE_EXT, 0,
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


# Start devId1
DTS_BLEAdvertise( devId1, ftdf.DTS_BLE_GAP_CONN_MODE_UNDIRECTED, 1100, 1100 )
# Expect OK
res, ret = DTS_getMsg( devId1, responseTimeout)
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_BLE_OK, 
               ' confirm, instead received ', ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

# Measure PER
status, reason, txPkt, rxPkt, duration = DTS_FTDFPERTest(devId1, devId2, msgDATA, 
                                                                     nrOfFrames, 0, 
                                                                     responseTimeout, 
                                                                     msgRxEnable_On, 
                                                                     msgRxEnable_Off)
if ( status != ftdf.DTS_BLE_FUNC_STATUS_OK):
    logstr = ( 'SCRIPT: ERROR: Expected status ', ftdf.DTS_BLE_FUNC_STATUS_OK, ' instead received ', 
               status )
    raise StopScript( ''.join( map( str, logstr ) ) )


DTS_BLEStop( devId1 )

# Expect OK
res, ret = DTS_getMsg( devId1, responseTimeout)
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_BLE_OK, 
               ' confirm, instead received ', ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

# Expect DTS_BLE_EVT_CODE_GAP_ADV_COMPLETED on devId1
res, ret = DTS_getMsg( devId1, responseTimeout)
if ( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_EVT:
    logstr = ( 'SCRIPT: ERROR: Expected msgId ', ftdf.DTS_MSG_ID_BLE_EVT, ' instead received ', 
               ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )
elif ret['evt_code'] != ftdf.DTS_BLE_EVT_CODE_GAP_ADV_COMPLETED:
    logstr = ( 'SCRIPT: ERROR: Expected evt_code ', ftdf.DTS_BLE_EVT_CODE_GAP_ADV_COMPLETED, 
               ' instead received ', ret['evt_code'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

DTS_CoexStatsReq(devId1)

# Expect arbiter stats
res, ret = DTS_getMsg( devId1, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_COEX_STATS:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_COEX_STATS, 
               ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )
 
if ret['txrxMonOverflow'] != 0:
    logstr = ( 'SCRIPT: ERROR: Expected 0 txrxMonOverflow, instead received ', 
               ret['txrxMonOverflow'] )
    raise StopScript( ''.join( map( str, logstr ) ) )  

if ret['txrxMonTxMasked1'] != 0:
    logstr = ( 'SCRIPT: ERROR: Expected 0 txrxMonTxMasked1, instead received ', 
               ret['txrxMonTxMasked1'] )
    raise StopScript( ''.join( map( str, logstr ) ) )   

if ret['txrxMonRxMasked1'] != 0:
    logstr = ( 'SCRIPT: ERROR: Expected 0 txrxMonRxMasked1, instead received ', 
               ret['txrxMonRxMasked1'] )
    raise StopScript( ''.join( map( str, logstr ) ) )   

if ret['txrxMonTxPassed1'] == 0:
    logstr = ( 'SCRIPT: ERROR: Expected non-zero txrxMonTxPassed1, instead received ', 
               ret['txrxMonRxPassed1'] )
    raise StopScript( ''.join( map( str, logstr ) ) )  

if ret['txrxMonRxPassed1'] == 0:
    logstr = ( 'SCRIPT: ERROR: Expected non-zero txrxMonRxPassed1, instead received ', 
               ret['txrxMonRxPassed1'] )
    raise StopScript( ''.join( map( str, logstr ) ) )  

if ret['txrxMonTxMasked2'] == 0:
    logstr = ( 'SCRIPT: ERROR: Expected non-zero txrxMonTxMasked2, instead received ', 
               ret['txrxMonTxMasked2'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

if ret['txrxMonRxMasked2'] == 0:
    logstr = ( 'SCRIPT: ERROR: Expected non-zero txrxMonRxMasked2, instead received ', 
               ret['txrxMonRxMasked2'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

##########################################################################################
# Verify Tx passed for FTDF 
##########################################################################################

DTS_ArbiterReset(devId1)

# Set arbiter configuration so that FTDF Tx is above BLE scanning
DTS_ArbiterSetConfig(devId1, 0x07f0, 0, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_FTDF, 1,
                     ftdf.DTS_COEX_MAC_TYPE_BLE, 5,
                     ftdf.DTS_COEX_MAC_TYPE_EXT, 0,
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


# Start devId1
DTS_BLEAdvertise( devId1, ftdf.DTS_BLE_GAP_CONN_MODE_UNDIRECTED, 1100, 1100 )
# Expect OK
res, ret = DTS_getMsg( devId1, responseTimeout)
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_BLE_OK, 
               ' confirm, instead received ', ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

# Measure PER
status, reason, txPkt, rxPkt, duration = DTS_FTDFPERTest(devId1, devId2, msgDATA, 
                                                                     nrOfFrames, 0, 
                                                                     responseTimeout, 
                                                                     msgRxEnable_On, 
                                                                     msgRxEnable_Off)
if ( status != ftdf.DTS_BLE_FUNC_STATUS_OK):
    logstr = ( 'SCRIPT: ERROR: Expected status ', ftdf.DTS_BLE_FUNC_STATUS_OK, ' instead received ', 
               status )
    raise StopScript( ''.join( map( str, logstr ) ) )


DTS_BLEStop( devId1 )

# Expect OK
res, ret = DTS_getMsg( devId1, responseTimeout)
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_BLE_OK, 
               ' confirm, instead received ', ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

# Expect DTS_BLE_EVT_CODE_GAP_ADV_COMPLETED on devId1
res, ret = DTS_getMsg( devId1, responseTimeout)
if ( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_EVT:
    logstr = ( 'SCRIPT: ERROR: Expected msgId ', ftdf.DTS_MSG_ID_BLE_EVT, ' instead received ', 
               ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )
elif ret['evt_code'] != ftdf.DTS_BLE_EVT_CODE_GAP_ADV_COMPLETED:
    logstr = ( 'SCRIPT: ERROR: Expected evt_code ', ftdf.DTS_BLE_EVT_CODE_GAP_ADV_COMPLETED, 
               ' instead received ', ret['evt_code'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

DTS_CoexStatsReq(devId1)

# Expect arbiter stats
res, ret = DTS_getMsg( devId1, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_COEX_STATS:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_COEX_STATS, 
               ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )
 
if ret['txrxMonOverflow'] != 0:
    logstr = ( 'SCRIPT: ERROR: Expected 0 txrxMonOverflow, instead received ', 
               ret['txrxMonOverflow'] )
    raise StopScript( ''.join( map( str, logstr ) ) )  

if ret['txrxMonTxMasked1'] != 0:
    logstr = ( 'SCRIPT: ERROR: Expected 0 txrxMonTxMasked1, instead received ', 
               ret['txrxMonTxMasked1'] )
    raise StopScript( ''.join( map( str, logstr ) ) )   

if ret['txrxMonRxMasked1'] != 0:
    logstr = ( 'SCRIPT: ERROR: Expected 0 txrxMonRxMasked1, instead received ', 
               ret['txrxMonRxMasked1'] )
    raise StopScript( ''.join( map( str, logstr ) ) )   

if ret['txrxMonTxPassed1'] == 0:
    logstr = ( 'SCRIPT: ERROR: Expected non-zero txrxMonTxPassed1, instead received ', 
               ret['txrxMonRxPassed1'] )
    raise StopScript( ''.join( map( str, logstr ) ) )  

if ret['txrxMonRxPassed1'] == 0:
    logstr = ( 'SCRIPT: ERROR: Expected non-zero txrxMonRxPassed1, instead received ', 
               ret['txrxMonRxPassed1'] )
    raise StopScript( ''.join( map( str, logstr ) ) )  

if ret['txrxMonTxMasked2'] == 0:
    logstr = ( 'SCRIPT: ERROR: Expected non-zero txrxMonTxMasked2, instead received ', 
               ret['txrxMonTxMasked2'] )
    raise StopScript( ''.join( map( str, logstr ) ) )


if ret['txrxMonRxMasked2'] == 0:
    logstr = ( 'SCRIPT: ERROR: Expected non-zero txrxMonRxMasked2, instead received ', 
               ret['txrxMonRxMasked2'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

