import sys
from scriptIncludes import *

msgSET_rxOnWhenIdle = { 'msgId': ftdf.FTDF_SET_REQUEST,
                        'PIBAttribute': ftdf.FTDF_PIB_RX_ON_WHEN_IDLE,
                        'PIBAttributeValue': True }

msgASSOC_RESP = {
    'msgId': ftdf.FTDF_ASSOCIATE_RESPONSE,
    'deviceAddress': 0x0020,
    'assocShortAddress': 0x1234,
    'status': ftdf.FTDF_FAST_ASSOCIATION_SUCCESSFUL,
    'fastA': True,
    'securityLevel':0,
    'keyIdMode': 0,
    'keySource': [0,0,0,0,0,0,0,0],
    'keyIndex': 0,
    'channelOffset': 0,
    'hoppingSequenceLength': 0
}

msdu = [0xde, 0xad, 0xbe, 0xef, 0x00, 0x00, 0x00, 0x00, 0x10, 0x20]
msgDATA = {
    'msgId': ftdf.FTDF_DATA_REQUEST,
    'srcAddrMode': ftdf.FTDF_EXTENDED_ADDRESS,
    'dstAddrMode': ftdf.FTDF_EXTENDED_ADDRESS,
    'dstPANId': 0x0001,
    'dstAddr': 0x0000000000000020,
    'msduLength': len( msdu ),
    'msdu': msdu,
    'msduHandle': 1,
    'ackTX': False,
    'GTSTX': False,
    'indirectTX': False,
    'securityLevel': 0,
    'keyIdMode': 0,
    'keySource': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
    'keyIndex': 0,
    'frameControlOptions': 0,
    'headerIEList': 0,
    'payloadIEList': 0,
    'sendMultiPurpose': False
}

# Message order
msgFlow = ( devId1, msgRESET, ftdf.FTDF_RESET_CONFIRM,
            devId2, msgRESET, ftdf.FTDF_RESET_CONFIRM,

            devId1, msgSET_Dev1_ShortAddress, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_Dev2_ShortAddress, ftdf.FTDF_SET_CONFIRM,

            devId1, msgSET_Dev1_ExtendedAddress, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_Dev2_ExtendedAddress, ftdf.FTDF_SET_CONFIRM,

            devId1, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,

            devId2, msgSET_rxOnWhenIdle, ftdf.FTDF_SET_CONFIRM )

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


############################
# Send unexpected associate response
############################
DTS_sndMsg( devId1, msgASSOC_RESP )

res, ret = DTS_getMsg( devId2, responseTimeout )
if res:
    raise StopScript( 'Expected no message' )

res, ret = DTS_getMsg( devId1, responseTimeout )
if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgId'] != ftdf.FTDF_COMM_STATUS_INDICATION:
    raise StopScript( 'Wrong response from device' )

############################
# Send data frame
############################
DTS_sndMsg( devId1, msgDATA )

res, ret = DTS_getMsg( devId2, responseTimeout )
if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgId'] != ftdf.FTDF_DATA_INDICATION:
    raise StopScript( 'Expected data indication' )

res, ret = DTS_getMsg( devId1, responseTimeout )
if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgId'] != ftdf.FTDF_DATA_CONFIRM:
    raise StopScript( 'Expected data confirm' )
