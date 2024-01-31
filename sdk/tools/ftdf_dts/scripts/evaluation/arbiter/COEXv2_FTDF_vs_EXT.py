## Arbiter v2 behavior (Auto PTI, MAC-PTI pair vs MAC-PTI pair).
## FTDF vs EXT behavior
## Script tests how FTDF Tx RX is affected when enabling EXT when:
## A) EXT has priority over FTDF 
## B) FTDF has priority over EXT
## Test case is the same as the v1 version, with the difference that auto PTI is used and
## specific PTI is tested each time. It also tests BA arbiter statistics.
## 
## Steps
## ---------
##
## - 1,2< Set FTDF TX PTI=1, RX PTI=2
## - 1< Set Arbiter configuration 0=EXT, 1=(FTDF, 1)
## - 2< Set Arbiter configuration 0=EXT, 1=(FTDF, 2)
## - 2< Enable Rx
## - 1< Enable EXT
## - 1< Send/Verify 4 frames
## - 2< Verify no frames received
## - 1< Disable EXT
## - 2< Disable Rx
## - 1< Verify txrxMonOverflow == 0
## - 1< Verify txrxMonTxMasked2 == 16 (4 transmissions * 4 retransmissions each)
## - 1< Verify txrxMonTxPassed2 == 0
## - 1< Set Arbiter configuration 0=(FTDF, 1), 1=EXT 
## - 2< Set Arbiter configuration 0=EXT, 1=(FTDF, 2)
## - 2< Enable Rx
## - 1< Enable EXT
## - 1< Send/Verify 4 frames
## - 2< Verify at least 1 frame received
## - 1< Disable EXT
## - 2< Disable Rx
## - 1< Verify txrxMonOverflow == 0
## - 1< Verify txrxMonTxMasked1 == 0
## - 1< Verify txrxMonTxPassed1 >= 4
## - 1< Set Arbiter configuration 0=EXT, 1=(FTDF, 1)
## - 2< Set Arbiter configuration 0=EXT, 1=(FTDF, 2)
## - 2< Enable Rx
## - 1< Enable EXT
## - 1< Send/Verify 4 frames
## - 2< Verify no frames received
## - 1< Disable EXT
## - 2< Disable Rx
## - 2< Verify txrxMonOverflow == 0
## - 2< Verify txrxMonTxMasked1 == 1
## - 2< Verify txrxMonTxPassed1 == 0
## - 1< Set Arbiter configuration 0=EXT, 1=(FTDF, 1)
## - 2< Set Arbiter configuration 0=(FTDF, 2), 1=EXT 
## - 2< Enable Rx
## - 1< Enable EXT
## - 1< Send/Verify 4 frames
## - 2< Verify at least 1 frame received
## - 1< Disable EXT
## - 2< Disable Rx
## - 2< Verify txrxMonOverflow == 0
## - 2< Verify txrxMonTxMasked1 == 0
## - 2< Verify txrxMonTxPassed1 >= 5

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

# time.sleep(5)

# Data frame
msdu = []
for i in range( 100 ):
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
            devId2, msgSET_PtiConfig, ftdf.FTDF_SET_CONFIRM,
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


DTS_sndMsg(devId1,msgDbgModeSetRequest);

# =================================================================================================#
# Reset arbiter
DTS_ArbiterReset(devId1)
DTS_ArbiterReset(devId2)

# =================================================================================================#
# =================================================================================================#

# On Tx side, Set arbiter configuration EXT priority over FTDF on Tx
DTS_ArbiterSetConfig(devId1, 0x07f0, 0, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_EXT, 0,
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

# On Rx side specify Rx PTI
DTS_ArbiterSetConfig(devId2, 0x07f0, 0, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_EXT, 0,
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

# Turn Rx on on devId2
DTS_sndMsg(devId2, msgRxEnable_On)

# Expect confirm
res, ret = DTS_getMsg( devId2, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.FTDF_RX_ENABLE_CONFIRM, 
               ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )

# Turn on external on devId1
DTS_ArbiterSetExtStatus(devId1, 1)

# Send data from devId1 (4 packets)
for i in range(4):
    # Data packet
    DTS_sndMsg(devId1, msgDATA)
    # Expect confirm
    res, ret = DTS_getMsg( devId1, responseTimeout )
    if( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    elif ret['msgId'] != ftdf.FTDF_DATA_CONFIRM:
        logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.FTDF_DATA_CONFIRM, 
                   ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
        raise StopScript( ''.join( map( str, logstr ) ) )

# Expect no message on devId2
res, ret = DTS_getMsg( devId2, responseTimeout )
if( res == True ):
    logstr = ( 'SCRIPT: ERROR: Expected no message, instead received msgId', 
               msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )

# Turn off external on peripheral
DTS_ArbiterSetExtStatus(devId1, 0)

# Turn Rx off on devId2
DTS_sndMsg(devId2, msgRxEnable_Off)

# Expect confirm
res, ret = DTS_getMsg( devId2, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.FTDF_RX_ENABLE_CONFIRM, 
               ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
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

# Masked will be 4 * 4 = 16 since there are NACK retries. 
if ret['txrxMonTxMasked2'] != 16:
    logstr = ( 'SCRIPT: ERROR: Expected 16 txrxMonTxMasked2, instead received ', 
               ret['txrxMonTxMasked2'] )
    raise StopScript( ''.join( map( str, logstr ) ) )   

if ret['txrxMonTxPassed2'] != 0:
    logstr = ( 'SCRIPT: ERROR: Expected 16 txrxMonTxPassed2, instead received ', 
               ret['txrxMonTxMasked2'] )
    raise StopScript( ''.join( map( str, logstr ) ) )  

# =================================================================================================#
# Reset arbiter
DTS_ArbiterReset(devId1)
DTS_ArbiterReset(devId2)

# =================================================================================================#
# Set arbiter configuration FTDF priority over EXT
DTS_ArbiterSetConfig(devId1, 0x07f0, 0, 0, 
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
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0 )

# On Rx side specify Rx PTI
DTS_ArbiterSetConfig(devId2, 0x07f0, 0, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_EXT, 0,
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

# Turn Rx on on devId2
DTS_sndMsg(devId2, msgRxEnable_On)

# Expect confirm
res, ret = DTS_getMsg( devId2, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.FTDF_RX_ENABLE_CONFIRM, 
               ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )

# Turn on external on devId1
DTS_ArbiterSetExtStatus(devId1, 1)

# Send data from devId1 (4 packets)
for i in range(4):
    # Data packet
    DTS_sndMsg(devId1, msgDATA)
    # Expect confirm
    res, ret = DTS_getMsg( devId1, responseTimeout )
    if( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    elif ret['msgId'] != ftdf.FTDF_DATA_CONFIRM:
        logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.FTDF_DATA_CONFIRM, 
                   ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
        raise StopScript( ''.join( map( str, logstr ) ) )

# Expect at least one message
count = 0
while(1):
    res, ret = DTS_getMsg( devId2, responseTimeout )
    if( res == False ):
        break
    elif ret['msgId'] != ftdf.FTDF_DATA_INDICATION:
        logstr = ( 'SCRIPT: ERROR: Expected FTDF_DATA_INDICATION confirm, instead received ', 
                   ret['msgId'] )
        raise StopScript( ''.join( map( str, logstr ) ) )
        break
    count = count + 1

if (count == 0):
    logstr = ( 'SCRIPT: ERROR: Expected at least one received packet, instead received none')
    raise StopScript( ''.join( map( str, logstr ) ) )

# Turn off external on peripheral
DTS_ArbiterSetExtStatus(devId1, 0)

# Turn Rx off on devId2
DTS_sndMsg(devId2, msgRxEnable_Off)

# Expect confirm
res, ret = DTS_getMsg( devId2, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.FTDF_RX_ENABLE_CONFIRM, 
               ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
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

# Masked will be 0. 
if ret['txrxMonTxMasked1'] != 0:
    logstr = ( 'SCRIPT: ERROR: Expected 0 txrxMonTxMasked1, instead received ', 
               ret['txrxMonTxMasked1'] )
    raise StopScript( ''.join( map( str, logstr ) ) )   

if ret['txrxMonTxPassed1'] < 4:
    logstr = ( 'SCRIPT: ERROR: Expected at least 4 txrxMonTxPassed1, instead received ', 
               ret['txrxMonTxPassed1'] )
    raise StopScript( ''.join( map( str, logstr ) ) )  

# =================================================================================================#
# Reset arbiter
DTS_ArbiterReset(devId1)
DTS_ArbiterReset(devId2)

# =================================================================================================#
# Test Rx
# =================================================================================================#

# On Tx side specify Tx PTI
DTS_ArbiterSetConfig(devId1, 0x07f0, 0, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_EXT, 0,
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

# ON Rx Set arbiter configuration EXT priority below FTDF
DTS_ArbiterSetConfig(devId2, 0x07f0, 0, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_EXT, 0,
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
 
# Turn Rx on on devId2
DTS_sndMsg(devId2, msgRxEnable_On)
 
# Expect confirm
res, ret = DTS_getMsg( devId2, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.FTDF_RX_ENABLE_CONFIRM, 
               ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )
 
# Turn on external on devId2
DTS_ArbiterSetExtStatus(devId2, 1)
 
# Send data from devId1 (4 packets)
for i in range(4):
    # Data packet
    DTS_sndMsg(devId1, msgDATA)
    # Expect confirm
    res, ret = DTS_getMsg( devId1, responseTimeout )
    if( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    elif ret['msgId'] != ftdf.FTDF_DATA_CONFIRM:
        logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.FTDF_DATA_CONFIRM, 
                   ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
        raise StopScript( ''.join( map( str, logstr ) ) )
 
# Expect no message on devId2
res, ret = DTS_getMsg( devId2, responseTimeout )
if( res == True ):
    logstr = ( 'SCRIPT: ERROR: Expected no message, instead received msgId', 
               msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )
 
# Turn off external on peripheral
DTS_ArbiterSetExtStatus(devId2, 0)
 
# Turn Rx off on devId2
DTS_sndMsg(devId2, msgRxEnable_Off)
 
# Expect confirm
res, ret = DTS_getMsg( devId2, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.FTDF_RX_ENABLE_CONFIRM, 
               ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )
 
DTS_CoexStatsReq(devId2)

# Expect arbiter stats
res, ret = DTS_getMsg( devId2, responseTimeout )
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

if ret['txrxMonRxMasked2'] != 1:
    logstr = ( 'SCRIPT: ERROR: Expected 1 txrxMonRxMasked2, instead received ', 
               ret['txrxMonTxMasked2'] )
    raise StopScript( ''.join( map( str, logstr ) ) )   

if ret['txrxMonRxPassed2'] != 0:
    logstr = ( 'SCRIPT: ERROR: Expected 0 txrxMonRxPassed2, instead received ', 
               ret['txrxMonTxMasked2'] )
    raise StopScript( ''.join( map( str, logstr ) ) )  

# =================================================================================================#
# Reset arbiter
DTS_ArbiterReset(devId1)
DTS_ArbiterReset(devId2)

# =================================================================================================#
# Set arbiter configuration FTDF priority over EXT

# On Tx side specify Tx PTI
DTS_ArbiterSetConfig(devId1, 0x07f0, 0, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_EXT, 0,
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

# ON Rx Set arbiter configuration EXT priority below FTDF
DTS_ArbiterSetConfig(devId2, 0x07f0, 0, 0, 
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
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0 )
 
# Turn Rx on on devId2
DTS_sndMsg(devId2, msgRxEnable_On)
 
# Turn on external on devId2
DTS_ArbiterSetExtStatus(devId2, 1) 

# Expect confirm
res, ret = DTS_getMsg( devId2, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.FTDF_RX_ENABLE_CONFIRM, 
               ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )
 
# Send data from devId1 (4 packets)
for i in range(4):
    # Data packet
    DTS_sndMsg(devId1, msgDATA)
    # Expect confirm
    res, ret = DTS_getMsg( devId1, responseTimeout )
    if( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    elif ret['msgId'] != ftdf.FTDF_DATA_CONFIRM:
        logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.FTDF_DATA_CONFIRM, 
                   ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
        raise StopScript( ''.join( map( str, logstr ) ) )
 
# Expect at least one message
count = 0
while(1):
    res, ret = DTS_getMsg( devId2, responseTimeout )
    if( res == False ):
        break
    elif ret['msgId'] != ftdf.FTDF_DATA_INDICATION:
        logstr = ( 'SCRIPT: ERROR: Expected FTDF_DATA_INDICATION confirm, instead received ', 
                   ret['msgId'] )
        raise StopScript( ''.join( map( str, logstr ) ) )
        break
    count = count + 1
 
if (count == 0):
    logstr = ( 'SCRIPT: ERROR: Expected at least one received packet, instead received none')
    raise StopScript( ''.join( map( str, logstr ) ) )

# Turn Rx off on devId2
DTS_sndMsg(devId2, msgRxEnable_Off)

# Turn off external on peripheral
DTS_ArbiterSetExtStatus(devId1, 0)
 
# Expect confirm
res, ret = DTS_getMsg( devId2, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.FTDF_RX_ENABLE_CONFIRM, 
               ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )

DTS_CoexStatsReq(devId2)

# Expect arbiter stats
res, ret = DTS_getMsg( devId2, responseTimeout )
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

# Masked will be 4 * 4 = 16 since there are NACK retries. 
if ret['txrxMonRxMasked1'] != 0:
    logstr = ( 'SCRIPT: ERROR: Expected 0 txrxMonRxMasked1, instead received ', 
               ret['txrxMonTxMasked1'] )
    raise StopScript( ''.join( map( str, logstr ) ) )   

if ret['txrxMonRxPassed1'] < 5:
    logstr = ( 'SCRIPT: ERROR: Expected at least 5 txrxMonRxPassed1, instead received ', 
               ret['txrxMonRxPassed1'] )
    raise StopScript( ''.join( map( str, logstr ) ) )  

# =================================================================================================#
# Reset arbiter
DTS_ArbiterReset(devId1)
DTS_ArbiterReset(devId2)



