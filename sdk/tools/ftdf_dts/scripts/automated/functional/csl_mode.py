import sys  #cli arguments
import time  #sleep

from scriptIncludes import *

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
                               'PIBAttributeValue': 40000 } 

set_le_ena_msg =             { 'msgId': ftdf.FTDF_SET_REQUEST, 
                               'PIBAttribute': ftdf.FTDF_PIB_LE_ENABLED, 
                               'PIBAttributeValue': 1 }    

set_le_dis_msg =             { 'msgId': ftdf.FTDF_SET_REQUEST, 
                               'PIBAttribute': ftdf.FTDF_PIB_LE_ENABLED, 
                               'PIBAttributeValue': 0 }    


# Message order
msgFlow = ( devId1, msgRESET, ftdf.FTDF_RESET_CONFIRM,
            devId2, msgRESET, ftdf.FTDF_RESET_CONFIRM,

            ##################################
            # 1+2> Set short address and PAN ID
            ##################################
            devId1, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,

            devId1, msgSET_Dev1_ShortAddress, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_Dev2_ShortAddress, ftdf.FTDF_SET_CONFIRM,

            ##################################
            # 1+2> Set macCSLPeriod, macCSLMaxPeriod,
            #      macCSLTxSyncMargin and macCSLMaxAgeRemoteInfo
            ##################################
            devId1, set_csl_period_msg, ftdf.FTDF_SET_CONFIRM,
            devId2, set_csl_period_msg, ftdf.FTDF_SET_CONFIRM,

            devId1, set_csl_period_max_msg, ftdf.FTDF_SET_CONFIRM,
            devId2, set_csl_period_max_msg, ftdf.FTDF_SET_CONFIRM,

            devId1, set_csl_sync_tx_margin_msg, ftdf.FTDF_SET_CONFIRM,
            devId2, set_csl_sync_tx_margin_msg, ftdf.FTDF_SET_CONFIRM,

            devId1, set_csl_max_age_msg, ftdf.FTDF_SET_CONFIRM,
            devId2, set_csl_max_age_msg, ftdf.FTDF_SET_CONFIRM,

            ##################################
            # 1+2> Set LE enabled
            ##################################
            devId1, set_le_ena_msg, ftdf.FTDF_SET_CONFIRM,
            devId2, set_le_ena_msg, ftdf.FTDF_SET_CONFIRM)

idx = 0
res = True
error = 0

while( idx < len( msgFlow ) ):
  # Send message
  DTS_sndMsg( msgFlow[idx], msgFlow[idx+1] )

  # Get message confirm
  res, ret = DTS_getMsg( msgFlow[idx],responseTimeout )

  # Check received expected confirm
  if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    error += 1
  elif ret['msgId'] != msgFlow[idx+2]:
    logstr = ( 'SCRIPT: ERROR: Expected ', msgFlow[idx+2], ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )
    error += 1

  idx += 3


# Data frame
msdu = [0x1, 0x2, 0x3, 0x4, 0x5]
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
    'keySource': [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
    'keyIndex': 0,
    'frameControlOptions': 0,
    'headerIEList': 0,
    'payloadIEList': 0,
    'sendMultiPurpose': False
}

########################################
# 1> Send data frame with short address matching DUT2
########################################
DTS_sndMsg( devId1, msgDATA )

res, ret = DTS_getMsg( devId1, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    error += 1
elif( ret['msgId'] != ftdf.FTDF_DATA_CONFIRM ):
    logstr = ( 'SCRIPT: ERROR: expected msgId DATA_CONFIRM', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )
    error += 1
else:
    ################################################
    # 2< Receive data frame matching sent data frame
    ################################################
    res, ret = DTS_getMsg( devId2, responseTimeout )
    if( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        error += 1
    elif( ret['msgId'] != ftdf.FTDF_DATA_INDICATION ):
        logstr = ( 'SCRIPT: ERROR: expected msgId DATA_INDICATION', ret['msgId'] )
        raise StopScript( ''.join( map( str, logstr ) ) )
        error += 1
    else:
        if msgDATA['msdu'] != ret['msdu']:
            raise StopScript( 'SCRIPT: ERROR: Received unexpected MSDU' )


########################################
# 1> Send data frame with short multicast address
########################################
msgDATA['dstAddr'] = 0xffff

DTS_sndMsg( devId1, msgDATA )

res, ret = DTS_getMsg( devId1, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    error += 1
elif( ret['msgId'] != ftdf.FTDF_DATA_CONFIRM ):
    logstr = ( 'SCRIPT: ERROR: expected msgId DATA_CONFIRM', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )
    error += 1
else:
    ################################################
    # 2< Receive data frame matching sent data frame
    ################################################
    res, ret = DTS_getMsg( devId2, responseTimeout )
    if( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        error += 1
    elif( ret['msgId'] != ftdf.FTDF_DATA_INDICATION ):
        logstr = ( 'SCRIPT: ERROR: expected msgId DATA_INDICATION', ret['msgId'] )
        raise StopScript( ''.join( map( str, logstr ) ) )
        error += 1
    else:
        if msgDATA['msdu'] != ret['msdu']:
            raise StopScript( 'SCRIPT: ERROR: Received unexpected MSDU' )
        elif msgDATA['dstAddr'] != ret['dstAddr']:
            raise StopScript( 'SCRIPT: ERROR: Expected dstAddr = 0xffff' )


########################################
# 2> Set macLeEnabled to false
########################################
DTS_sndMsg( devId2, set_le_dis_msg )
res, ret = DTS_getMsg( devId2, responseTimeout )

if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgId'] != ftdf.FTDF_SET_CONFIRM:
    raise StopScript( 'Incorrect response from device' )


########################################
# 2> Set transparent mode with no option set
########################################
DTS_enableTransparantMode( devId2, True, 0 )


########################################
# 1> Send data frame with short address matching DUT2
########################################
msgDATA['dstAddr'] = 0x0020

DTS_sndMsg( devId1, msgDATA )

################################################
# 1< Receive NO_ACK data confirm
################################################
res, ret = DTS_getMsg( devId1, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    error += 1
elif( ret['msgId'] != ftdf.FTDF_DATA_CONFIRM ):
    logstr = ( 'SCRIPT: ERROR: expected msgId DATA_CONFIRM', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )
    error += 1
elif ret['status'] != ftdf.FTDF_NO_ACK:
    raise StopScript( 'Expected NO_ACK data confirm' )


