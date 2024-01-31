## Arbiter v1 behavior (PTI set 0, MAC vs MAC tests).
## BLE priority set over FTDF
## Script tests the increasing loss caused on FTDF traffic by increasing BLE duty cycle. 
##  
## Steps
## ---------
## - 1< Set arbiter configuration BLE priority over FTDF
## - 1,2< Perform FTDF PER test (DUT 1 Tx, DUT 2 Rx)
## - rxPktBLECycleZero = FTDFPERTest[RxPkt]
## - 1,2< Open BLE connection with low duty cycle (DUT 1 peripheral, DUT 2 central)
## - 1,2< Verify BLE connection
## - 1,2< Perform FTDF PER test (DUT 1 Tx, DUT 2 Rx)
## - rxPktBLECycleLo = FTDFPERTest[RxPkt]
## - 1,2< Verify BLE connection
## - 1,2< Close BLE connection (verify no connection drop)
## - 1,2< Open BLE connection with high duty cycle (DUT 1 peripheral, DUT 2 central)
## - 1,2< Verify BLE connection
## - 1,2< Perform FTDF PER test (DUT 1 Tx, DUT 2 Rx)
## - rxPktBLECycleHi = FTDFPERTest[RxPkt]
## - 1,2< Verify BLE connection
## - 1,2< Close BLE connection
## - Verify rxPktBLECycleZero > rxPktBLECycleLo
## - Verify rxPktBLECycleLo > rxPktBLECycleHi
##


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

# Set arbiter configuration BLE priority over FTDF
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
# Now make the same test with more frequent BLE traffic
#########################################################

status, reason = DTS_BLEConnectionOpen( devId1, devId2, 200, 80, 112, 0, 84)
  
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

status, reason, txPkt, rxPktBLECycleLo, duration =  DTS_FTDFPERTest(devId1, devId2, msgDATA, 
                                                                    nrOfFrames, 0, 
                                                                    responseTimeout, msgRxEnable_On, 
                                                                    msgRxEnable_Off)
if ( status != ftdf.DTS_BLE_FUNC_STATUS_OK):
    logstr = ( 'SCRIPT: ERROR: Expected status ', ftdf.DTS_BLE_FUNC_STATUS_OK, ' instead received ', 
               status )
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


#######################################################
# Now make the same test with more frequent BLE traffic
#########################################################

status, reason = DTS_BLEConnectionOpen( devId1, devId2, 100, 40, 56, 0, 42)
# status, reason = DTS_BLEConnect( devId1, devId2, 50, 20, 28, 0, 21)
  
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

status, reason, txPkt, rxPktBLECycleHi, duration =  DTS_FTDFPERTest(devId1, devId2, msgDATA, 
                                                                    nrOfFrames, 0, responseTimeout, 
                                                                    msgRxEnable_On, msgRxEnable_Off)
if ( status != ftdf.DTS_BLE_FUNC_STATUS_OK):
    logstr = ( 'SCRIPT: ERROR: Expected status ', ftdf.DTS_BLE_FUNC_STATUS_OK, ' instead received ', 
               status )
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

if (rxPktBLECycleZero <= rxPktBLECycleLo):
    logstr = ( 'SCRIPT: ERROR: FTDF received packets with zero BLE duty cycle ', rxPktBLECycleZero, 
               ' are expected to be more than packets received on low BLE cycle ', 
               rxPktBLECycleLo)
    raise StopScript( ''.join( map( str, logstr ) ) )

if (rxPktBLECycleLo <= rxPktBLECycleHi):
    logstr = ( 'SCRIPT: ERROR: FTDF received packets on low BLE duty cycle ', rxPktBLECycleLo, 
               ' are expected to be more than packets received on high BLE cycle ', 
               rxPktBLECycleHi)
    raise StopScript( ''.join( map( str, logstr ) ) )

# All OK
# =================================================================================================#


