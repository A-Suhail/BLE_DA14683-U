## Test BLE passive and active on one node. 
## This script may be used to observe BLE PTI diagnostics.

import sys    #cli arguments
import time    #sleep

from scriptIncludes import *

central = devId2

DTS_BLEReset(central)
# Expect OK
res, ret = DTS_getMsg( central, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_BLE_OK, 
               ' confirm, instead received ', ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

# Start central in non-connectable mode
DTS_BLEScan( central, ftdf.DTS_BLE_GAP_SCAN_PASSIVE, 160, 80 )
# Expect OK
res, ret = DTS_getMsg( central, responseTimeout)
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_BLE_OK, 
               ' confirm, instead received ', ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

time.sleep(2)

DTS_BLEStop( central )

# Get 0 or more reports
while 1:
    res, ret = DTS_getMsg( central, responseTimeout)
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
res, ret = DTS_getMsg( central, responseTimeout)
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

# Start central
DTS_BLEScan( central, ftdf.DTS_BLE_GAP_SCAN_ACTIVE, 160, 80 )
# Expect OK
res, ret = DTS_getMsg( central, responseTimeout)
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_BLE_OK, 
               ' confirm, instead received ', ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

time.sleep(2)

DTS_BLEStop( central )

# Get 0 or more reports
while 1:
    res, ret = DTS_getMsg( central, responseTimeout)
    if ( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    elif ((ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK) and (ret['msgId'] != ftdf.DTS_MSG_ID_BLE_EVT)):
        logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_BLE_OK, 'or', ftdf.DTS_MSG_ID_BLE_EVT,
                   ', instead received ', ret['msgId'] )
        raise StopScript( ''.join( map( str, logstr ) ) )
    
    if ret['msgId'] == ftdf.DTS_MSG_ID_BLE_OK:
        break;
    else:
        continue;

# Expect Scan complete 
res, ret = DTS_getMsg( central, responseTimeout)
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

