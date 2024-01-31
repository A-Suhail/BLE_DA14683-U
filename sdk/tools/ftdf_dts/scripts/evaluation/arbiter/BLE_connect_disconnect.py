## Test BLE connection setup and tear down between a central and a peripheral node.
## A dummy GATT service is established and reads and wirtes to a dummy attribute are also tested.
## This script may be used to observe BLE PTI diagnostics.

import sys    #cli arguments
import time    #sleep

from scriptIncludes import *

# Reset arbiter
DTS_ArbiterReset(devId1)
DTS_ArbiterReset(devId2)

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

time.sleep(2);

DTS_BLERead(devId2)

# Expect OK
res, ret = DTS_getMsg( devId2, responseTimeout)
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_BLE_OK, 
               ' confirm, instead received ', ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

# Expect read complete 
res, ret = DTS_getMsg( devId2, responseTimeout)
if ( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_EVT:
    logstr = ( 'SCRIPT: ERROR: Expected msgId ', ftdf.DTS_MSG_ID_BLE_EVT, ' instead received ', 
               ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )
elif ret['evt_code'] != ftdf.DTS_BLE_EVT_CODE_GATTC_READ_COMPLETED:
    logstr = ( 'SCRIPT: ERROR: Expected evt_code ', ftdf.DTS_BLE_EVT_CODE_GATTC_READ_COMPLETED, 
               ' instead received ', ret['evt_code'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

# Write a different value
new_value = ret['value'] + 3


DTS_BLEWrite(devId2, new_value)
# Expect OK
res, ret = DTS_getMsg( devId2, responseTimeout)
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_BLE_OK, 
               ' confirm, instead received ', ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

# Expect write complete 
res, ret = DTS_getMsg( devId2, responseTimeout)
if ( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_EVT:
    logstr = ( 'SCRIPT: ERROR: Expected msgId ', ftdf.DTS_MSG_ID_BLE_EVT, ' instead received ', 
               ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )
elif ret['evt_code'] != ftdf.DTS_BLE_EVT_CODE_GATTC_WRITE_COMPLETED:
    logstr = ( 'SCRIPT: ERROR: Expected evt_code ', ftdf.DTS_BLE_EVT_CODE_GATTC_WRITE_COMPLETED, 
               ' instead received ', ret['evt_code'] )
    raise StopScript( ''.join( map( str, logstr ) ) )


# Expect write request on periheral
res, ret = DTS_getMsg( devId1, responseTimeout)
if ( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_EVT:
    logstr = ( 'SCRIPT: ERROR: Expected msgId ', ftdf.DTS_MSG_ID_BLE_EVT, ' instead received ', 
               ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )
elif ret['evt_code'] != ftdf.DTS_BLE_EVT_CODE_GATTS_WRITE_REQ:
    logstr = ( 'SCRIPT: ERROR: Expected evt_code ', ftdf.DTS_BLE_EVT_CODE_GATTS_WRITE_REQ, 
               ' instead received ', ret['evt_code'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

# Read again
DTS_BLERead(devId2)
# Expect OK
res, ret = DTS_getMsg( devId2, responseTimeout)
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_BLE_OK, 
               ' confirm, instead received ', ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

# Expect read complete 
res, ret = DTS_getMsg( devId2, responseTimeout)
if ( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_EVT:
    logstr = ( 'SCRIPT: ERROR: Expected msgId ', ftdf.DTS_MSG_ID_BLE_EVT, ' instead received ', 
               ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )
elif ret['evt_code'] != ftdf.DTS_BLE_EVT_CODE_GATTC_READ_COMPLETED:
    logstr = ( 'SCRIPT: ERROR: Expected evt_code ', ftdf.DTS_BLE_EVT_CODE_GATTC_READ_COMPLETED, 
               ' instead received ', ret['evt_code'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

if ( new_value != ret['value']):
    raise StopScript ( 'SCRIPT: ERROR: Written value does not equal read value.')


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
