import sys
from scriptIncludes import *

msgSET_rxOnWhenIdle = { 'msgId': ftdf.FTDF_SET_REQUEST,
                        'PIBAttribute': ftdf.FTDF_PIB_RX_ON_WHEN_IDLE,
                        'PIBAttributeValue': True }

set_csl_period_msg =         { 'msgId': ftdf.FTDF_SET_REQUEST,
                               'PIBAttribute': ftdf.FTDF_PIB_CSL_PERIOD,
                               'PIBAttributeValue': 80 }

set_csl_period_max_msg =     { 'msgId': ftdf.FTDF_SET_REQUEST,
                               'PIBAttribute': ftdf.FTDF_PIB_CSL_MAX_PERIOD,
                               'PIBAttributeValue': 80 }

set_csl_sync_tx_margin_msg = { 'msgId': ftdf.FTDF_SET_REQUEST,
                               'PIBAttribute': ftdf.FTDF_PIB_CSL_SYNC_TX_MARGIN,
                               'PIBAttributeValue': 80 }

set_csl_max_age_msg =        { 'msgId': ftdf.FTDF_SET_REQUEST,
                               'PIBAttribute': ftdf.FTDF_PIB_CSL_MAX_AGE_REMOTE_INFO,
                               'PIBAttributeValue': 62500 }

set_le_ena_msg =             { 'msgId': ftdf.FTDF_SET_REQUEST,
                               'PIBAttribute': ftdf.FTDF_PIB_LE_ENABLED,
                               'PIBAttributeValue': 1 }


msdu = [0xde, 0xad, 0xbe, 0xef, 0x00, 0x00, 0x00, 0x00, 0x10, 0x20]
msgDATA = {
    'msgId': ftdf.FTDF_DATA_REQUEST,
    'srcAddrMode': ftdf.FTDF_SHORT_ADDRESS,
    'dstAddrMode': ftdf.FTDF_SHORT_ADDRESS,
    'dstPANId': 0x0001,
    'dstAddr': 0x0010,
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

            devId1, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,

            devId1, set_csl_period_msg, ftdf.FTDF_SET_CONFIRM,
            devId2, set_csl_period_msg, ftdf.FTDF_SET_CONFIRM,

            devId1, set_csl_period_max_msg, ftdf.FTDF_SET_CONFIRM,
            devId2, set_csl_period_max_msg, ftdf.FTDF_SET_CONFIRM,

            devId1, set_csl_sync_tx_margin_msg, ftdf.FTDF_SET_CONFIRM,
            devId2, set_csl_sync_tx_margin_msg, ftdf.FTDF_SET_CONFIRM,

            devId1, set_csl_max_age_msg, ftdf.FTDF_SET_CONFIRM,
            devId2, set_csl_max_age_msg, ftdf.FTDF_SET_CONFIRM,

            devId1, set_le_ena_msg, ftdf.FTDF_SET_CONFIRM )


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
# Send 1000 transparent wakeup frames
############################
for i in reversed( range( 1000 ) ):
    wu_frame = [
        0x0d,
        0x2d,
        0x81,
        0xaa, # SN
        0x01, # PAN id
        0x00, # PAN id
        0x10, # short addr
        0x00, # short addr
        0x82,
        0x0e,
        0x01, # RZ
        0x01, # RZ
        0x00, # CRC
        0x00
    ]

    DTS_sendFrameTransparant( devId2, len( wu_frame ), wu_frame, 11, True, 0 )

    res, ret = DTS_getMsg( devId2, responseTimeout )

    if res == False:
        raise StopScript( 'No response from device' )
    elif ret['msgId'] != ftdf.FTDF_TRANSPARENT_CONFIRM:
        raise StopScript( 'Expected transparent confirm' )


# Check that no message was received
res, ret = DTS_getMsg( devId1, 1 )
if res:
    raise StopScript( 'Expected no msg after wu sequence without data frame' )


############################
# Disable transparent mode and enable LE
############################
DTS_enableTransparantMode( devId2, False, 0 )
DTS_sndMsg( devId2, set_le_ena_msg )

res, ret = DTS_getMsg( devId2, responseTimeout )

# Check received expected confirm
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.FTDF_SET_CONFIRM:
    raise StopScript( 'Expected SET_CONFIRM' )


############################
# Send data frame
############################
DTS_sndMsg( devId2, msgDATA )

res, ret = DTS_getMsg( devId1, responseTimeout )
if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgId'] != ftdf.FTDF_DATA_INDICATION:
    raise StopScript( 'Expected DATA_INDICATION' )

res, ret = DTS_getMsg( devId2, responseTimeout )
if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgId'] != ftdf.FTDF_DATA_CONFIRM:
    raise StopScript( 'Expected data confirm' )
