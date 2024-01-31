import sys  #cli arguments
import time  #sleep

from scriptIncludes import *

DTS_getReleaseInfo(devId1)
DTS_getReleaseInfo(devId2)
#time.sleep( responseTimeout )
res, ret = DTS_getMsg( devId1,responseTimeout )
res, ret = DTS_getMsg( devId2,responseTimeout )

# Data frame
msdu = [0x1, 0x2, 0x3, 0x4, 0x5]
keySource = [0x0, 0x0, 0x0, 0x0,
       0x0, 0x0, 0x0, 0x0]

      
msgBR  = { 'msgId': ftdf.FTDF_BEACON_REQUEST,
           'beaconType': ftdf.FTDF_NORMAL_BEACON,
           'channel': 11,
           'channelPage': 0,
           'superframeOrder': 0,
           'beaconSecurityLevel': 0,
           'beaconKeyIdMode': 0,
           'beaconKeySource': keySource,
           'beaconKeyIndex': 0,
           'dstAddrMode': ftdf.FTDF_SHORT_ADDRESS,
           'dstAddr': 0xFFFF,
           'BSNSuppression': 0, }
      
set_autore_msg =  { 'msgId': ftdf.FTDF_SET_REQUEST, 
                    'PIBAttribute': ftdf.FTDF_PIB_AUTO_REQUEST, 
                    'PIBAttributeValue': 1 }  

unset_autore_msg =  { 'msgId': ftdf.FTDF_SET_REQUEST, 
                    'PIBAttribute': ftdf.FTDF_PIB_AUTO_REQUEST, 
                    'PIBAttributeValue': 0 }                      

# Message order
msgFlow = ( devId1, msgRESET, ftdf.FTDF_RESET_CONFIRM,
            devId2, msgRESET, ftdf.FTDF_RESET_CONFIRM,
      
            devId1, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
      
            devId1, msgSET_Dev1_ShortAddress, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_Dev2_ShortAddress, ftdf.FTDF_SET_CONFIRM )
           
counter_msg       = { 'msgId': ftdf.FTDF_GET_REQUEST,
                          'PIBAttribute': ftdf.FTDF_PIB_TRAFFIC_COUNTERS }                 

idx = 0
res = True
error = 0
rx_beacon = 0

while( idx < len( msgFlow ) ):
  # Send message
  DTS_sndMsg( msgFlow[idx], msgFlow[idx+1] )

  # Get message confirm
  res, ret = DTS_getMsg( msgFlow[idx],responseTimeout )

  # Check received expected confirm
  if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    error += 1
  elif ret['msgId'] != msgFlow[idx+2]:
    logstr = ( 'SCRIPT: ERROR: Expected ', msgFlow[idx+2], ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )
    error += 1
    
  idx += 3
  
###########################
## Disable macAutoRequest ##
###########################
DTS_sndMsg( devId1, unset_autore_msg )
res, ret = DTS_getMsg( devId1,responseTimeout )
if( res == False ):
  raise StopScript( 'SCRIPT: ERROR: No response received from device' )
  error += 1
elif ret['msgId'] != ftdf.FTDF_SET_CONFIRM:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_SET_CONFIRM, instead received ', msgNameStr[ ret['msgId'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
elif ret['status'] != ftdf.FTDF_SUCCESS:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_SUCCESS confirm, instead received ', resultStr[ ret['status'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
DTS_sndMsg( devId2, unset_autore_msg )
res, ret = DTS_getMsg( devId2,responseTimeout )
if( res == False ):
  raise StopScript( 'SCRIPT: ERROR: No response received from device' )
  error += 1
elif ret['msgId'] != ftdf.FTDF_SET_CONFIRM:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_SET_CONFIRM, instead received ', msgNameStr[ ret['msgId'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
elif ret['status'] != ftdf.FTDF_SUCCESS:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_SUCCESS confirm, instead received ', resultStr[ ret['status'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1  


###################################################
## test beacons received, macAutoRequest = FALSE ##
################################################### 
#Enable receiver
DTS_sndMsg( devId2, msgRxEnable_On )
res, ret = DTS_getMsg( devId2,responseTimeout )
if( res == False ):
  raise StopScript( 'SCRIPT: ERROR: No response received from device' )
  error += 1
elif ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_RX_ENABLE_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
DTS_sndMsg( devId1, msgRxEnable_On )
res, ret = DTS_getMsg( devId1,responseTimeout )
if( res == False ):
  raise StopScript( 'SCRIPT: ERROR: No response received from device' )
  error += 1
elif ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_RX_ENABLE_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1  

## send beacon
DTS_sndMsg( devId1, msgBR )
res, ret = DTS_getMsg( devId1,responseTimeout )
if( res == False ):
  raise StopScript( 'SCRIPT: ERROR: No response received from device' )
  error += 1
elif ret['msgId'] != ftdf.FTDF_BEACON_CONFIRM:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_BEACON_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
elif ret['status'] != ftdf.FTDF_SUCCESS:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_SUCCESS confirm, instead received ', resultStr[ ret['status']  ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
else:
  rx_beacon += 1

##res 2 beacon
res, ret = DTS_getMsg( devId2,responseTimeout )
if( res == False ):
  raise StopScript( 'SCRIPT: ERROR: No response received from device' )
  error += 1
elif ret['msgId'] != ftdf.FTDF_BEACON_NOTIFY_INDICATION:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_BEACON_NOTIFY_INDICATION, instead received ', msgNameStr[ ret['msgId'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
else:
  DTS_sndMsg( devId2, msgBR )
  res, ret = DTS_getMsg( devId2,responseTimeout )
  if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    error += 1
  elif ret['msgId'] != ftdf.FTDF_BEACON_CONFIRM:
    logstr = ( 'SCRIPT: ERROR: Expected FTDF_BEACON_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )
    error += 1
  elif ret['status'] != ftdf.FTDF_SUCCESS:
    logstr = ( 'SCRIPT: ERROR: Expected FTDF_SUCCESS confirm, instead received ', resultStr[ ret['status']  ])
    raise StopScript( ''.join( map( str, logstr ) ) )
    error += 1
  
res, ret = DTS_getMsg( devId1,responseTimeout )
if( res == False ):
  raise StopScript( 'SCRIPT: ERROR: No response received from device' )
  error += 1
elif ret['msgId'] != ftdf.FTDF_BEACON_NOTIFY_INDICATION:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_BEACON_NOTIFY_INDICATION, instead received ', msgNameStr[ ret['msgId'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1

###########################
## Enable macAutoRequest ##
###########################
DTS_sndMsg( devId1, set_autore_msg )
res, ret = DTS_getMsg( devId1,responseTimeout )
if( res == False ):
  raise StopScript( 'SCRIPT: ERROR: No response received from device' )
  error += 1
elif ret['msgId'] != ftdf.FTDF_SET_CONFIRM:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_SET_CONFIRM, instead received ', msgNameStr[ ret['msgId'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
elif ret['status'] != ftdf.FTDF_SUCCESS:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_SUCCESS confirm, instead received ', resultStr[ ret['status'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
DTS_sndMsg( devId2, set_autore_msg )
res, ret = DTS_getMsg( devId2,responseTimeout )
if( res == False ):
  raise StopScript( 'SCRIPT: ERROR: No response received from device' )
  error += 1
elif ret['msgId'] != ftdf.FTDF_SET_CONFIRM:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_SET_CONFIRM, instead received ', msgNameStr[ ret['msgId'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
elif ret['status'] != ftdf.FTDF_SUCCESS:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_SUCCESS confirm, instead received ', resultStr[ ret['status'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1  
  
##################################################
## test beacons received, macAutoRequest = TRUE ##
################################################## 
#Enable receiver
DTS_sndMsg( devId2, msgRxEnable_On )
res, ret = DTS_getMsg( devId2,responseTimeout )
if( res == False ):
  raise StopScript( 'SCRIPT: ERROR: No response received from device' )
  error += 1
elif ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_RX_ENABLE_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
DTS_sndMsg( devId1, msgRxEnable_On )
res, ret = DTS_getMsg( devId1,responseTimeout )
if( res == False ):
  raise StopScript( 'SCRIPT: ERROR: No response received from device' )
  error += 1
elif ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_RX_ENABLE_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1  

## send beacon
DTS_sndMsg( devId1, msgBR )
res, ret = DTS_getMsg( devId1,responseTimeout )
if( res == False ):
  raise StopScript( 'SCRIPT: ERROR: No response received from device' )
  error += 1
elif ret['msgId'] != ftdf.FTDF_BEACON_CONFIRM:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_BEACON_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
elif ret['status'] != ftdf.FTDF_SUCCESS:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_SUCCESS confirm, instead received ', resultStr[ ret['status'] ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1

 
res, ret = DTS_getMsg( devId2,responseTimeout )
if ( res == True ):
  error += 1
  raise StopScript( 'SCRIPT: ERROR: Unexpected response received from device' )


  
###################  
## Counter check ##
###################
DTS_sndMsg( devId1, counter_msg )
res, ret = DTS_getMsg( devId1,responseTimeout )
if( res == False ):
  raise StopScript( 'SCRIPT: ERROR: No response received from device' )
  error += 1
elif ret['msgId'] != ftdf.FTDF_GET_CONFIRM:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_GET_CONFIRM, instead received ', msgNameStr[ ret['msgId'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
elif ret['status'] != ftdf.FTDF_SUCCESS:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_SUCCESS confirm, instead received ', resultStr[ ret['status']  ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
elif ret['PIBAttributeValue']['rxBeaconFrmOkCnt'] != rx_beacon:
  logstr = ( 'SCRIPT: ERROR: Expected rxBeaconFrmOkCnt = ',rx_beacon,', instead received ', ret['PIBAttributeValue']['rxBeaconFrmOkCnt'])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
elif ret['PIBAttributeValue']['txCmdFrmCnt'] != 0:
  logstr = ( 'SCRIPT: ERROR: Expected txCmdFrmCnt = 0, instead received ', ret['PIBAttributeValue']['txCmdFrmCnt'])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1    

##########################################
## END OF TEST, let examine the results ##
##########################################   
if error != 0:
  logstr = ('SCRIPT: test FAILED with ' , error , ' ERRORS')
  raise StopScript( ''.join( map( str, logstr ) ) )
