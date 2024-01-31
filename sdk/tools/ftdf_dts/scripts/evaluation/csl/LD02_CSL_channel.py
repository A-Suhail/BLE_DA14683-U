# Scenario example script
# Send reset to both devices
# Device 2: Send RX enable request
# Device 1: Send data request, wait for data confirm.
# Device 2: Check for data indication.
import sys  #cli arguments
import time  #sleep

from scriptIncludes import *

set_csl_period_msg =         { 'msgId': ftdf.FTDF_SET_REQUEST, 
                               'PIBAttribute': ftdf.FTDF_PIB_CSL_PERIOD, 
                               'PIBAttributeValue': 80 }
                               
set_csl_channel_msg =         { 'msgId': ftdf.FTDF_SET_REQUEST, 
                               'PIBAttribute': ftdf.FTDF_PIB_CSL_CHANNEL_MASK, 
                               'PIBAttributeValue': 0xf }                               
                       
set_csl_period_max_msg =     { 'msgId': ftdf.FTDF_SET_REQUEST, 
                               'PIBAttribute': ftdf.FTDF_PIB_CSL_MAX_PERIOD, 
                               'PIBAttributeValue': 80 }
                           
set_csl_sync_tx_margin_msg = { 'msgId': ftdf.FTDF_SET_REQUEST, 
                               'PIBAttribute': ftdf.FTDF_PIB_CSL_SYNC_TX_MARGIN, 
                               'PIBAttributeValue': 80 }  

set_csl_max_age_msg =        { 'msgId': ftdf.FTDF_SET_REQUEST, 
                               'PIBAttribute': ftdf.FTDF_PIB_CSL_MAX_AGE_REMOTE_INFO, 
                               'PIBAttributeValue': 40000 } 

set_enh_ack_wait_msg =       { 'msgId': ftdf.FTDF_SET_REQUEST, 
                               'PIBAttribute': ftdf.FTDF_PIB_ENH_ACK_WAIT_DURATION, 
                               'PIBAttributeValue': 864 }    

set_le_ena_msg =             { 'msgId': ftdf.FTDF_SET_REQUEST, 
                               'PIBAttribute': ftdf.FTDF_PIB_LE_ENABLED, 
                               'PIBAttributeValue': 1 }    

                   

# Message order
msgFlow = ( devId1, msgRESET, ftdf.FTDF_RESET_CONFIRM,
            devId2, msgRESET, ftdf.FTDF_RESET_CONFIRM,
      
            devId1, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
      
            devId1, msgSET_Dev1_ShortAddress, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_Dev2_ShortAddress, ftdf.FTDF_SET_CONFIRM,
      
            devId1, set_csl_period_msg, ftdf.FTDF_SET_CONFIRM,
            devId2, set_csl_period_msg, ftdf.FTDF_SET_CONFIRM,
            
            
            
            devId1, set_csl_period_max_msg, ftdf.FTDF_SET_CONFIRM,
            devId2, set_csl_period_max_msg, ftdf.FTDF_SET_CONFIRM,
            
            devId1, set_csl_sync_tx_margin_msg, ftdf.FTDF_SET_CONFIRM,
            devId2, set_csl_sync_tx_margin_msg, ftdf.FTDF_SET_CONFIRM,
            
            devId1, set_csl_max_age_msg, ftdf.FTDF_SET_CONFIRM,
            devId2, set_csl_max_age_msg, ftdf.FTDF_SET_CONFIRM,
            
            ##################################
            # Set enh ack wait duration
            ##################################
            
            devId1, set_enh_ack_wait_msg, ftdf.FTDF_SET_CONFIRM,
            
            ##################################
            # Set LE enabled
            ##################################
            
            devId1, set_le_ena_msg, ftdf.FTDF_SET_CONFIRM,
            devId2, set_le_ena_msg, ftdf.FTDF_SET_CONFIRM,
            
            devId1, set_csl_channel_msg, ftdf.FTDF_SET_CONFIRM,
            devId2, set_csl_channel_msg, ftdf.FTDF_SET_CONFIRM)

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
    #break
  elif ret['msgId'] != msgFlow[idx+2]:
    logstr = ( 'SCRIPT: ERROR: Expected ', msgFlow[idx+2], ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )
    error += 1
    #break
    
  idx += 3

##################################
# Data request
##################################
# Prepare MSDU payload
msdu = [0x10, 0x32, 0x54, 0x76, 0x98, 0xba, 0xdc, 0xfe, 0x10, 0x32, 0x54, 0x76, 0x98, 0xba, 0xdc, 0xfe]

# Create a data request message
msg = {'msgId': ftdf.FTDF_DATA_REQUEST,
       'srcAddrMode': ftdf.FTDF_SHORT_ADDRESS,
       'dstAddrMode': ftdf.FTDF_SHORT_ADDRESS,
       'dstPANId': 0x0001,
       'dstAddr': 0x0020,
       'msduLength': len( msdu ),
       'msdu': msdu,
       'msduHandle': 5,
       'ackTX': 1,
       'GTSTX': 0,
       'indirectTX': 0,
       'securityLevel': 0,
       'keyIdMode': 0,
       'keySource': [],
       'keyIndex': 0,
       'frameControlOptions': 0,
       'headerIEList': 0,
       'payloadIEList': 0,
       'sendMultiPurpose': 0}

DTS_sndMsg( devId1, msg )

res1, ret1 = DTS_getMsg( devId1, responseTimeout )

if (res1 == False):
    raise StopScript( "No response received from device!" )
    error += 1
elif (ret1['msgId'] != ftdf.FTDF_DATA_CONFIRM):
    logstr = ( "Incorrect response received from device: ret1=%s" % (ret1['msgId']))
    raise StopScript( ''.join( map( str, logstr ) ) )
    error += 1
elif ret1['status'] != ftdf.FTDF_SUCCESS: 
    logstr = ( 'SCRIPT: ERROR: Expected FTDF_SUCCESS , instead received ', resultStr[ ret1['status'] ] )
    raise StopScript( ''.join( map( str, logstr ) ) )
    error += 1

# Check if data indication is received on device 2
res2, ret2 = DTS_getMsg( devId2, responseTimeout )

if (res2 == False):
    raise StopScript( "No response received from device!" )
    error += 1
elif (ret2['msgId'] != ftdf.FTDF_DATA_INDICATION):
    logstr = ( "Incorrect response received from device: ret2=%s" % (ret2['msgId']))
    raise StopScript( ''.join( map( str, logstr ) ) )
    error += 1

time.sleep( 4 )

##################################
# Data request
##################################

# Create a data request message
msg = {'msgId': ftdf.FTDF_DATA_REQUEST,
       'srcAddrMode': ftdf.FTDF_SHORT_ADDRESS,
       'dstAddrMode': ftdf.FTDF_SHORT_ADDRESS,
       'dstPANId': 0x0001,
       'dstAddr': 0x0020,
       'msduLength': len( msdu ),
       'msdu': msdu,
       'msduHandle': 5,
       'ackTX': 1,
       'GTSTX': 0,
       'indirectTX': 0,
       'securityLevel': 0,
       'keyIdMode': 0,
       'keySource': [],
       'keyIndex': 0,
       'frameControlOptions': 0,
       'headerIEList': 0,
       'payloadIEList': 0,
       'sendMultiPurpose': 0}

DTS_sndMsg( devId1, msg )

res1, ret1 = DTS_getMsg( devId1, responseTimeout )

if (res1 == False):
    raise StopScript( "No response received from device!" )
    error += 1
elif (ret1['msgId'] != ftdf.FTDF_DATA_CONFIRM):
    logstr = ( "Incorrect response received from device: ret1=%s" % (ret1['msgId']))
    raise StopScript( ''.join( map( str, logstr ) ) )
    error += 1
elif ret1['status'] != ftdf.FTDF_SUCCESS: 
    logstr = ( 'SCRIPT: ERROR: Expected FTDF_SUCCESS , instead received ', resultStr[ ret1['status'] ] )
    raise StopScript( ''.join( map( str, logstr ) ) )
    error += 1

# Check if data indication is received on device 2
res2, ret2 = DTS_getMsg( devId2, responseTimeout )

if (res2 == False):
    raise StopScript( "No response received from device!" )
    error += 1
elif (ret2['msgId'] != ftdf.FTDF_DATA_INDICATION):
    logstr = ( "Incorrect response received from device: ret2=%s" % (ret2['msgId']))
    raise StopScript( ''.join( map( str, logstr ) ) )
    error += 1
    
##########################################
## END OF TEST, let examine the results ##
##########################################   
if error != 0:
  logstr = ('SCRIPT: test FAILED with ' , error , ' ERRORS')
  raise StopScript( ''.join( map( str, logstr ) ) )
