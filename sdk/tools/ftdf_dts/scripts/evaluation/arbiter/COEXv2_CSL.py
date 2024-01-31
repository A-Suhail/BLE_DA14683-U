## Arbiter v2 behavior (Auto PTI, MAC-PTI pair vs MAC-PTI pair).
## FTDF CSL mode vs EXT behavior
## Script tests how FTDF CSL mode TX and RX is affected when enabling EXT
## 
## Steps
## ---------
## - 1,2< Enable CSL mode 
## - 1,2< Set FTDF TX PTI=1, RX PTI=2
## - 2< Set Arbiter configuration 0=EXT, 1=(FTDF, 1)
## - 1< Set Arbiter configuration 0=EXT, 1=(FTDF, 2)
## - 2< Send frame
## - 2< Verify send success
## - 1> Verify received frame
## - 2> Enable EXT
## - 2< Send frame
## - 2< Verify send success
## - 1> Verify no received frame
## - 2> Disable EXT
## - 2< Set Arbiter configuration 0=(FTDF, 1), 1=EXT
## - 1< Set Arbiter configuration 0=EXT, 1=(FTDF, 2)
## - 2< Send frame
## - 2< Verify send success
## - 1> Verify received frame
## - 2> Enable EXT
## - 2< Send frame
## - 2< Verify send success
## - 1> Verify received frame
## - 2> Disable EXT
## - 2< Set Arbiter configuration 0=(FTDF, 1), 1=EXT
## - 1< Set Arbiter configuration 0=EXT, 1=(FTDF, 2)
## - 2< Send frame
## - 2< Verify send success
## - 1> Verify received frame
## - 1> Enable EXT
## - 2< Send frame
## - 2< Verify send success
## - 1> Verify no received frame
## - 1> Disable EXT
## - 2< Set Arbiter configuration 0=(FTDF, 1), 1=EXT
## - 1< Set Arbiter configuration 1=(FTDF, 2), 0=EXT
## - 2< Send frame
## - 2< Verify send success
## - 1> Verify received frame
## - 1> Enable EXT
## - 2< Send frame
## - 2< Verify send success
## - 1> Verify received frame
## - 1> Disable EXT


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

msgSET_PtiConfig = { 'msgId': ftdf.FTDF_SET_REQUEST,
           'PIBAttribute': ftdf.FTDF_PIB_PTI_CONFIG,
           'PIBAttributeValue': [2, 1, 3, 4, 5, 6, 7, 8] }                   


msgSET_keepPhyEnable = { 'msgId': ftdf.FTDF_SET_REQUEST,
           'PIBAttribute': ftdf.FTDF_PIB_KEEP_PHY_ENABLED,
           'PIBAttributeValue': 1 }    


msgDbgModeSetRequest = {
    'msgId': ftdf.FTDF_DBG_MODE_SET_REQUEST,
    'dbgMode': 0x3b,
}

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
            
            devId1, msgSET_PtiConfig, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_PtiConfig, ftdf.FTDF_SET_CONFIRM,
            
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

# Reset arbiter
DTS_ArbiterReset(devId1)
DTS_ArbiterReset(devId2)

# DTS_sndMsg(devId1, msgDbgModeSetRequest);
# DTS_sndMsg(devId2, msgDbgModeSetRequest);

# On Tx side, Set arbiter configuration EXT priority over FTDF on Tx
DTS_ArbiterSetConfig(devId2, 0x07f0, 0, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_EXT, 0,
                     ftdf.DTS_COEX_MAC_TYPE_FTDF, 1,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0 )
 
DTS_ArbiterSetConfig(devId1, 0x07f0, 0, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_EXT, 0,
                     ftdf.DTS_COEX_MAC_TYPE_FTDF, 2,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0 )

DTS_sndMsg( devId2, msgDATA )
res, ret = DTS_getMsg( devId2, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    error += 1
elif( ret['msgId'] != ftdf.FTDF_DATA_CONFIRM ):
    logstr = ( 'SCRIPT: ERROR: expected msgId DATA_CONFIRM', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )
    error += 1
elif ( ret['status'] != ftdf.FTDF_SUCCESS):
    logstr = ( 'SCRIPT: ERROR: expected FTDF_SUCCESS ', ret['status'] )
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

# Turn on external on devId2
DTS_ArbiterSetExtStatus(devId2, 1)

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
    if( res == True ):
        raise StopScript( 'SCRIPT: ERROR: No response expected from device' )
        error += 1

# Turn off external on devId2
DTS_ArbiterSetExtStatus(devId2, 0)

# Reset arbiter
DTS_ArbiterReset(devId1)
DTS_ArbiterReset(devId2)
 
# On Tx side, Set arbiter configuration EXT priority over FTDF on Tx
DTS_ArbiterSetConfig(devId2, 0x07f0, 0, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_FTDF, 1,
                     ftdf.DTS_COEX_MAC_TYPE_EXT, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0 )
  
DTS_ArbiterSetConfig(devId1, 0x07f0, 0, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_EXT, 0,
                     ftdf.DTS_COEX_MAC_TYPE_FTDF, 2,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0 )
 
DTS_sndMsg( devId2, msgDATA )
res, ret = DTS_getMsg( devId2, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    error += 1
elif( ret['msgId'] != ftdf.FTDF_DATA_CONFIRM ):
    logstr = ( 'SCRIPT: ERROR: expected msgId DATA_CONFIRM', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )
    error += 1
elif ( ret['status'] != ftdf.FTDF_SUCCESS):
    logstr = ( 'SCRIPT: ERROR: expected FTDF_SUCCESS ', ret['status'] )
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
 
# Turn on external on devId2
DTS_ArbiterSetExtStatus(devId2, 1)
 
DTS_sndMsg( devId2, msgDATA )
res, ret = DTS_getMsg( devId2, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    error += 1
elif( ret['msgId'] != ftdf.FTDF_DATA_CONFIRM ):
    logstr = ( 'SCRIPT: ERROR: expected msgId DATA_CONFIRM', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )
    error += 1
elif ( ret['status'] != ftdf.FTDF_SUCCESS):
    logstr = ( 'SCRIPT: ERROR: expected FTDF_SUCCESS ', ret['status'] )
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
 
# Turn off external on devId1
DTS_ArbiterSetExtStatus(devId2, 0)
 
####################################################################################################
# Arbiter Rx side
# 
# Reset arbiter
 
DTS_ArbiterReset(devId1)
DTS_ArbiterReset(devId2)
 
DTS_ArbiterSetConfig(devId2, 0x07f0, 0, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_FTDF, 1,
                     ftdf.DTS_COEX_MAC_TYPE_EXT, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0 )
 
DTS_ArbiterSetConfig(devId1, 0x07f0, 0, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_EXT, 0,
                     ftdf.DTS_COEX_MAC_TYPE_FTDF, 2,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0 )
 
 
 
DTS_sndMsg( devId2, msgDATA )
res, ret = DTS_getMsg( devId2, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    error += 1
elif( ret['msgId'] != ftdf.FTDF_DATA_CONFIRM ):
    logstr = ( 'SCRIPT: ERROR: expected msgId DATA_CONFIRM', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )
    error += 1
elif ( ret['status'] != ftdf.FTDF_SUCCESS):
    logstr = ( 'SCRIPT: ERROR: expected FTDF_SUCCESS ', ret['status'] )
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
 
# Turn on external on devId1
DTS_ArbiterSetExtStatus(devId1, 1)
 
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
    if( res == True ):
        raise StopScript( 'SCRIPT: ERROR: No response expected from device' )
        error += 1
 
# Turn off external on devId1
DTS_ArbiterSetExtStatus(devId1, 0)
 
# Reset arbiter
DTS_ArbiterReset(devId1)
DTS_ArbiterReset(devId2)
 
DTS_ArbiterSetConfig(devId2, 0x07f0, 0, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_FTDF, 1,
                     ftdf.DTS_COEX_MAC_TYPE_EXT, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0 )
 
DTS_ArbiterSetConfig(devId1, 0x07f0, 0, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_FTDF, 2,
                     ftdf.DTS_COEX_MAC_TYPE_EXT, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0,
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_NONE, 0 )
 
 
DTS_sndMsg( devId2, msgDATA )
res, ret = DTS_getMsg( devId2, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    error += 1
elif( ret['msgId'] != ftdf.FTDF_DATA_CONFIRM ):
    logstr = ( 'SCRIPT: ERROR: expected msgId DATA_CONFIRM', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )
    error += 1
elif ( ret['status'] != ftdf.FTDF_SUCCESS):
    logstr = ( 'SCRIPT: ERROR: expected FTDF_SUCCESS ', ret['status'] )
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
 
# Turn on external on devId1
DTS_ArbiterSetExtStatus(devId1, 1)
 
DTS_sndMsg( devId2, msgDATA )
res, ret = DTS_getMsg( devId2, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    error += 1
elif( ret['msgId'] != ftdf.FTDF_DATA_CONFIRM ):
    logstr = ( 'SCRIPT: ERROR: expected msgId DATA_CONFIRM', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )
    error += 1
elif ( ret['status'] != ftdf.FTDF_SUCCESS):
    logstr = ( 'SCRIPT: ERROR: expected FTDF_SUCCESS ', ret['status'] )
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
 
# Turn off external on devId1
DTS_ArbiterSetExtStatus(devId1, 0)
 
# Reset arbiter
DTS_ArbiterReset(devId1)
 
# Reset arbiter
DTS_ArbiterReset(devId2)

##########################################
## END OF TEST, let examine the results ##
##########################################   
if error != 0:
  logstr = ('SCRIPT: test FAILED with ' , error , ' ERRORS')
  raise StopScript( ''.join( map( str, logstr ) ) )

