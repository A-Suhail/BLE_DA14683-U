#TODO: energie list chack for value's whem bugs are fixxed

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
      
msgSCAN_short = { 'msgId':        ftdf.FTDF_SCAN_REQUEST,
                  'scanType':     ftdf.FTDF_ACTIVE_SCAN,
                  'scanChannels': 0x7fff800,
                  'channelPage':  0,
                  'scanDuration': 1,
                  'securityLevel': 0,
                  'keyIdMode': 0,
                  'keySource': keySource,
                  'keyIndex': 0}
                  
msgSCAN_long = { 'msgId':        ftdf.FTDF_SCAN_REQUEST,
                 'scanType':     ftdf.FTDF_ACTIVE_SCAN,
                 'scanChannels': 0x7fff800,
                 'channelPage':  0,
                 'scanDuration': 6,
                 'securityLevel': 0,
                 'keyIdMode': 0,
                 'keySource': keySource,
                 'keyIndex': 0,}      

set_autore_msg =  { 'msgId': ftdf.FTDF_SET_REQUEST, 
                    'PIBAttribute': ftdf.FTDF_PIB_AUTO_REQUEST, 
                    'PIBAttributeValue': 1 }        

unset_autore_msg =  { 'msgId': ftdf.FTDF_SET_REQUEST, 
                    'PIBAttribute': ftdf.FTDF_PIB_AUTO_REQUEST, 
                    'PIBAttributeValue': 0 }    

counter_msg       = { 'msgId': ftdf.FTDF_GET_REQUEST,
                          'PIBAttribute': ftdf.FTDF_PIB_TRAFFIC_COUNTERS }                    

# Message order
msgFlow = ( devId1, msgRESET, ftdf.FTDF_RESET_CONFIRM,
            devId2, msgRESET, ftdf.FTDF_RESET_CONFIRM,
      
            devId1, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
      
            devId1, msgSET_Dev1_ShortAddress, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_Dev2_ShortAddress, ftdf.FTDF_SET_CONFIRM )

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
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_SUCCESS confirm, instead received ', resultStr[ ret['status']  ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1

######################################################
## test no beacons received, macAutoRequest = FALSE ##
###################################################### 
DTS_sndMsg( devId1, msgSCAN_short )
res, ret = DTS_getMsg( devId1,responseTimeout )
if( res == False ):
  raise StopScript( 'SCRIPT: ERROR: No response received from device' )
  error += 1
elif ret['msgId'] != ftdf.FTDF_SCAN_CONFIRM:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_SCAN_CONFIRM, instead received ', msgNameStr[ ret['msgId'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
elif ret['status'] != ftdf.FTDF_SUCCESS:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_SUCCESS confirm, instead received ', resultStr[ ret['status']  ])
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

DTS_sndMsg( devId1, msgSCAN_long )

count = 10
    
while( 1 ):
  count += 1
  res, ret = DTS_getMsg( devId1,responseTimeout+20 )
  if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    error += 1
  elif ret['msgId'] == ftdf.FTDF_BEACON_NOTIFY_INDICATION:
    rx_beacon += 1
    #print( 'SCRIPT: ERROR: Expected FTDF_BEACON_NOTIFY_INDICATION, instead received ', msgNameStr[ ret['msgId'] -1 ])
    if ret['PANDescriptor'][0]['channelNumber'] != count:
      logstr = ( 'SCRIPT: ERROR: Expected channelNumber = ',count,', instead received ', ret['PANDescriptor'][0]['channelNumber'])
      raise StopScript( ''.join( map( str, logstr ) ) )
      error += 1
  elif ret['msgId'] == ftdf.FTDF_SCAN_CONFIRM:
    #print( 'SCRIPT: ERROR: Expected FTDF_SCAN_CONFIRM, instead received ', msgNameStr[ ret['msgId'] -1 ])
    if ret['status'] == ftdf.FTDF_SUCCESS:
      break
    else:
      logstr = ( 'SCRIPT: ERROR: Expected FTDF_SUCCESS confirm, instead received ', resultStr[ ret['status']  ])
      raise StopScript( ''.join( map( str, logstr ) ) )
      error += 1
      break     

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
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_SUCCESS confirm, instead received ', resultStr[ ret['status'] ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
  
#####################################################
## test no beacons received, macAutoRequest = TRUE ##
#####################################################
## disable rx remote device so we dont get anny beacons back 
DTS_sndMsg( devId2, msgRxEnable_Off )
res, ret = DTS_getMsg( devId2,responseTimeout )
if( res == False ):
  raise StopScript( 'SCRIPT: ERROR: No response received from device' )
  error += 1
elif ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_RX_ENABLE_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
  
rx_beacon += 16  

DTS_sndMsg( devId1, msgSCAN_short )
res, ret = DTS_getMsg( devId1,responseTimeout )
if( res == False ):
  raise StopScript( 'SCRIPT: ERROR: No response received from device' )
  error += 1
elif ret['msgId'] != ftdf.FTDF_SCAN_CONFIRM:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_SCAN_CONFIRM, instead received ', msgNameStr[ ret['msgId'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
elif ret['status'] != ftdf.FTDF_NO_BEACON:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_NO_BEACON confirm, instead received ', resultStr[ ret['status'] ])
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

DTS_sndMsg( devId1, msgSCAN_long )

 
##res end of scan
res, ret = DTS_getMsg( devId1,responseTimeout + 20 )
if( res == False ):
  raise StopScript( 'SCRIPT: ERROR: No response received from device' )
  error += 1
elif ret['msgId'] != ftdf.FTDF_SCAN_CONFIRM:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_SCAN_CONFIRM, instead received ', msgNameStr[ ret['msgId'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
elif ret['status'] != ftdf.FTDF_SUCCESS:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_SUCCESS confirm, instead received ', resultStr[ ret['status']  ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
elif ret['PANDescriptorList'][0]['channelNumber'] != 11:
  logstr = ( 'SCRIPT: ERROR: Expected channelNumber = 11, instead received ', ret['PANDescriptorList'][0]['channelNumber'])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1

###################  
## Counter check ##
###################
rcvdBeacons = 2

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
elif ret['PIBAttributeValue']['rxBeaconFrmOkCnt'] != rcvdBeacons:
  logstr = ( 'SCRIPT: ERROR: Expected rxBeaconFrmOkCnt = ', rcvdBeacons, ' instead received ', ret['PIBAttributeValue']['rxBeaconFrmOkCnt'])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
elif ret['PIBAttributeValue']['txCmdFrmCnt'] != 64:
  logstr = ( 'SCRIPT: ERROR: Expected txCmdFrmCnt = 64, instead received ', ret['PIBAttributeValue']['txCmdFrmCnt'])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1  

##########################################
## END OF TEST, let examine the results ##
##########################################   
if error != 0:
  logstr = ('SCRIPT: test FAILED with ' , error , ' ERRORS')
  raise StopScript( ''.join( map( str, logstr ) ) )
