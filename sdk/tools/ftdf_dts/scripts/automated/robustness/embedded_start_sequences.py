import sys, time
from scriptIncludes import *

msdu = [0x01, 0x02, 0x03, 0x04, 0x00, 0x00, 0x00, 0x00, 0x7a, 0x85]
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
    'keySource': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
    'keyIndex': 0,
    'frameControlOptions': 0,
    'headerIEList': 0,
    'payloadIEList': 0,
    'sendMultiPurpose': False
}

msgRxEnable_1 = { 'msgId': ftdf.FTDF_RX_ENABLE_REQUEST,
                  'deferPermit': False,
                  'rxOnTime': 0,
                  'rxOnDuration':1 }
# Message order
msgFlow = ( devId1, msgRESET, ftdf.FTDF_RESET_CONFIRM,
            devId2, msgRESET, ftdf.FTDF_RESET_CONFIRM,

            devId1, msgSET_Dev1_ShortAddress, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_Dev2_ShortAddress, ftdf.FTDF_SET_CONFIRM,

            devId1, msgSET_Dev1_ExtendedAddress, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_Dev2_ExtendedAddress, ftdf.FTDF_SET_CONFIRM,

            devId1, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_PANId, ftdf.FTDF_SET_CONFIRM )

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


for i in range( 100 ):
    DTS_sndMsg( devId1, msgDATA )

    time.sleep(.01)
    DTS_sndMsg( devId2, msgRxEnable_1 )

    res, ret = DTS_getMsg( devId2, responseTimeout )

    if res == False:
        raise StopScript( 'No response from device' )
    elif ret['status'] != ftdf.FTDF_SUCCESS:
        raise StopScript( 'Rx could not be enabled' )

    res, ret = DTS_getMsg( devId1, responseTimeout )

    if res == False:
        raise StopScript( 'No response from device' )
    elif ret['status'] != ftdf.FTDF_NO_ACK:
        raise StopScript( 'Expected no acknowledge frame' )

    res, ret = DTS_getMsg( devId2, 1 )

    if res == True:
        raise StopScript( 'Expected no received frame' )
