## Test BLE non-connectable and connectable advertising on one node. 
## This script may be used to observe BLE PTI diagnostics.  

import sys    #cli arguments
import time    #sleep

from scriptIncludes import *

peripheral = devId1

DTS_BLEReset(peripheral)
# Expect OK
res, ret = DTS_getMsg( peripheral, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_BLE_OK, 
               ' confirm, instead received ', ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

# Start peripheral in non-connectable mode
DTS_BLEAdvertise( peripheral, ftdf.DTS_BLE_GAP_CONN_MODE_NON_CONN, 1100, 1100 )
# Expect OK
res, ret = DTS_getMsg( peripheral, responseTimeout)
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_BLE_OK, 
               ' confirm, instead received ', ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

#time.sleep(2)

DTS_BLEStop( peripheral )

# Expect OK
res, ret = DTS_getMsg( peripheral, responseTimeout)
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_BLE_OK, 
               ' confirm, instead received ', ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

# Expect DTS_BLE_EVT_CODE_GAP_ADV_COMPLETED on peripheral
res, ret = DTS_getMsg( peripheral, responseTimeout)
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



# Start peripheral
DTS_BLEAdvertise( peripheral, ftdf.DTS_BLE_GAP_CONN_MODE_UNDIRECTED, 1100, 1100 )
# Expect OK
res, ret = DTS_getMsg( peripheral, responseTimeout)
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_BLE_OK, 
               ' confirm, instead received ', ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

time.sleep(2)

DTS_BLEStop( peripheral )

# Expect OK
res, ret = DTS_getMsg( peripheral, responseTimeout)
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_BLE_OK, 
               ' confirm, instead received ', ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

# Expect DTS_BLE_EVT_CODE_GAP_ADV_COMPLETED on peripheral
res, ret = DTS_getMsg( peripheral, responseTimeout)
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
