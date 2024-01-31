import sys    #cli arguments

from scriptIncludes import *


# Message order
msgFlow = (
    devId1, msgRESET, ftdf.FTDF_RESET_CONFIRM,
    devId2, msgRESET, ftdf.FTDF_RESET_CONFIRM,

    devId1, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
    devId2, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,

    devId1, msgSET_Dev1_ShortAddress, ftdf.FTDF_SET_CONFIRM,
    devId2, msgSET_Dev2_ShortAddress, ftdf.FTDF_SET_CONFIRM,

    devId2, msgRxEnable_On, ftdf.FTDF_RX_ENABLE_CONFIRM
)


idx = 0
result = True
while( idx < len( msgFlow ) ):
    # Send message
    DTS_sndMsg( msgFlow[idx], msgFlow[idx+1] )

    # Get message confirm
    res, ret = DTS_getMsg( msgFlow[idx], responseTimeout )

    # Check received expected confirm
    if( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        result = False
        break
    elif ret['msgId'] != msgFlow[idx+2]:
        logstr = ( 'SCRIPT: ERROR: Expected ', msgFlow[idx+2], ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False
        break
    else:
        if( ret['msgId'] == ftdf.FTDF_SET_CONFIRM ):

            if( ret['status'] != ftdf.FTDF_SUCCESS ):
                result = False
                break

            # Check set request with get request
            msgGet['PIBAttribute'] = msgFlow[idx+1]['PIBAttribute']

            DTS_sndMsg( msgFlow[idx], msgGet )

            res2, ret2 = DTS_getMsg( msgFlow[idx], responseTimeout )
            if( res2 == False ):
                raise StopScript( 'SCRIPT: ERROR: No response received from device' )
                result = False
                break
            elif ret2['msgId'] != ftdf.FTDF_GET_CONFIRM:
                logstr = ( 'SCRIPT: ERROR: Expected GET_CONFIRM, instead received ', ret2['msgId'] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break
            elif ret2['PIBAttributeValue'] != msgFlow[idx+1]['PIBAttributeValue']:
                logstr = ( 'SCRIPT: ERROR: Incorrect set PIBAttribute: ', msgGet['PIBAttribute'] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break
        else:
            if( ret['status'] != ftdf.FTDF_SUCCESS ):
                result = False
                break

    idx += 3

# Following options are allready tested in FR3010 srcipt:
# FTDF_TRANSPARENT_PASS_FRAME_TYPE_0
# FTDF_TRANSPARENT_PASS_FRAME_TYPE_1
# FTDF_TRANSPARENT_PASS_FRAME_TYPE_2
# FTDF_TRANSPARENT_PASS_FRAME_TYPE_3
# FTDF_TRANSPARENT_PASS_FRAME_TYPE_5
# FTDF_TRANSPARENT_PASS_ALL_FRAME_TYPES
# FTDF_TRANSPARENT_AUTO_ACK

# Following options are allready tested in FR3020 srcipt:
# FTDF_TRANSPARENT_ENABLE_FCS_GENERATION


# Test: FTDF_TRANSPARENT_PASS_CRC_ERROR
#------------------------------- Data Frame:
# Frame Control:
#frameControl_FrameType         = 0x0000 # Beacon
frameControl_FrameType          = 0x0001 # DataFrame
#frameControl_FrameType         = 0x0002 # Acknowledgment
#frameControl_FrameType         = 0x0003 # MAC command
#frameControl_FrameType         = 0x0004 # LLDN
#frameControl_FrameType         = 0x0005 # Multipurpose

#frameControl_SecurityEnabled   = 0x0008 # Bit: 3 (Yes)
frameControl_SecurityEnabled    = 0x0000 # Bit: 3 (No)

frameControl_FramePending       = 0x0000 # Bit: 4 (No)
#frameControl_FramePending      = 0x0010 # Bit: 4 (Yes)

#frameControl_AckReq            = 0x0020 # Bit: 5 (Yes)
frameControl_AckReq             = 0x0000 # Bit: 5 (No)

#frameControl_PANidCompression  = 0x0040 # Bit: 6 (Yes)
frameControl_PANidCompression   = 0x0000 # Bit: 6 (No)

#frameControl_SequenceNrSup     = 0x0100 # Bit: 8 (Yes) # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved
frameControl_SequenceNrSup      = 0x0000 # Bit: 8 (No)  # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved

#frameControl_IEListPresent     = 0x0200 # Bit: 9 (Yes) # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved
frameControl_IEListPresent      = 0x0000 # Bit: 9 (No) # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved

frameControl_dstAddrMode        = 0x0800 # Bit: 10-11 (Short)

#frameControl_FrameVersion      = 0x0000 # Bit: 12-13 (IEEE Std 802.15.4-2003)
frameControl_FrameVersion       = 0x1000 # Bit: 12-13 (IEEE Std 802.15.4-2006)
#frameControl_FrameVersion      = 0x2000 # Bit: 12-13 (IEEE Std 802.15.4)
#frameControl_FrameVersion      = 0x3000 # Bit: 12-13 (Reserved)

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
frameAuxSecCon_FrameCounterSuppression  = 0x00 # Bit 5 (No Suppression)
frameAuxSecCon_FrameCounterSize         = 0x00 # Bit 6 (4 Byte)
frameAuxSecCon_Reserved                 = 0x00 # Bit 7

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

if(result):
    # Enable Transparant Mode Receiving DUT
    options = ( ftdf.FTDF_TRANSPARENT_PASS_CRC_ERROR )
    enable = True
    DTS_enableTransparantMode( devId2, enable, options )

    # Enable Transparant Mode Transmitting DUT
    options = ( ftdf.FTDF_TRANSPARENT_ENABLE_CSMA_CA )
    enable = True
    DTS_enableTransparantMode( devId1, enable, options )

    length = len( dataFrame )
    channel = 11
    handle = 0 # Application can pas data using this handle to itself
    csmaSuppress = ftdf.FTDF_FALSE
    DTS_sendFrameTransparant( devId1, length, dataFrame, channel, csmaSuppress, handle )

    res, ret = DTS_getMsg( devId1, responseTimeout )
    if( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        result = False

    res, ret = DTS_getMsg( devId2, responseTimeout )
    if( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        result = False


# Test: FTDF_TRANSPARENT_PASS_ALL_PAN_ID
# Frame Control:
#frameControl_FrameType         = 0x0000 # Beacon
frameControl_FrameType          = 0x0001 # DataFrame
#frameControl_FrameType         = 0x0002 # Acknowledgment
#frameControl_FrameType         = 0x0003 # MAC command
#frameControl_FrameType         = 0x0004 # LLDN
#frameControl_FrameType         = 0x0005 # Multipurpose

#frameControl_SecurityEnabled   = 0x0008 # Bit: 3 (Yes)
frameControl_SecurityEnabled    = 0x0000 # Bit: 3 (No)

frameControl_FramePending       = 0x0000 # Bit: 4 (No)
#frameControl_FramePending      = 0x0010 # Bit: 4 (Yes)

#frameControl_AckReq            = 0x0020 # Bit: 5 (Yes)
frameControl_AckReq             = 0x0000 # Bit: 5 (No)

#frameControl_PANidCompression  = 0x0040 # Bit: 6 (Yes)
frameControl_PANidCompression   = 0x0000 # Bit: 6 (No)

#frameControl_SequenceNrSup     = 0x0100 # Bit: 8 (Yes) # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved
frameControl_SequenceNrSup      = 0x0000 # Bit: 8 (No)  # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved

#frameControl_IEListPresent     = 0x0200 # Bit: 9 (Yes) # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved
frameControl_IEListPresent      = 0x0000 # Bit: 9 (No) # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved

frameControl_dstAddrMode        = 0x0800 # Bit: 10-11 (Short)

#frameControl_FrameVersion      = 0x0000 # Bit: 12-13 (IEEE Std 802.15.4-2003)
frameControl_FrameVersion       = 0x1000 # Bit: 12-13 (IEEE Std 802.15.4-2006)
#frameControl_FrameVersion      = 0x2000 # Bit: 12-13 (IEEE Std 802.15.4)
#frameControl_FrameVersion      = 0x3000 # Bit: 12-13 (Reserved)

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
frameAuxSecCon_FrameCounterSuppression  = 0x00 # Bit 5 (No Suppression)
frameAuxSecCon_FrameCounterSize         = 0x00 # Bit 6 (4 Byte)
frameAuxSecCon_Reserved                 = 0x00 # Bit 7

frameAuxSecCon = ( frameAuxSecCon_SecurityLevel |
                   frameAuxSecCon_KeyIdentifierMode |
                   frameAuxSecCon_FrameCounterSuppression |
                   frameAuxSecCon_FrameCounterSize |
                   frameAuxSecCon_Reserved )

dataFrame = [
    frameControlByte0,
    frameControlByte1, # Frame Control
    0x02, # Sequence number
    0x03, # Destination PanId
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

if(result):
    # Enable Transparant Mode Receiving DUT
    options = ( ftdf.FTDF_TRANSPARENT_PASS_ALL_PAN_ID )
    enable = True
    DTS_enableTransparantMode( devId2, enable, options )

    # Enable Transparant Mode Transmitting DUT
    options = ( ftdf.FTDF_TRANSPARENT_ENABLE_CSMA_CA |
                ftdf.FTDF_TRANSPARENT_ENABLE_FCS_GENERATION )
    enable = True
    DTS_enableTransparantMode( devId1, enable, options )

    length = len( dataFrame )
    channel = 11
    handle = 0 # Application can pas data using this handle to itself
    csmaSuppress = ftdf.FTDF_FALSE
    DTS_sendFrameTransparant( devId1, length, dataFrame, channel, csmaSuppress, handle )

    res, ret = DTS_getMsg( devId1, responseTimeout )
    if( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        result = False

    res, ret = DTS_getMsg( devId2, responseTimeout )
    if( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        result = False


# Test: FTDF_TRANSPARENT_PASS_ALL_ADDR
# Frame Control:
#frameControl_FrameType         = 0x0000 # Beacon
frameControl_FrameType          = 0x0001 # DataFrame
#frameControl_FrameType         = 0x0002 # Acknowledgment
#frameControl_FrameType         = 0x0003 # MAC command
#frameControl_FrameType         = 0x0004 # LLDN
#frameControl_FrameType         = 0x0005 # Multipurpose

#frameControl_SecurityEnabled   = 0x0008 # Bit: 3 (Yes)
frameControl_SecurityEnabled    = 0x0000 # Bit: 3 (No)

frameControl_FramePending       = 0x0000 # Bit: 4 (No)
#frameControl_FramePending      = 0x0010 # Bit: 4 (Yes)

#frameControl_AckReq            = 0x0020 # Bit: 5 (Yes)
frameControl_AckReq             = 0x0000 # Bit: 5 (No)

#frameControl_PANidCompression  = 0x0040 # Bit: 6 (Yes)
frameControl_PANidCompression   = 0x0000 # Bit: 6 (No)

#frameControl_SequenceNrSup     = 0x0100 # Bit: 8 (Yes) # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved
frameControl_SequenceNrSup      = 0x0000 # Bit: 8 (No)  # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved

#frameControl_IEListPresent     = 0x0200 # Bit: 9 (Yes) # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved
frameControl_IEListPresent      = 0x0000 # Bit: 9 (No) # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved

frameControl_dstAddrMode        = 0x0800 # Bit: 10-11 (Short)

#frameControl_FrameVersion      = 0x0000 # Bit: 12-13 (IEEE Std 802.15.4-2003)
frameControl_FrameVersion       = 0x1000 # Bit: 12-13 (IEEE Std 802.15.4-2006)
#frameControl_FrameVersion      = 0x2000 # Bit: 12-13 (IEEE Std 802.15.4)
#frameControl_FrameVersion      = 0x3000 # Bit: 12-13 (Reserved)

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
frameAuxSecCon_FrameCounterSuppression  = 0x00 # Bit 5 (No Suppression)
frameAuxSecCon_FrameCounterSize         = 0x00 # Bit 6 (4 Byte)
frameAuxSecCon_Reserved                 = 0x00 # Bit 7

frameAuxSecCon = ( frameAuxSecCon_SecurityLevel |
                   frameAuxSecCon_KeyIdentifierMode |
                   frameAuxSecCon_FrameCounterSuppression |
                   frameAuxSecCon_FrameCounterSize |
                   frameAuxSecCon_Reserved )

dataFrame = [
    frameControlByte0,
    frameControlByte1, # Frame Control
    0x03, # Sequence number
    0x01, # Destination PanId
    0x00,
    0x30, # Destination address
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

if(result):
    # Enable Transparant Mode Receiving DUT
    options = ( ftdf.FTDF_TRANSPARENT_PASS_ALL_ADDR )
    enable = True
    DTS_enableTransparantMode( devId2, enable, options )

    # Enable Transparant Mode Transmitting DUT
    options = ( ftdf.FTDF_TRANSPARENT_ENABLE_CSMA_CA |
                ftdf.FTDF_TRANSPARENT_ENABLE_FCS_GENERATION )
    enable = True
    DTS_enableTransparantMode( devId1, enable, options )

    length = len( dataFrame )
    channel = 11
    handle = 0 # Application can pas data using this handle to itself
    csmaSuppress = ftdf.FTDF_FALSE
    DTS_sendFrameTransparant( devId1, length, dataFrame, channel, csmaSuppress, handle )

    res, ret = DTS_getMsg( devId1, responseTimeout )
    if( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        result = False

    res, ret = DTS_getMsg( devId2, responseTimeout )
    if( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        result = False


# Test: FTDF_TRANSPARENT_PASS_ALL_NO_DEST_ADDR
#------------------------------- Data Frame:
# Frame Control:
#frameControl_FrameType         = 0x0000 # Beacon
frameControl_FrameType          = 0x0001 # DataFrame
#frameControl_FrameType         = 0x0002 # Acknowledgment
#frameControl_FrameType         = 0x0003 # MAC command
#frameControl_FrameType         = 0x0004 # LLDN
#frameControl_FrameType         = 0x0005 # Multipurpose

#frameControl_SecurityEnabled   = 0x0008 # Bit: 3 (Yes)
frameControl_SecurityEnabled    = 0x0000 # Bit: 3 (No)

frameControl_FramePending       = 0x0000 # Bit: 4 (No)
#frameControl_FramePending      = 0x0010 # Bit: 4 (Yes)

#frameControl_AckReq            = 0x0020 # Bit: 5 (Yes)
frameControl_AckReq             = 0x0000 # Bit: 5 (No)

#frameControl_PANidCompression  = 0x0040 # Bit: 6 (Yes)
frameControl_PANidCompression   = 0x0000 # Bit: 6 (No)

#frameControl_SequenceNrSup     = 0x0100 # Bit: 8 (Yes) # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved
frameControl_SequenceNrSup      = 0x0000 # Bit: 8 (No)  # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved

#frameControl_IEListPresent     = 0x0200 # Bit: 9 (Yes) # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved
frameControl_IEListPresent      = 0x0000 # Bit: 9 (No) # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved

frameControl_dstAddrMode        = 0x0000 # Bit: 10-11 (No Dest address and no Dest PANid)
#frameControl_dstAddrMode       = 0x0800 # Bit: 10-11 (Short)

#frameControl_FrameVersion      = 0x0000 # Bit: 12-13 (IEEE Std 802.15.4-2003)
frameControl_FrameVersion       = 0x1000 # Bit: 12-13 (IEEE Std 802.15.4-2006)
#frameControl_FrameVersion      = 0x2000 # Bit: 12-13 (IEEE Std 802.15.4)
#frameControl_FrameVersion      = 0x3000 # Bit: 12-13 (Reserved)

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
frameAuxSecCon_FrameCounterSuppression  = 0x00 # Bit 5 (No Suppression)
frameAuxSecCon_FrameCounterSize         = 0x00 # Bit 6 (4 Byte)
frameAuxSecCon_Reserved                 = 0x00 # Bit 7

frameAuxSecCon = ( frameAuxSecCon_SecurityLevel |
                   frameAuxSecCon_KeyIdentifierMode |
                   frameAuxSecCon_FrameCounterSuppression |
                   frameAuxSecCon_FrameCounterSize |
                   frameAuxSecCon_Reserved )

dataFrame = [
    frameControlByte0,
    frameControlByte1, # Frame Control
    0x04, # Sequence number
#    0x01, # Destination PanId
#    0x00,
#    0x20, # Destination address
#    0x00,
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

if(result):
    # Enable Transparant Mode Receiving DUT
    options = ( ftdf.FTDF_TRANSPARENT_PASS_ALL_NO_DEST_ADDR )
    enable = True
    DTS_enableTransparantMode( devId2, enable, options )

    # Enable Transparant Mode Transmitting DUT
    options = ( ftdf.FTDF_TRANSPARENT_ENABLE_CSMA_CA |
                ftdf.FTDF_TRANSPARENT_ENABLE_FCS_GENERATION )
    enable = True
    DTS_enableTransparantMode( devId1, enable, options )

    length = len( dataFrame )
    channel = 11
    handle = 0 # Application can pas data using this handle to itself
    csmaSuppress = ftdf.FTDF_FALSE
    DTS_sendFrameTransparant( devId1, length, dataFrame, channel, csmaSuppress, handle )

    res, ret = DTS_getMsg( devId1, responseTimeout )
    if( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        result = False

    res, ret = DTS_getMsg( devId2, responseTimeout )
    if( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        result = False


# Test: FTDF_TRANSPARENT_PASS_ALL_FRAME_VERSION
#------------------------------- Data Frame:
# Frame Control:
#frameControl_FrameType         = 0x0000 # Beacon
frameControl_FrameType          = 0x0001 # DataFrame
#frameControl_FrameType         = 0x0002 # Acknowledgment
#frameControl_FrameType         = 0x0003 # MAC command
#frameControl_FrameType         = 0x0004 # LLDN
#frameControl_FrameType         = 0x0005 # Multipurpose

#frameControl_SecurityEnabled   = 0x0008 # Bit: 3 (Yes)
frameControl_SecurityEnabled    = 0x0000 # Bit: 3 (No)

frameControl_FramePending       = 0x0000 # Bit: 4 (No)
#frameControl_FramePending      = 0x0010 # Bit: 4 (Yes)

#frameControl_AckReq            = 0x0020 # Bit: 5 (Yes)
frameControl_AckReq             = 0x0000 # Bit: 5 (No)

#frameControl_PANidCompression  = 0x0040 # Bit: 6 (Yes)
frameControl_PANidCompression   = 0x0000 # Bit: 6 (No)

#frameControl_SequenceNrSup     = 0x0100 # Bit: 8 (Yes) # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved
frameControl_SequenceNrSup      = 0x0000 # Bit: 8 (No)  # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved

#frameControl_IEListPresent     = 0x0200 # Bit: 9 (Yes) # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved
frameControl_IEListPresent      = 0x0000 # Bit: 9 (No) # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved

#frameControl_dstAddrMode       = 0x0000 # Bit: 10-11 (No Dest address and no Dest PANid)
frameControl_dstAddrMode        = 0x0800 # Bit: 10-11 (Short)

#frameControl_FrameVersion      = 0x0000 # Bit: 12-13 (IEEE Std 802.15.4-2003)
#frameControl_FrameVersion      = 0x1000 # Bit: 12-13 (IEEE Std 802.15.4-2006)
#frameControl_FrameVersion      = 0x2000 # Bit: 12-13 (IEEE Std 802.15.4)
frameControl_FrameVersion       = 0x3000 # Bit: 12-13 (Reserved)

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
frameAuxSecCon_FrameCounterSuppression  = 0x00 # Bit 5 (No Suppression)
frameAuxSecCon_FrameCounterSize         = 0x00 # Bit 6 (4 Byte)
frameAuxSecCon_Reserved                 = 0x00 # Bit 7

frameAuxSecCon = ( frameAuxSecCon_SecurityLevel |
                   frameAuxSecCon_KeyIdentifierMode |
                   frameAuxSecCon_FrameCounterSuppression |
                   frameAuxSecCon_FrameCounterSize |
                   frameAuxSecCon_Reserved )

dataFrame = [
    frameControlByte0,
    frameControlByte1, # Frame Control
    0x05, # Sequence number
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

if(result):
    # Enable Transparant Mode Receiving DUT
    options = ( ftdf.FTDF_TRANSPARENT_PASS_ALL_FRAME_VERSION )
    enable = True
    DTS_enableTransparantMode( devId2, enable, options )

    # Enable Transparant Mode Transmitting DUT
    options = ( ftdf.FTDF_TRANSPARENT_ENABLE_CSMA_CA |
                ftdf.FTDF_TRANSPARENT_ENABLE_FCS_GENERATION )
    enable = True
    DTS_enableTransparantMode( devId1, enable, options )

    length = len( dataFrame )
    channel = 11
    handle = 0 # Application can pas data using this handle to itself
    csmaSuppress = ftdf.FTDF_FALSE
    DTS_sendFrameTransparant( devId1, length, dataFrame, channel, csmaSuppress, handle )

    res, ret = DTS_getMsg( devId1, responseTimeout )

    res, ret = DTS_getMsg( devId2, responseTimeout )
    if( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        result = False


# Test: PassNonSupportedFrameTypes:
#           FTDF_TRANSPARENT_PASS_FRAME_TYPE_4
#           FTDF_TRANSPARENT_PASS_FRAME_TYPE_6
#           FTDF_TRANSPARENT_PASS_FRAME_TYPE_7
#------------------------------- Data Frame:
# Frame Control:
#frameControl_FrameType         = 0x0000 # Beacon
#frameControl_FrameType         = 0x0001 # DataFrame
#frameControl_FrameType         = 0x0002 # Acknowledgment
#frameControl_FrameType         = 0x0003 # MAC command
frameControl_FrameType          = 0x0004 # LLDN
#frameControl_FrameType         = 0x0005 # Multipurpose
#frameControl_FrameType         = 0x0006 # Reserved
#frameControl_FrameType         = 0x0007 # Reserved

#frameControl_SecurityEnabled   = 0x0008 # Bit: 3 (Yes)
frameControl_SecurityEnabled    = 0x0000 # Bit: 3 (No)

frameControl_FramePending       = 0x0000 # Bit: 4 (No)
#frameControl_FramePending      = 0x0010 # Bit: 4 (Yes)

#frameControl_AckReq            = 0x0020 # Bit: 5 (Yes)
frameControl_AckReq             = 0x0000 # Bit: 5 (No)

#frameControl_PANidCompression  = 0x0040 # Bit: 6 (Yes)
frameControl_PANidCompression   = 0x0000 # Bit: 6 (No)

#frameControl_SequenceNrSup     = 0x0100 # Bit: 8 (Yes) # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved
frameControl_SequenceNrSup      = 0x0000 # Bit: 8 (No)  # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved

#frameControl_IEListPresent     = 0x0200 # Bit: 9 (Yes) # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved
frameControl_IEListPresent      = 0x0000 # Bit: 9 (No) # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved

#frameControl_dstAddrMode       = 0x0000 # Bit: 10-11 (No Dest address and no Dest PANid)
frameControl_dstAddrMode        = 0x0800 # Bit: 10-11 (Short)

#frameControl_FrameVersion      = 0x0000 # Bit: 12-13 (IEEE Std 802.15.4-2003)
frameControl_FrameVersion       = 0x1000 # Bit: 12-13 (IEEE Std 802.15.4-2006)
#frameControl_FrameVersion      = 0x2000 # Bit: 12-13 (IEEE Std 802.15.4)
#frameControl_FrameVersion      = 0x3000 # Bit: 12-13 (Reserved)

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
frameAuxSecCon_FrameCounterSuppression  = 0x00 # Bit 5 (No Suppression)
frameAuxSecCon_FrameCounterSize         = 0x00 # Bit 6 (4 Byte)
frameAuxSecCon_Reserved                 = 0x00 # Bit 7

frameAuxSecCon = ( frameAuxSecCon_SecurityLevel |
                   frameAuxSecCon_KeyIdentifierMode |
                   frameAuxSecCon_FrameCounterSuppression |
                   frameAuxSecCon_FrameCounterSize |
                   frameAuxSecCon_Reserved )

dataFrame_v_4 = [
    frameControlByte0,
    frameControlByte1, # Frame Control
    0x06, # Sequence number
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

# Frame Control:
#frameControl_FrameType         = 0x0000 # Beacon
#frameControl_FrameType         = 0x0001 # DataFrame
#frameControl_FrameType         = 0x0002 # Acknowledgment
#frameControl_FrameType         = 0x0003 # MAC command
#frameControl_FrameType         = 0x0004 # LLDN
#frameControl_FrameType         = 0x0005 # Multipurpose
frameControl_FrameType          = 0x0006 # Reserved
#frameControl_FrameType         = 0x0007 # Reserved

#frameControl_SecurityEnabled   = 0x0008 # Bit: 3 (Yes)
frameControl_SecurityEnabled    = 0x0000 # Bit: 3 (No)

frameControl_FramePending       = 0x0000 # Bit: 4 (No)
#frameControl_FramePending      = 0x0010 # Bit: 4 (Yes)

#frameControl_AckReq            = 0x0020 # Bit: 5 (Yes)
frameControl_AckReq             = 0x0000 # Bit: 5 (No)

#frameControl_PANidCompression  = 0x0040 # Bit: 6 (Yes)
frameControl_PANidCompression   = 0x0000 # Bit: 6 (No)

#frameControl_SequenceNrSup     = 0x0100 # Bit: 8 (Yes) # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved
frameControl_SequenceNrSup      = 0x0000 # Bit: 8 (No)  # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved

#frameControl_IEListPresent     = 0x0200 # Bit: 9 (Yes) # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved
frameControl_IEListPresent      = 0x0000 # Bit: 9 (No) # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved

#frameControl_dstAddrMode       = 0x0000 # Bit: 10-11 (No Dest address and no Dest PANid)
frameControl_dstAddrMode        = 0x0800 # Bit: 10-11 (Short)

#frameControl_FrameVersion      = 0x0000 # Bit: 12-13 (IEEE Std 802.15.4-2003)
frameControl_FrameVersion       = 0x1000 # Bit: 12-13 (IEEE Std 802.15.4-2006)
#frameControl_FrameVersion      = 0x2000 # Bit: 12-13 (IEEE Std 802.15.4)
#frameControl_FrameVersion      = 0x3000 # Bit: 12-13 (Reserved)

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
frameAuxSecCon_FrameCounterSuppression  = 0x00 # Bit 5 (No Suppression)
frameAuxSecCon_FrameCounterSize         = 0x00 # Bit 6 (4 Byte)
frameAuxSecCon_Reserved                 = 0x00 # Bit 7

frameAuxSecCon = ( frameAuxSecCon_SecurityLevel |
                   frameAuxSecCon_KeyIdentifierMode |
                   frameAuxSecCon_FrameCounterSuppression |
                   frameAuxSecCon_FrameCounterSize |
                   frameAuxSecCon_Reserved )

dataFrame_v_6 = [
    frameControlByte0,
    frameControlByte1, # Frame Control
    0x07, # Sequence number
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

# Frame Control:
#frameControl_FrameType         = 0x0000 # Beacon
#frameControl_FrameType         = 0x0001 # DataFrame
#frameControl_FrameType         = 0x0002 # Acknowledgment
#frameControl_FrameType         = 0x0003 # MAC command
#frameControl_FrameType         = 0x0004 # LLDN
#frameControl_FrameType         = 0x0005 # Multipurpose
#frameControl_FrameType         = 0x0006 # Reserved
frameControl_FrameType          = 0x0007 # Reserved

#frameControl_SecurityEnabled   = 0x0008 # Bit: 3 (Yes)
frameControl_SecurityEnabled    = 0x0000 # Bit: 3 (No)

frameControl_FramePending       = 0x0000 # Bit: 4 (No)
#frameControl_FramePending      = 0x0010 # Bit: 4 (Yes)

#frameControl_AckReq            = 0x0020 # Bit: 5 (Yes)
frameControl_AckReq             = 0x0000 # Bit: 5 (No)

#frameControl_PANidCompression  = 0x0040 # Bit: 6 (Yes)
frameControl_PANidCompression   = 0x0000 # Bit: 6 (No)

#frameControl_SequenceNrSup     = 0x0100 # Bit: 8 (Yes) # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved
frameControl_SequenceNrSup      = 0x0000 # Bit: 8 (No)  # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved

#frameControl_IEListPresent     = 0x0200 # Bit: 9 (Yes) # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved
frameControl_IEListPresent      = 0x0000 # Bit: 9 (No) # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved

#frameControl_dstAddrMode       = 0x0000 # Bit: 10-11 (No Dest address and no Dest PANid)
frameControl_dstAddrMode        = 0x0800 # Bit: 10-11 (Short)

#frameControl_FrameVersion      = 0x0000 # Bit: 12-13 (IEEE Std 802.15.4-2003)
frameControl_FrameVersion       = 0x1000 # Bit: 12-13 (IEEE Std 802.15.4-2006)
#frameControl_FrameVersion      = 0x2000 # Bit: 12-13 (IEEE Std 802.15.4)
#frameControl_FrameVersion      = 0x3000 # Bit: 12-13 (Reserved)

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
frameAuxSecCon_FrameCounterSuppression  = 0x00 # Bit 5 (No Suppression)
frameAuxSecCon_FrameCounterSize         = 0x00 # Bit 6 (4 Byte)
frameAuxSecCon_Reserved                 = 0x00 # Bit 7

frameAuxSecCon = ( frameAuxSecCon_SecurityLevel |
                   frameAuxSecCon_KeyIdentifierMode |
                   frameAuxSecCon_FrameCounterSuppression |
                   frameAuxSecCon_FrameCounterSize |
                   frameAuxSecCon_Reserved )

dataFrame_v_7 = [
    frameControlByte0,
    frameControlByte1, # Frame Control
    0x08, # Sequence number
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

if(result):
    # Enable Transparant Mode Receiving DUT
    options = ( ftdf.FTDF_TRANSPARENT_PASS_FRAME_TYPE_4 |
                ftdf.FTDF_TRANSPARENT_PASS_FRAME_TYPE_6 |
                ftdf.FTDF_TRANSPARENT_PASS_FRAME_TYPE_7 )
    enable = True
    DTS_enableTransparantMode( devId2, enable, options )

    # Enable Transparant Mode Transmitting DUT
    options = ( ftdf.FTDF_TRANSPARENT_ENABLE_CSMA_CA |
                ftdf.FTDF_TRANSPARENT_ENABLE_FCS_GENERATION )
    enable = True
    DTS_enableTransparantMode( devId1, enable, options )

    length = len( dataFrame_v_4 )
    channel = 11
    handle = 0 # Application can pas data using this handle to itself
    csmaSuppress = ftdf.FTDF_FALSE
    DTS_sendFrameTransparant( devId1, length, dataFrame_v_4, channel, csmaSuppress, handle )

    res, ret = DTS_getMsg( devId1, responseTimeout )
    res, ret = DTS_getMsg( devId2, responseTimeout )
    if( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        result = False

if(result):
    length = len( dataFrame_v_6 )
    channel = 11
    handle = 0 # Application can pas data using this handle to itself
    csmaSuppress = ftdf.FTDF_FALSE
    DTS_sendFrameTransparant( devId1, length, dataFrame_v_6, channel, csmaSuppress, handle )

    res, ret = DTS_getMsg( devId1, responseTimeout )
    res, ret = DTS_getMsg( devId2, responseTimeout )
    if( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        result = False

if(result):
    length = len( dataFrame_v_7 )
    channel = 11
    handle = 0 # Application can pas data using this handle to itself
    csmaSuppress = ftdf.FTDF_FALSE
    DTS_sendFrameTransparant( devId1, length, dataFrame_v_7, channel, csmaSuppress, handle )

    res, ret = DTS_getMsg( devId1, responseTimeout )
    res, ret = DTS_getMsg( devId2, responseTimeout )
    if( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        result = False

# Test duplicate frames
if (result):
    length = len( dataFrame_v_7 )
    channel = 11
    handle = 0
    csmaSuppress = ftdf.FTDF_FALSE

    # send frame 5 times to check if it is not being dropped due to duplication error
    for i in range( 5 ):
        DTS_sendFrameTransparant( devId1, length, dataFrame_v_7, channel, csmaSuppress, handle )

        res1, ret1 = DTS_getMsg( devId1, responseTimeout )
        res2, ret2 = DTS_getMsg( devId2, responseTimeout )
        if( res1 == False or res2 == False ):
            raise StopScript( 'SCRIPT: ERROR: No response received from device' )
            result = False



if( not result ):
    raise StopScript('SCRIPT: FAILED')
