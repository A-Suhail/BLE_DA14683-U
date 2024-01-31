import sys  #cli arguments
import time  #sleep

from scriptIncludes import *

DTS_getReleaseInfo(devId1)
DTS_getReleaseInfo(devId2)
res, ret = DTS_getMsg( devId1,responseTimeout )
res, ret = DTS_getMsg( devId2,responseTimeout )

# Data frame
msdu = [0x1, 0x2, 0x3, 0x4, 0x5]
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
      
msgDATA_inval = { 'msgId': ftdf.FTDF_DATA_REQUEST,
      'srcAddrMode': ftdf.FTDF_SHORT_ADDRESS,
      'dstAddrMode': ftdf.FTDF_SHORT_ADDRESS,
      'dstPANId': 0x0002,
      'dstAddr': 0x0025,
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
      
set_promiscuous_msg = { 'msgId': ftdf.FTDF_SET_REQUEST, 
                        'PIBAttribute': ftdf.FTDF_PIB_PROMISCUOUS_MODE, 
                        'PIBAttributeValue': 1 }      
      
# Message order
msgFlow = ( devId1, msgRESET, ftdf.FTDF_RESET_CONFIRM,
            devId2, msgRESET, ftdf.FTDF_RESET_CONFIRM,
      
            devId1, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
            
            devId2, set_promiscuous_msg, ftdf.FTDF_SET_CONFIRM,
      
            devId1, msgSET_Dev1_ShortAddress, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_Dev2_ShortAddress, ftdf.FTDF_SET_CONFIRM )

idx = 0
res = True
error = 0

####################################
## Send message while air is busy ##
####################################

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

#######################################################################

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

# Send message
DTS_sndMsg( devId1, msgDATA )

# Get message confirm
res, ret = DTS_getMsg( devId1,responseTimeout )
if( res == False ):
  raise StopScript( 'SCRIPT: ERROR: No response received from device' )
  error += 1
elif ret['msgId'] != ftdf.FTDF_DATA_CONFIRM:
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_DATA_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
else:
  if ret['status'] != ftdf.FTDF_SUCCESS: 
    logstr = ( 'SCRIPT: ERROR: Expected FTDF_SUCCESS , instead received ', resultStr[ ret['status'] ] ) 
    raise StopScript( ''.join( map( str, logstr ) ) )
    error += 1
   
  res2, ret2 = DTS_getMsg( devId2, responseTimeout )

  if( res2 == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    error += 1
  elif ret2['msgId'] != ftdf.FTDF_DATA_INDICATION:
    logstr = ( 'SCRIPT: ERROR: Expected FTDF_DATA_INDICATION confirm, instead received ', ret2['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )
    error += 1  
##########################################
## END OF TEST, let examine the results ##
##########################################   
if error != 0:
  logstr = ('SCRIPT: test FAILED with ' , error , ' ERRORS')
  raise StopScript( ''.join( map( str, logstr ) ) )
