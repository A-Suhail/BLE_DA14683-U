import sys
from scriptIncludes import *

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
            devId1, msgSET_PANId, ftdf.FTDF_SET_CONFIRM )

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
# Send 256 data frames using burst mechanism
#####################################
DTS_setQueueParameters(devId1,
                       ftdf.DTS_QUEUE_SND,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       255, 0 )

DTS_sndMsg( devId1, msgDATA )
DTS_setQueueEnable( devId1, True )

# get results
res, ret = DTS_getMsg( devId1, responseTimeout )

if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgTotal'] != 256:
    raise StopScript( 'Expected 256 sent messages' )
elif ret['msgSuccess'] != 0:
    raise StopScript( 'Expected 0 successful messages' )
