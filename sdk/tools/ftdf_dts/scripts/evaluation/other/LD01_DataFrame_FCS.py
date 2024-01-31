# Load-drop 1 Test: Send data frame

# Test manually:
# Test data frame is received using srcAddrMode and dstAddrMode set to FTDF_EXTENDED_ADDRESS
# Test data frame is droppend when using incorrect dstPANId
# Test data frame is droppend when using incorrect dstAddr

import sys  #cli arguments
import time  #sleep

from scriptIncludes import *

DTS_getReleaseInfo(devId1)
DTS_getReleaseInfo(devId2)

res, ret = DTS_getMsg( devId1, responseTimeout )
res, ret = DTS_getMsg( devId2, responseTimeout )

msgchannel = { 'msgId': ftdf.FTDF_SET_REQUEST,
                       'PIBAttribute': ftdf.FTDF_PIB_CHANNEL_PAGE,
                       'PIBAttributeValue': 2 }

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
      'ackTX': True,
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

# Message order
msgFlow = ( devId1, msgRESET, ftdf.FTDF_RESET_CONFIRM,
      devId2, msgRESET, ftdf.FTDF_RESET_CONFIRM,
      
      devId1, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
      devId2, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
      
      devId1, msgSET_Dev1_ShortAddress, ftdf.FTDF_SET_CONFIRM,
      devId2, msgSET_Dev2_ShortAddress, ftdf.FTDF_SET_CONFIRM,
      
      devId2, msgchannel, ftdf.FTDF_SET_CONFIRM,
      
      devId2, msgRxEnable_On, ftdf.FTDF_RX_ENABLE_CONFIRM,
      
      devId1, msgDATA, ftdf.FTDF_DATA_CONFIRM )

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
    if( ret['msgId'] == ftdf.FTDF_DATA_CONFIRM ):
      if( ret['status'] != ftdf.FTDF_SUCCESS ):
        break

      # Check data frame received correctly
      res2, ret2 = DTS_getMsg( devId2, responseTimeout )
      if( res == False ):
        raise StopScript( 'SCRIPT: FAILED' )
        break
  idx += 3
