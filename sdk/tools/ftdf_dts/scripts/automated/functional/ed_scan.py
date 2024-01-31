import sys  #cli arguments
import time  #sleep

from scriptIncludes import *

keySource = [0,0,0,0,0,0,0,0]

msgSCAN_inval_channelPage = { 'msgId':        ftdf.FTDF_SCAN_REQUEST,
                              'scanType':     ftdf.FTDF_ED_SCAN,
                              'scanChannels': 0x3ff800,
                              'channelPage':  10,
                              'scanDuration': 0,
                              'securityLevel': 0,
                              'keyIdMode': 0,
                              'keySource': keySource,
                              'keyIndex': 0}

msgSCAN_inval_scanChannels1 = { 'msgId':        ftdf.FTDF_SCAN_REQUEST,
                                'scanType':     ftdf.FTDF_ED_SCAN,
                                'scanChannels': 0x2,
                                'channelPage':  0,
                                'scanDuration': 0,
                                'securityLevel': 0,
                                'keyIdMode': 0,
                                'keySource': keySource,
                                'keyIndex': 0}

msgSCAN_short = { 'msgId':        ftdf.FTDF_SCAN_REQUEST,
                  'scanType':     ftdf.FTDF_ED_SCAN,
                  'scanChannels': 0x7fff800,
                  'channelPage':  0,
                  'scanDuration': 1,
                  'securityLevel': 0,
                  'keyIdMode': 0,
                  'keySource': keySource,
                  'keyIndex': 0}

msgSCAN_long = { 'msgId':        ftdf.FTDF_SCAN_REQUEST,
                 'scanType':     ftdf.FTDF_ED_SCAN,
                 'scanChannels': 0x7fff800,
                 'channelPage':  0,
                 'scanDuration': 5,
                 'securityLevel': 0,
                 'keyIdMode': 0,
                 'keySource': keySource,
                 'keyIndex': 0}

# Message order
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
    break
  elif ret['msgId'] != msgFlow[idx+2]:
    logstr = ( 'SCRIPT: ERROR: Expected ', msgFlow[idx+2], ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )
    break

  idx += 3



###############################
# 1> Send ED scan request with channelPage = 10
###############################
DTS_sndMsg( devId1, msgSCAN_inval_channelPage )

###############################
# 1< Receive INVALID_PARAMETER scan confirm
###############################
res, ret = DTS_getMsg( devId1,responseTimeout )
if( res == False ):
  raise StopScript( 'SCRIPT: ERROR: No response received from device' )
  error += 1
elif ret['msgId'] != ftdf.FTDF_SCAN_CONFIRM:
  logstr = ( 'SCRIPT: ERROR: Expected ', msgFlow[idx+2], ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
elif ret['status'] != ftdf.FTDF_INVALID_PARAMETER:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_INVALID_PARAMETER , instead received ', resultStr[ ret['status'] ] )
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1


###############################
# 1> Send ED scan request with channelPage = 0 and scanChannels = 0x2
###############################
DTS_sndMsg( devId1, msgSCAN_inval_scanChannels1 )

###############################
# 1< Receive INVALID_PARAMETER scan confirm
###############################
res, ret = DTS_getMsg( devId1,responseTimeout )
if( res == False ):
  raise StopScript( 'SCRIPT: ERROR: No response received from device' )
  error += 1
elif ret['msgId'] != ftdf.FTDF_SCAN_CONFIRM:
  logstr = ( 'SCRIPT: ERROR: Expected ', msgFlow[idx+2], ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
elif ret['status'] != ftdf.FTDF_INVALID_PARAMETER:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_INVALID_PARAMETER , instead received ', resultStr[ ret['status'] ] )
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1


###############################
# 1> Send ED scan request with channelPage = 0, scanChannels = 0x7fff800 and scanDuration = 1
###############################
DTS_setRegister(devId1,0x50002F80, 2, 30)
DTS_setRegister(devId2,0x50002F80, 2, 30)
DTS_sndMsg( devId1, msgSCAN_short )

###############################
# 1< Receive successful scan confirm with a list of energy levels
###############################
res, ret = DTS_getMsg( devId1,responseTimeout )
if( res == False ):
  raise StopScript( 'SCRIPT: ERROR: No response received from device' )
  error += 1
elif ret['msgId'] != ftdf.FTDF_SCAN_CONFIRM:
  logstr = ( 'SCRIPT: ERROR: Expected ', msgFlow[idx+2], ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
elif ret['status'] != ftdf.FTDF_SUCCESS:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_SUCCESS , instead received ', resultStr[ ret['status'] ] )
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
elif ret['resultListSize'] != 16:
    raise StopScript( 'Expected 16 energy detect levels' )


###############################
# 1> Send ED scan request with channelPage = 0, scanChannels = 0x7fff800 and scanDuration = 5
###############################
DTS_sndMsg( devId1, msgSCAN_long )

###############################
# 1< Receive successful scan confirm with a list of energy levels
###############################
res, ret = DTS_getMsg( devId1, 60 )
if( res == False ):
  raise StopScript( 'SCRIPT: ERROR: No response received from device' )
  error += 1
elif ret['msgId'] != ftdf.FTDF_SCAN_CONFIRM:
  logstr = ( 'SCRIPT: ERROR: Expected ', msgFlow[idx+2], ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
elif ret['status'] != ftdf.FTDF_SUCCESS:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_SUCCESS , instead received ', resultStr[ ret['status'] ] )
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
elif ret['resultListSize'] != 16:
    raise StopScript( 'Expected 16 energy detect levels' )
