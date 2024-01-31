## Arbiter v1 behavior (PTI set 0, MAC vs MAC tests).
## FTDF Tx vs EXT behavior
## Script tests how FTDF Tx is affected when enabling EXT when:
## A) EXT has priority over FTDF 
## B) FTDF has priority over EXT
##
## Steps
## ---------
## - 1< Set arbiter configuration EXT priority over FTDF
## - 2< Enable Rx
## - 1< Enable EXT
## - 1< Send/Verify 4 frames
## - 2< Verify no frames received
## - 1< Disable EXT
## - 2< Disable Rx
## - 1< Set arbiter configuration FTDF priority over EXT
## - 2< Enable Rx
## - 1< Enable EXT
## - 1< Send/Verify 4 frames
## - 2< Verify at least 1 frame received
## - 1< Disable EXT
## - 2< Disable Rx

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

# =================================================================================================#

# Set arbiter configuration EXT priority over FTDF
DTS_ArbiterSetConfig(devId1, 0, 0, 0,
                     ftdf.DTS_COEX_MAC_TYPE_EXT, 0,
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

# =================================================================================================#
# Set arbiter configuration FTDF priority over EXT
DTS_ArbiterSetConfig(devId1, 0, 0, 0,
                     ftdf.DTS_COEX_MAC_TYPE_FTDF, 0,
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
