import sys  #cli arguments
import time  #sleep

from scriptIncludes import *

keySource = [0,0,0,0,0,0,0,0]

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

msgSCAN_short = { 'msgId':        ftdf.FTDF_SCAN_REQUEST,
                  'scanType':     ftdf.FTDF_PASSIVE_SCAN,
                  'scanChannels': 0x7fff800,
                  'channelPage':  0,
                  'scanDuration': 1,
                  'securityLevel': 0,
                  'keyIdMode': 0,
                  'keySource': keySource,
                  'keyIndex': 0}

msgSCAN_long = { 'msgId':        ftdf.FTDF_SCAN_REQUEST,
                 'scanType':     ftdf.FTDF_PASSIVE_SCAN,
                 'scanChannels': 0x7fff800,
                 'channelPage':  0,
                 'scanDuration': 6,
                 'securityLevel': 0,
                 'keyIdMode': 0,
                 'keySource': keySource,
                 'keyIndex': 0}

set_autore_msg =  { 'msgId': ftdf.FTDF_SET_REQUEST,
                    'PIBAttribute': ftdf.FTDF_PIB_AUTO_REQUEST,
                    'PIBAttributeValue': 1 }

unset_autore_msg =  { 'msgId': ftdf.FTDF_SET_REQUEST,
                    'PIBAttribute': ftdf.FTDF_PIB_AUTO_REQUEST,
                    'PIBAttributeValue': 0 }

msgFlow = ( devId1, msgRESET, ftdf.FTDF_RESET_CONFIRM,
            devId2, msgRESET, ftdf.FTDF_RESET_CONFIRM,

            ###############################
            # 1+2> Set short address and PAN ID
            ###############################
            devId1, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,

            devId1, msgSET_Dev1_ShortAddress, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_Dev2_ShortAddress, ftdf.FTDF_SET_CONFIRM )

idx = 0
res = True
error = 0

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


###############################
# 1> Set macAutoRequest = false
###############################
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


###############################
# 1> Send passive scan request with channelPage = 0, scanChannels = 0x7fff800 and scanDuration = 1
###############################
DTS_sndMsg( devId1, msgSCAN_short )

###############################
# 1< Receive successful scan confirm with no PAN descriptors
###############################
res, ret = DTS_getMsg( devId1,responseTimeout )
if( res == False ):
  raise StopScript( 'SCRIPT: ERROR: No response received from device' )
  error += 1
elif ret['msgId'] != ftdf.FTDF_SCAN_CONFIRM:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_SCAN_CONFIRM, instead received ', msgNameStr[ ret['msgId'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
elif ret['status'] != ftdf.FTDF_SUCCESS:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_SUCCESS confirm, instead received ', resultStr[ ret['status'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
elif ret['resultListSize'] != 0:
    raise StopScript( 'Expected no PAN descriptors' )


###############################
# 1> Send passive scan request with channelPage = 0, scanChannels = 0x7fff800 and scanDuration = 6
###############################
DTS_sndMsg( devId1, msgSCAN_short )

###############################
# 2> Send beacon
###############################
DTS_sndMsg( devId2, msgBR )

###############################
# 2< Receive beacon confirm
###############################
res2, ret2 = DTS_getMsg( devId2,responseTimeout )
if( res2 == False ):
  raise StopScript( 'SCRIPT: ERROR: No response received from device1' )
  error += 1
elif ret2['msgId'] != ftdf.FTDF_BEACON_CONFIRM:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_BEACON_CONFIRM confirm, instead received ', msgNameStr[ ret2['msgId'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
elif ret2['status'] != ftdf.FTDF_SUCCESS:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_SUCCESS confirm, instead received ', resultStr[ ret2['status'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1

###############################
# 1< Receive beacon notify indication
###############################
res, ret = DTS_getMsg( devId1,responseTimeout )
if( res == False ):
  raise StopScript( 'SCRIPT: ERROR: No response received from device2' )
  error += 1
elif ret['msgId'] != ftdf.FTDF_BEACON_NOTIFY_INDICATION:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_BEACON_NOTIFY_INDICATION, instead received ', msgNameStr[ ret['msgId'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
elif ret['PANDescriptor'][0]['channelNumber'] != 11:
  logstr = ( 'SCRIPT: ERROR: Expected channelNumber = 11, instead received ', ret['PANDescriptor'][0]['channelNumber'])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1

###############################
# 1< Receive successful scan confirm with no PAN descriptors
###############################
res, ret = DTS_getMsg( devId1,responseTimeout )
if( res == False ):
  raise StopScript( 'SCRIPT: ERROR: No response received from device' )
  error += 1
elif ret['msgId'] != ftdf.FTDF_SCAN_CONFIRM:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_SCAN_CONFIRM, instead received ', msgNameStr[ ret['msgId'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
elif ret['status'] != ftdf.FTDF_SUCCESS:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_SUCCESS confirm, instead received ', resultStr[ ret['status'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
elif ret['resultListSize'] != 0:
    raise StopScript( 'Expected no PAN descriptors' )



###############################
# 1> Set macAutoRequest = true
###############################
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



###############################
# 1> Send passive scan request with channelPage = 0, scanChannels = 0x7fff800 and scanDuration = 1
###############################
DTS_sndMsg( devId1, msgSCAN_short )

###############################
# 1< Receive NO_BEACON scan confirm with no PAN descriptors
###############################
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


###############################
# 1> Send passive scan request with channelPage = 0, scanChannels = 0x7fff800 and scanDuration = 6
###############################
DTS_sndMsg( devId1, msgSCAN_long )

###############################
# 2> Send beacon
###############################
DTS_sndMsg( devId2, msgBR )

###############################
# 2< Receive beacon confirm
###############################
res2, ret2 = DTS_getMsg( devId2,responseTimeout )
if( res2 == False ):
  raise StopScript( 'SCRIPT: ERROR: No response received from device' )
  error += 1
elif ret2['msgId'] != ftdf.FTDF_BEACON_CONFIRM:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_BEACON_CONFIRM confirm, instead received ', msgNameStr[ ret2['msgId'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
elif ret2['status'] != ftdf.FTDF_SUCCESS:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_SUCCESS confirm, instead received ', resultStr[ ret2['status'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1

###############################
# 1< Receive successful scan confirm with 1 PAN descriptor matching the beacon
###############################
res, ret = DTS_getMsg( devId1,responseTimeout+20 )
if( res == False ):
  raise StopScript( 'SCRIPT: ERROR: No response received from device' )
  error += 1
elif ret['msgId'] != ftdf.FTDF_SCAN_CONFIRM:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_SCAN_CONFIRM, instead received ', msgNameStr[ ret['msgId'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
elif ret['status'] != ftdf.FTDF_SUCCESS:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_SUCCESS confirm, instead received ', resultStr[ ret['status'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
elif ret['resultListSize'] != 1:
    raise StopScript( 'Expected 1 PAN descriptor' )
