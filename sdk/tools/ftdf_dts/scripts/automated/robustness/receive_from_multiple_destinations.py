import sys, time
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
            devId3, msgRESET, ftdf.FTDF_RESET_CONFIRM,

            devId1, msgSET_Dev1_ShortAddress, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_Dev2_ShortAddress, ftdf.FTDF_SET_CONFIRM,
            devId3, msgSET_Dev3_ShortAddress, ftdf.FTDF_SET_CONFIRM,

            devId1, msgSET_Dev1_ExtendedAddress, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_Dev2_ExtendedAddress, ftdf.FTDF_SET_CONFIRM,
            devId3, msgSET_Dev3_ExtendedAddress, ftdf.FTDF_SET_CONFIRM,

            devId1, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
            devId3, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,

#            devId1, msgSET_MAX_CSMA_BACKOFFS_0, ftdf.FTDF_SET_CONFIRM,
#            devId2, msgSET_MAX_CSMA_BACKOFFS_0, ftdf.FTDF_SET_CONFIRM,
#            devId3, msgSET_MAX_CSMA_BACKOFFS_0, ftdf.FTDF_SET_CONFIRM,

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



#####################################
# Prepare burst mechanism for 3 devices
# - devId1 = receive role
# - devId2 and devId3 = send role
#####################################
DTS_setQueueParameters( devId1,
                       ftdf.DTS_QUEUE_RCV,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       0, 0 )

DTS_setQueueParameters( devId2,
                       ftdf.DTS_QUEUE_SND,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       255, 0 )

DTS_setQueueParameters( devId3,
                       ftdf.DTS_QUEUE_SND,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       255, 0 )

DTS_sndMsg( devId2, msgDATA )
DTS_sndMsg( devId3, msgDATA )

DTS_setQueueEnable( devId2, True )


##############################
# get results
##############################
res, ret = DTS_getMsg( devId2, 60 )

if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgTotal'] != 256:
    raise StopScript( 'Expected 256 sent messages' )
elif ret['msgSuccess'] != 256:
    raise StopScript( 'Expected 256 successful messages' )


DTS_setQueueEnable( devId3, True )

res, ret = DTS_getMsg( devId3, 60 )

if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgTotal'] != 256:
    raise StopScript( 'Expected 256 sent messages' )
elif ret['msgSuccess'] != 256:
    raise StopScript( 'Expected 256 successful messages' )

time.sleep(1)

DTS_setQueueParameters( devId1,
                       ftdf.DTS_QUEUE_DIS,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       0, 0 )

res, ret = DTS_getMsg( devId1, responseTimeout )

if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgTotal'] != 512:
    raise StopScript( 'Expected 512 sent messages' )
elif ret['msgSuccess'] != 512:
    raise StopScript( 'Expected 512 successful messages' )

