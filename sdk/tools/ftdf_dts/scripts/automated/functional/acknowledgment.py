import sys  #cli arguments
import time  #sleep

from scriptIncludes import *

msgSET_DSN = {
    'msgId': ftdf.FTDF_SET_REQUEST,
    'PIBAttribute': ftdf.FTDF_PIB_DSN,
    'PIBAttributeValue': 16
}
msgRxOnWhenIdle_ena = {'msgId': ftdf.FTDF_SET_REQUEST,
                       'PIBAttribute': ftdf.FTDF_PIB_RX_ON_WHEN_IDLE,
                       'PIBAttributeValue': True}

# Message order
msgFlow = ( devId1, msgRESET, ftdf.FTDF_RESET_CONFIRM,
      devId2, msgRESET, ftdf.FTDF_RESET_CONFIRM,

      ##################################
      # Set short address and PAN ID
      ##################################
      devId1, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
      devId2, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,

      devId1, msgSET_Dev1_ShortAddress, ftdf.FTDF_SET_CONFIRM,
      devId2, msgSET_Dev2_ShortAddress, ftdf.FTDF_SET_CONFIRM,

      devId1, msgSET_DSN, ftdf.FTDF_SET_CONFIRM,
      devId2, msgRxOnWhenIdle_ena, ftdf.FTDF_SET_CONFIRM )

idx = 0

while( idx < len( msgFlow ) ):
  # Send message
  DTS_sndMsg( msgFlow[idx], msgFlow[idx+1] )

  # Get message confirm
  res, ret = DTS_getMsg( msgFlow[idx],responseTimeout )

  # Check received expected confirm
  if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
  elif ret['msgId'] != msgFlow[idx+2]:
    logstr = ( 'SCRIPT: ERROR: Expected ', msgFlow[idx+2], ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )

  idx += 3


##################################
# Set transparent mode with no options
##################################
DTS_enableTransparantMode( devId2, True, 0 )


##################################
# Send acknowledged frame
##################################
msdu = [0xa, 0xb, 0xc, 0xd, 0xe]
msgDATA = {
  'msgId': ftdf.FTDF_DATA_REQUEST,
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
  'keySource': [],
  'keyIndex': 0,
  'frameControlOptions': 0,
  'headerIEList': 0,
  'payloadIEList': 0,
  'sendMultiPurpose': False }

DTS_sndMsg(devId1, msgDATA)

res, ret = DTS_getMsg( devId1, responseTimeout )
if res == False or ret['msgId'] != ftdf.FTDF_DATA_CONFIRM or ret['status'] != ftdf.FTDF_NO_ACK:
    raise StopScript("Expected FTDF_DATA_CONFIRM(NO_ACK)")

##################################
# Receive 4 identical transparent frames
##################################
exp_frame = [97, 136, 16, 1, 0, 32, 0, 16, 0, 10, 11, 12, 13, 14, 81, 1]
for i in range( 4 ):
    res, ret = DTS_getMsg( devId2, 1 )

    if res == False or ret['msgId'] != ftdf.FTDF_TRANSPARENT_INDICATION:
        raise StopScript("Expected 4x transparent frame")
    elif ret['status'] != 0 or ret['frameLength'] != 16 or ret['frame'] != exp_frame:
        raise StopScript("Unexpected transparent frame received" )

res, ret = DTS_getMsg( devId2, 1 )

if res == True:
    raise StopScript("Expected exactly 4 transparent frames" )
