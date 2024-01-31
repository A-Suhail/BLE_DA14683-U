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
    'dstAddr': 0x0000000000000010,
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

            devId1, msgSET_rxOnWhenIdle, ftdf.FTDF_SET_CONFIRM )

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
DTS_enableTransparantMode( devId2, True, ftdf.FTDF_TRANSPARENT_ENABLE_FCS_GENERATION )


############################
# Send a burst of 8 frames with AR=1
############################
fc_frameType    = 0x0001 # dataframe
fc_ackRequest   = 0x0020
fc_dstAddrMode  = 0x0800 # short
fc_frameVersion = 0x1000 # 2006
fc_srcAddrMode  = 0x8000 # short

frameControl = ( fc_frameType | fc_ackRequest | fc_dstAddrMode | fc_frameVersion | fc_srcAddrMode )

fc_byte0 = frameControl & 0xff
fc_byte1 = frameControl >> 8

DTS_setQueueParameters( devId2,
                       ftdf.DTS_QUEUE_SND,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       0, 0 )

for i in range( 8 ):
    dataframe = [
        fc_byte0,
        fc_byte1,
        i,    # SN
        0x01, # dst PAN ID
        0x00,
        0x10, # dest addr
        0x00,
        0x01, # src PAN ID
        0x00,
        0x20, # src addr
        0x00,
        0xff, # Payload
        0xff,
        0xff,
        0xff,
        0xff,
        0x00, # FCS
        0x00
    ]

    DTS_sendFrameTransparant( devId2, len( dataframe ), dataframe, 11, True, 0 )


DTS_setQueueEnable( devId2, True )

res, ret = DTS_getMsg( devId2, responseTimeout )

if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgTotal'] != 8:
    raise StopScript( 'Expected 8 sent messages' )
elif ret['msgSuccess'] != 8:
    raise StopScript( 'Expected 8 successful messages' )


cnt = 0
while True:
    # Expect less than 8 messages
    res, ret = DTS_getMsg( devId1, responseTimeout )

    if res == False:
        break

    cnt += 1

if cnt >= 8:
    raise StopScript( 'Expected less than 8 messages on receiving side' )


############################
# Disable transparent mode and send data frame
############################
DTS_enableTransparantMode( devId2, False, 0 )


DTS_sndMsg( devId2, msgDATA )

res, ret = DTS_getMsg( devId1, responseTimeout )
if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgId'] != ftdf.FTDF_DATA_INDICATION:
    raise StopScript( 'Expected receive transparent frame' )

res, ret = DTS_getMsg( devId2, responseTimeout )
if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgId'] != ftdf.FTDF_DATA_CONFIRM:
    raise StopScript( 'Expected data confirm' )
