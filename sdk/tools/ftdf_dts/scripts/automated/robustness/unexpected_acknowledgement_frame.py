import sys
from scriptIncludes import *

msgSET_rxOnWhenIdle = { 'msgId': ftdf.FTDF_SET_REQUEST,
                        'PIBAttribute': ftdf.FTDF_PIB_RX_ON_WHEN_IDLE,
                        'PIBAttributeValue': True }

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
    'ackTX': True,
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

            devId1, msgSET_rxOnWhenIdle, ftdf.FTDF_SET_CONFIRM,
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
# Enable transparent mode with FCS_GENERATION
############################
DTS_enableTransparantMode( devId2, True, ftdf.FTDF_TRANSPARENT_ENABLE_FCS_GENERATION | ftdf.FTDF_TRANSPARENT_AUTO_ACK )

############################
# Send 256 transparent acknowledgement frames with increasing SN
############################
for i in range( 256 ):
    frameType    = 0x0002 # acknowledge
    frameVersion = 0x2000 # 2011

    frameControl = frameType | frameVersion

    byte0 = frameControl & 0x00ff
    byte1 = frameControl >> 8

    ackFrame = [
        byte0,
        byte1,
        i,     # SN
        0x00,  # FCS
        0x00   # FCS
    ]

    DTS_sendFrameTransparant( devId2, len( ackFrame ), ackFrame, 11, True, 0 )

    res, ret = DTS_getMsg( devId2, responseTimeout )

    if res == False:
        raise StopScript( 'No response from device' )
    elif ret['msgId'] != ftdf.FTDF_TRANSPARENT_CONFIRM:
        raise StopScript( 'Expected transparent confirm' )


# Check that no message was received
res, ret = DTS_getMsg( devId1, 1 )
if res:
    raise StopScript( 'Expected no msg with unexpected ack frame' )


############################
# Send data frame
############################
DTS_sndMsg( devId1, msgDATA )

res, ret = DTS_getMsg( devId2, responseTimeout )
if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgId'] != ftdf.FTDF_TRANSPARENT_INDICATION:
    raise StopScript( 'Expected receive transparent frame' )

res, ret = DTS_getMsg( devId1, responseTimeout )
if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgId'] != ftdf.FTDF_DATA_CONFIRM:
    raise StopScript( 'Expected data confirm' )
