## Arbiter v2 behavior (Auto PTI, MAC-PTI pair vs MAC-PTI pair).
## FTDF transparent Tx vs EXT behavior
## Script tests how FTDF transparent Tx is affected when enabling EXT when:
## A) EXT has priority over FTDF 
## B) FTDF has priority over EXT
##
## Steps
## ---------
## - 1,2< Set FTDF TX PTI=1, RX PTI=2
## - 1< Set Arbiter configuration 0=EXT, 1=(FTDF, 1)
## - 2< Set Arbiter configuration 0=EXT, 1=(FTDF, 2)
## - 2< Enable Rx
## - 1< Enable EXT
## - 1< Send/Verify 4 frames
## - 2< Verify no frames received
## - 1< Disable EXT
## - 2< Disable Rx
## - 1< Set Arbiter configuration 0=(FTDF, 1), 1=EXT 
## - 2< Set Arbiter configuration 0=EXT, 1=(FTDF, 2)
## - 2< Enable Rx
## - 1< Enable EXT
## - 1< Send/Verify 4 frames
## - 2< Verify at least 1 frame received
## - 1< Disable EXT
## - 2< Disable Rx

import sys    #cli arguments
import time    #sleep

from scriptIncludes import *

DTS_BLEReset(devId1)
# Expect OK
res, ret = DTS_getMsg( devId1, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_BLE_OK, 
               ' confirm, instead received ', ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )
 
DTS_BLEReset(devId2)
# Expect OK
res, ret = DTS_getMsg( devId2, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.DTS_MSG_ID_BLE_OK, 
               ' confirm, instead received ', ret['msgId'] )
    raise StopScript( ''.join( map( str, logstr ) ) )

# time.sleep(5)

channel = 11

# Data frame
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

#frameControl_AckReq            = 0x0020 # Bit: 5 (Yes)
frameControl_AckReq                = 0x0000 # Bit: 5 (No)

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
    0x01, # Sequence number
    0x01, # Destination PanId
    0x00,
    0x20, # Destination address
    0x00,
    0x01, # Source PanId
    0x00,
    0x10, # Source address
    0x00,
#    frameAuxSecCon, # Auxiliary security header: Security Control
#    0x00, # Auxiliary security header: Frame Counter (4 Byte)
#    0x00,
#    0x00,
#    0x01,
#    0x08, # Key Source (8 Byte)
#    0x09,
#    0x0a,
#    0x0b,
#    0x0c,
#    0x0d,
#    0x0e,
#    0x0f,
#    0x05, # Key Index
    0xFF, # Payload
    0xFF, # MIC32 or just extra payload
    0xFF,
    0xFF,
    0xFF,
    0x00, # FCS
    0x00
]


msgSET_PtiConfig = { 'msgId': ftdf.FTDF_SET_REQUEST,
           'PIBAttribute': ftdf.FTDF_PIB_PTI_CONFIG,
           'PIBAttributeValue': [2, 1, 3, 4, 5, 6, 7, 8] }

# Prepare test messages
msgFlow = ( devId1, msgRESET, ftdf.FTDF_RESET_CONFIRM,
            devId2, msgRESET, ftdf.FTDF_RESET_CONFIRM,
            
            devId1, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
            
            devId1, msgSET_Dev1_ShortAddress, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_Dev2_ShortAddress, ftdf.FTDF_SET_CONFIRM,
            
            devId1, msgSET_PtiConfig, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_PtiConfig, ftdf.FTDF_SET_CONFIRM,
            )


msgDbgModeSetRequest = {
    'msgId': ftdf.FTDF_DBG_MODE_SET_REQUEST,
    'dbgMode': 0x1,
}

idx = 0
res = True

while( idx < len( msgFlow ) ):
    # Send message
    DTS_sndMsg( msgFlow[idx], msgFlow[idx+1] )

    # Get message confirm
    res, ret = DTS_getMsg( msgFlow[idx], responseTimeout )

    # Check received expected confirm
    if( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        break
    elif ret['msgId'] != msgFlow[idx+2]:
        logstr = ( 'SCRIPT: ERROR: Expected ', msgFlow[idx+2], ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
        raise StopScript( ''.join( map( str, logstr ) ) )
        break
    else:
        if ret['msgId'] == ftdf.FTDF_SET_CONFIRM:
            if( ret['status'] != ftdf.FTDF_SUCCESS ):
                break
            # Check set request with get request
            msgGet['PIBAttribute'] = msgFlow[idx+1]['PIBAttribute']

            DTS_sndMsg( msgFlow[idx], msgGet )

            res2, ret2 = DTS_getMsg( msgFlow[idx], responseTimeout )

            if( res2 == False ):
                raise StopScript( 'SCRIPT: ERROR: No response received from device' )
                break
            elif ret2['msgId'] != ftdf.FTDF_GET_CONFIRM:
                logstr = ( 'SCRIPT: ERROR: Expected GET_CONFIRM, instead received ', ret2['msgId'] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                break
            elif ret2['PIBAttributeValue'] != msgFlow[idx+1]['PIBAttributeValue']:
                logstr = ( 'SCRIPT: ERROR: Incorrect set PIBAttribute: ', msgGet['PIBAttribute'] );
                raise StopScript( ''.join( map( str, logstr ) ) )
                break
        else:
            if( ret['status'] != ftdf.FTDF_SUCCESS ):
                break

    idx += 3

# =================================================================================================#
# Enable transparent mode 
# 
options = ( ftdf.FTDF_TRANSPARENT_ENABLE_CSMA_CA |
            ftdf.FTDF_TRANSPARENT_ENABLE_FCS_GENERATION )
enable = True
DTS_enableTransparantMode( devId1, enable, options )
DTS_enableTransparantMode( devId2, enable, options )

# =================================================================================================#
# Reset arbiter
DTS_ArbiterReset(devId1)
DTS_ArbiterReset(devId2)

# =================================================================================================#
# =================================================================================================#

# On Tx side, Set arbiter configuration EXT priority over FTDF on Tx
DTS_ArbiterSetConfig(devId1, 0x07f0, 0, 0, 
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

# On Rx side specify Rx PTI
DTS_ArbiterSetConfig(devId2, 0x07f0, 0, 0, 
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

# Turn Rx on on devId2
DTS_sndMsg(devId2, msgRxEnable_On)

# Expect confirm
res, ret = DTS_getMsg( devId2, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.FTDF_RX_ENABLE_CONFIRM, 
               ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )

# Turn on external on devId1
DTS_ArbiterSetExtStatus(devId1, 1)

# Send data from devId1 (4 packets)
for i in range(4):
    # Data packet
    DTS_sendFrameTransparant( devId1, len( dataFrame ), dataFrame, channel, ftdf.FTDF_FALSE, 0, 1 )
    # Expect confirm
    res, ret = DTS_getMsg( devId1, responseTimeout )
    if( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    elif ret['msgId'] != ftdf.FTDF_TRANSPARENT_CONFIRM:
        logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.FTDF_TRANSPARENT_CONFIRM, 
                   ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
        raise StopScript( ''.join( map( str, logstr ) ) )

# Expect no message on devId2
res, ret = DTS_getMsg( devId2, responseTimeout )
if( res == True ):
    logstr = ( 'SCRIPT: ERROR: Expected no message, instead received msgId', 
               msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )

# Turn off external on peripheral
DTS_ArbiterSetExtStatus(devId1, 0)

# Turn Rx off on devId2
DTS_sndMsg(devId2, msgRxEnable_Off)

# Expect confirm
res, ret = DTS_getMsg( devId2, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.FTDF_RX_ENABLE_CONFIRM, 
               ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )

# =================================================================================================#
# Set arbiter configuration FTDF priority over EXT
DTS_ArbiterSetConfig(devId1, 0x07f0, 0, 0, 
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

# On Rx side specify Rx PTI
DTS_ArbiterSetConfig(devId2, 0x07f0, 0, 0, 
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

# Turn Rx on on devId2
DTS_sndMsg(devId2, msgRxEnable_On)

# Expect confirm
res, ret = DTS_getMsg( devId2, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.FTDF_RX_ENABLE_CONFIRM, 
               ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )

# Turn on external on devId1
DTS_ArbiterSetExtStatus(devId1, 1)

# Send data from devId1 (4 packets)
for i in range(4):
    # Data packet
    DTS_sendFrameTransparant( devId1, len( dataFrame ), dataFrame, channel, ftdf.FTDF_FALSE, 0, 1 )
    # Expect confirm
    res, ret = DTS_getMsg( devId1, responseTimeout )
    if( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    elif ret['msgId'] != ftdf.FTDF_TRANSPARENT_CONFIRM:
        logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.FTDF_TRANSPARENT_CONFIRM, 
                   ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
        raise StopScript( ''.join( map( str, logstr ) ) )

# Expect at least one message
count = 0
while(1):
    res, ret = DTS_getMsg( devId2, responseTimeout )
    if( res == False ):
        break
    elif ret['msgId'] != ftdf.FTDF_TRANSPARENT_INDICATION:
        logstr = ( 'SCRIPT: ERROR: Expected FTDF_DATA_INDICATION confirm, instead received ', 
                   ret['msgId'] )
        raise StopScript( ''.join( map( str, logstr ) ) )
        break
    count = count + 1

if (count == 0):
    logstr = ( 'SCRIPT: ERROR: Expected at least one received packet, instead received none')
    raise StopScript( ''.join( map( str, logstr ) ) )


# Turn off external on peripheral
DTS_ArbiterSetExtStatus(devId1, 0)

# Turn Rx off on devId2
DTS_sndMsg(devId2, msgRxEnable_Off)

# Expect confirm
res, ret = DTS_getMsg( devId2, responseTimeout )
if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
elif ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM:
    logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.FTDF_RX_ENABLE_CONFIRM, 
               ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )


