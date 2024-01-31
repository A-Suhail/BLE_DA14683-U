## Arbiter v2 behavior (Auto PTI, MAC-PTI pair vs MAC-PTI pair).
## BLE vs EXT behavior
## Script tests how BLE connections are affected when enabling EXT when:
## A) EXT has priority over BLE 
## B) BLE has priority over EXT
## Test case is the same as the v1 version, with the difference that auto PTI is used and
## thus all PTIs must be programmed in the arbiter.  
## 
## Steps
## ---------
## - 1< Set arbiter configuration 0=EXT, then BLE with PTIs 0 - 7
## - 1,2< Open BLE connection (DUT 1 peripheral, DUT 2 central)
## - 1,2< Verify BLE connection
## - 1< Enable EXT
## - 1,2,< Verify BLE connection drop
## - 1< Disable EXT
## - 1< Set arbiter configuration 0-7= BLE PTI 0-7, then 8=EXT
## - 1,2< Open BLE connection (DUT 1 peripheral, DUT 2 central)
## - 1,2< Verify BLE connection
## - 1< Enable EXT
## - 1,2< Verify BLE connection 
## - 1< Disable EXT
## - 1,2< Close BLE connection
## - 1< Set arbiter configuration EXT first priority, then BLE with PTIs 0 - 7
## - 1< Enable EXT
## - 1,2< Open BLE connection (DUT 1 peripheral, DUT 2 central)
## - 1,2< Verify connection failure
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
# =================================================================================================#
# Reset arbiter
DTS_ArbiterReset(devId1)
DTS_ArbiterReset(devId2)
  
# Set arbiter configuration EXT priority over BLE
DTS_ArbiterSetConfig(devId1, 0x07f0, 0, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_EXT, 0,
                     ftdf.DTS_COEX_MAC_TYPE_BLE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_BLE, 1, 
                     ftdf.DTS_COEX_MAC_TYPE_BLE, 2,
                     ftdf.DTS_COEX_MAC_TYPE_BLE, 3, 
                     ftdf.DTS_COEX_MAC_TYPE_BLE, 4,
                     ftdf.DTS_COEX_MAC_TYPE_BLE, 5, 
                     ftdf.DTS_COEX_MAC_TYPE_BLE, 6,
                     ftdf.DTS_COEX_MAC_TYPE_BLE, 7, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0 )
 
# Setup connection
status, reason = DTS_BLEConnectionOpen( devId1, devId2, responseTimeout, 0x28, 0x38, 0, 0x2a)
 
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
 
# Turn on external on peripheral
DTS_ArbiterSetExtStatus(devId1, 1)

# Expect GAP disconnect on both devices.
res, ret = DTS_getMsg( devId1, responseTimeout)
if ( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_EVT:
    logstr = ( 'SCRIPT: ERROR: Expected msgId ', ftdf.DTS_MSG_ID_BLE_EVT, ' instead received ', 
               ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )
elif ret['evt_code'] != ftdf.DTS_BLE_EVT_CODE_GAP_DISCONNECTED:
    logstr = ( 'SCRIPT: ERROR: Expected evt_code ', ftdf.DTS_BLE_EVT_CODE_GAP_DISCONNECTED, 
               ' instead received ', ret['evt_code'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

res, ret = DTS_getMsg( devId2, responseTimeout)
if ( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_EVT:
    logstr = ( 'SCRIPT: ERROR: Expected msgId ', ftdf.DTS_MSG_ID_BLE_EVT, ' instead received ', 
               ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )
elif ret['evt_code'] != ftdf.DTS_BLE_EVT_CODE_GAP_DISCONNECTED:
    logstr = ( 'SCRIPT: ERROR: Expected evt_code ', ftdf.DTS_BLE_EVT_CODE_GAP_DISCONNECTED, 
               ' instead received ', ret['evt_code'] )
    raise StopScript( ''.join( map( str, logstr ) ) )
 
# Turn off external on peripheral
DTS_ArbiterSetExtStatus(devId1, 0)

# =================================================================================================#
# Set arbiter configuration BLE priority over EXT
DTS_ArbiterSetConfig(devId1, 0x07f0, 0, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_BLE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_BLE, 1, 
                     ftdf.DTS_COEX_MAC_TYPE_BLE, 2,
                     ftdf.DTS_COEX_MAC_TYPE_BLE, 3, 
                     ftdf.DTS_COEX_MAC_TYPE_BLE, 4,
                     ftdf.DTS_COEX_MAC_TYPE_BLE, 5, 
                     ftdf.DTS_COEX_MAC_TYPE_BLE, 6,
                     ftdf.DTS_COEX_MAC_TYPE_BLE, 7, 
                     ftdf.DTS_COEX_MAC_TYPE_EXT, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0 )

# Turn on external on peripheral
DTS_ArbiterSetExtStatus(devId1, 1)
# Setup connection
status, reason = DTS_BLEConnectionOpen( devId1, devId2, responseTimeout, 0x28, 0x38, 0, 0x2a)

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


# Expect nothing on both devices
res, ret = DTS_getMsg( devId1, 3)
if ( res == True ):
    logstr = ( 'SCRIPT: ERROR: No message expected instead received msgId ', ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )
  
res, ret = DTS_getMsg( devId2, 3)
if ( res == True ):
    logstr = ( 'SCRIPT: ERROR: No message expected instead received msgId ', ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

# Disconnect
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

# Turn off external on peripheral
DTS_ArbiterSetExtStatus(devId1, 0)
#==================================================================================================#
# Set arbiter configuration EXT priority over BLE
DTS_ArbiterSetConfig(devId1, 0x07f0, 0, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_EXT, 0,
                     ftdf.DTS_COEX_MAC_TYPE_BLE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_BLE, 1, 
                     ftdf.DTS_COEX_MAC_TYPE_BLE, 2,
                     ftdf.DTS_COEX_MAC_TYPE_BLE, 3, 
                     ftdf.DTS_COEX_MAC_TYPE_BLE, 4,
                     ftdf.DTS_COEX_MAC_TYPE_BLE, 5, 
                     ftdf.DTS_COEX_MAC_TYPE_BLE, 6,
                     ftdf.DTS_COEX_MAC_TYPE_BLE, 7, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0 )
 
# Turn on external on peripheral
DTS_ArbiterSetExtStatus(devId1, 1)
 
# Expect connection failure
status, reason = DTS_BLEConnectionOpen( devId1, devId2, responseTimeout, 0x28, 0x38, 0, 0x2a)
 
if (status != ftdf.DTS_BLE_FUNC_STATUS_NO_RSP):
    logstr = ( 'SCRIPT: ERROR: Expected connection fail with status ', 
               ftdf.DTS_BLE_FUNC_STATUS_NO_RSP, ' instead received status ', status)
    raise StopScript( ''.join( map( str, logstr ) ) )
elif (reason['expected'] != ftdf.DTS_MSG_ID_BLE_EVT):
    logstr = ( 'SCRIPT: ERROR: Expected connection fail with expected msgId ', 
               ftdf.DTS_MSG_ID_BLE_EVT, ' instead expected msgId is ', reason['expected'])
    raise StopScript( ''.join( map( str, logstr ) ) )
 
# Stop both devices
DTS_BLEStop(devId1)
# Expect DTS_MSG_ID_BLE_OK
res, ret = DTS_getMsg( devId1, responseTimeout)
if ( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
    logstr = ( 'SCRIPT: ERROR: Expected msgId ', ftdf.DTS_MSG_ID_BLE_OK, ' instead received ', 
               ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

# Expect DTS_BLE_EVT_CODE_GAP_ADV_COMPLETED on peripheral
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

DTS_BLEStop(devId2)
 # Expect DTS_MSG_ID_BLE_OK
res, ret = DTS_getMsg( devId2, responseTimeout)
if ( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
    logstr = ( 'SCRIPT: ERROR: Expected msgId ', ftdf.DTS_MSG_ID_BLE_OK, ' instead received ', 
               ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

# Turn off external on peripheral
DTS_ArbiterSetExtStatus(devId1, 0)

# Reset arbiter
DTS_ArbiterReset(devId1)
DTS_ArbiterReset(devId2)

