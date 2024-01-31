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
    #break
  elif ret['msgId'] != msgFlow[idx+2]:
    logstr = ( 'SCRIPT: ERROR: Expected ', msgFlow[idx+2], ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )
    error += 1
    #break
    
  idx += 3


##################################
# Test that transparent operations are disabled when in CSL mode
##################################
# Correct Frames definition:
#------------------------------- Data Frame:
# Frame Control:
#frameControl_FrameType            = 0x0000 # Beacon
frameControl_FrameType            = 0x0001 # DataFrame
#frameControl_FrameType            = 0x0002 # Acknowledgment
#frameControl_FrameType            = 0x0003 # MAC command
#frameControl_FrameType            = 0x0004 # LLDN
#frameControl_FrameType            = 0x0005 # Multipurpose

#frameControl_SecurityEnabled    = 0x0008 # Bit: 3 (Yes)
frameControl_SecurityEnabled    = 0x0000 # Bit: 3 (No)

frameControl_FramePending        = 0x0000 # Bit: 4 (No)
#frameControl_FramePending        = 0x0010 # Bit: 4 (Yes)

frameControl_AckReq                = 0x0020 # Bit: 5 (Yes)
#frameControl_AckReq            = 0x0000 # Bit: 5 (No)

#frameControl_PANidCompression    = 0x0040 # Bit: 6 (Yes)
frameControl_PANidCompression    = 0x0000 # Bit: 6 (No)

#frameControl_SequenceNrSup        = 0x0100 # Bit: 8 (Yes) # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved
frameControl_SequenceNrSup        = 0x0000 # Bit: 8 (No)  # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved

#frameControl_IEListPresent        = 0x0200 # Bit: 9 (Yes) # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved
frameControl_IEListPresent        = 0x0000 # Bit: 9 (No) # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved

frameControl_dstAddrMode        = 0x0800 # Bit: 10-11 (Short)

#frameControl_FrameVersion        = 0x0000 # Bit: 12-13 (IEEE Std 802.15.4-2003)
frameControl_FrameVersion        = 0x1000 # Bit: 12-13 (IEEE Std 802.15.4-2006)
#frameControl_FrameVersion        = 0x2000 # Bit: 12-13 (IEEE Std 802.15.4)
#frameControl_FrameVersion        = 0x3000 # Bit: 12-13 (Reserved)

frameControl_srcAddrMode        = 0x8000 # Bit: 14-15 (Short)

frameControl = ( frameControl_FrameType |
                 frameControl_SecurityEnabled |
                 frameControl_AckReq |
                 frameControl_PANidCompression |
                 frameControl_SequenceNrSup |
                 frameControl_IEListPresent |
                 frameControl_dstAddrMode |
                 frameControl_FrameVersion |
                 frameControl_srcAddrMode )

frameControlByte0 = frameControl & 0x00ff
frameControlByte1 = frameControl >> 8

# Auxiliary security header:
frameAuxSecCon_SecurityLevel            = 0x00 # Bit 0-2 (Tip: using 4 disables the use of MIC (the need to calculate and add the association bytes in the transparent send frame))
frameAuxSecCon_KeyIdentifierMode        = 0x18 # Bit 3-4
frameAuxSecCon_FrameCounterSuppression    = 0x00 # Bit 5 (No Suppression)
frameAuxSecCon_FrameCounterSize            = 0x00 # Bit 6 (4 Byte)
frameAuxSecCon_Reserved                    = 0x00 # Bit 7

frameAuxSecCon = (    frameAuxSecCon_SecurityLevel |
                    frameAuxSecCon_KeyIdentifierMode |
                    frameAuxSecCon_FrameCounterSuppression |
                    frameAuxSecCon_FrameCounterSize |
                    frameAuxSecCon_Reserved )

dataFrame = [
    frameControlByte0,
    frameControlByte1, # Frame Control
    0x00, # Sequence number
    0x01, # Destination PanId
    0x00,
    0x20, # Destination address
    0x00,
    0x01, # Source PanId
    0x00,
    0x10, # Source address
    0x00,
#   frameAuxSecCon, # Auxiliary security header: Security Control
#   0x00, # Auxiliary security header: Frame Counter (4 Byte)
#   0x00,
#   0x00,
#   0x01,
#   0x08, # Key Source (8 Byte)
#   0x09,
#   0x0a,
#   0x0b,
#   0x0c,
#   0x0d,
#   0x0e,
#   0x0f,
#   0x05, # Key Index
    0xFF, # Payload
    0xFF, # MIC32 or just extra payload
    0xFF,
    0xFF,
    0xFF,
    0x00, # FCS
    0x00
]

# Data frame
msdu = [0x1, 0x2, 0x3, 0x4, 0x5]
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
    'keySource': [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
    'keyIndex': 0,
    'frameControlOptions': 0,
    'headerIEList': 0,
    'payloadIEList': 0,
    'sendMultiPurpose': False
}

# Enable Transparant Mode Receiving DUT
options = ( ftdf.FTDF_TRANSPARENT_ENABLE_CSMA_CA |
            ftdf.FTDF_TRANSPARENT_ENABLE_FCS_GENERATION )
enable = True
DTS_enableTransparantMode( devId1, enable, options )

DTS_sndMsg( devId2, msgDATA )
res, ret = DTS_getMsg( devId2, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    error += 1
elif( ret['msgId'] != ftdf.FTDF_DATA_CONFIRM ):
    logstr = ( 'SCRIPT: ERROR: expected msgId DATA_CONFIRM', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )
    error += 1
else:
    res, ret = DTS_getMsg( devId1, responseTimeout )
    if( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        error += 1
    elif( ret['msgId'] != ftdf.FTDF_DATA_INDICATION ):
        logstr = ( 'SCRIPT: ERROR: expected msgId DATA_INDICATION', ret['msgId'] )
        raise StopScript( ''.join( map( str, logstr ) ) )
        error += 1

length = len( dataFrame )
channel = 11
handle = 0 # Application can pas data using this handle to itself
csmaSuppress = ftdf.FTDF_FALSE
DTS_sendFrameTransparant( devId1, length, dataFrame, channel, csmaSuppress, handle )
res, ret = DTS_getMsg( devId1, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    error += 1
elif( ret['msgId'] != ftdf.FTDF_TRANSPARENT_CONFIRM ):
    logstr = ( 'SCRIPT: ERROR: expected msgId ftdf.FTDF_TRANSPARENT_CONFIRM', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )
    error += 1
elif( ret['status'] != ftdf.FTDF_INVALID_PARAMETER ):
    logstr = ( 'SCRIPT: ERROR: expected status INVALID_PARAMETER, instead received ', resultStr[ ret['status'] ] )
    raise StopScript( ''.join( map( str, logstr ) ) )
    error += 1

res, ret = DTS_getMsg( devId2, responseTimeout )
if( res != False ):
    raise StopScript( 'SCRIPT: ERROR: Transparantly send frame should not be received' )
    error += 1


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
    
time.sleep( 4 )
##################################
# test when sending to other non exciting device
##################################

# Create a data request message
msg = {'msgId': ftdf.FTDF_DATA_REQUEST,
       'srcAddrMode': ftdf.FTDF_SHORT_ADDRESS,
       'dstAddrMode': ftdf.FTDF_SHORT_ADDRESS,
       'dstPANId': 0x0001,
       'dstAddr': 0x0022,
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
elif ret1['status'] != ftdf.FTDF_NO_ACK: 
    logstr = ( 'SCRIPT: ERROR: Expected FTDF_NO_ACK , instead received ', resultStr[ ret1['status'] ] )
    raise StopScript( ''.join( map( str, logstr ) ) )
    error += 1
      
##################################
# test when sending to broadcast
##################################

# Create a data request message
msg = {'msgId': ftdf.FTDF_DATA_REQUEST,
       'srcAddrMode': ftdf.FTDF_SHORT_ADDRESS,
       'dstAddrMode': ftdf.FTDF_SHORT_ADDRESS,
       'dstPANId': 0x0001,
       'dstAddr': 0xffff,
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
    
    
######################
##################################
# Data request unsynchronised
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

##################################
# Data request synchronised
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

##################################
# Data request unsynchronised beacause other channel
##################################
msgchannel = { 'msgId': ftdf.FTDF_SET_REQUEST,
                       'PIBAttribute': ftdf.FTDF_PIB_CURRENT_CHANNEL,
                       'PIBAttributeValue': 2 }

DTS_sndMsg( devId1, msgchannel )
res1, ret1 = DTS_getMsg( devId1, responseTimeout )
DTS_sndMsg( devId2, msgchannel )
res1, ret1 = DTS_getMsg( devId2, responseTimeout )

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
