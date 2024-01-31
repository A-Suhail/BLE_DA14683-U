# Load-drop 2 Test: Security
#

import sys  #cli arguments
import time  #sleep

from scriptIncludes import *

# Message order
msgFlow = (
  devId1, msgRESET, ftdf.FTDF_RESET_CONFIRM,
  devId2, msgRESET, ftdf.FTDF_RESET_CONFIRM,

  devId1, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
  devId2, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,

  devId1, msgSET_Dev1_ShortAddress, ftdf.FTDF_SET_CONFIRM,
  devId2, msgSET_Dev2_ShortAddress, ftdf.FTDF_SET_CONFIRM,

  devId1, msgRxEnable_On, ftdf.FTDF_RX_ENABLE_CONFIRM,
  devId2, msgRxEnable_On, ftdf.FTDF_RX_ENABLE_CONFIRM )


idx = 0
result = True
maxFrameRetries = 0
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


#------------------------------- Data Frame:
dns = 0xAB # Sequence number

# Frame Control:
#frameControl_FrameType      = 0x0000 # Beacon
frameControl_FrameType      = 0x0001 # DataFrame
#frameControl_FrameType      = 0x0002 # Acknowledgment
#frameControl_FrameType      = 0x0003 # MAC command
#frameControl_FrameType      = 0x0004 # LLDN
#frameControl_FrameType      = 0x0005 # Multipurpose

#frameControl_SecurityEnabled  = 0x0008 # Bit: 3 (Yes)
frameControl_SecurityEnabled  = 0x0000 # Bit: 3 (No)

frameControl_FramePending    = 0x0000 # Bit: 4 (No)
#frameControl_FramePending    = 0x0010 # Bit: 4 (Yes)

frameControl_AckReq        = 0x0020 # Bit: 5 (Yes)
#frameControl_AckReq      = 0x0000 # Bit: 5 (No)

#frameControl_PANidCompression  = 0x0040 # Bit: 6 (Yes)
frameControl_PANidCompression  = 0x0000 # Bit: 6 (No)

#frameControl_SequenceNrSup    = 0x0100 # Bit: 8 (Yes) # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved
frameControl_SequenceNrSup    = 0x0000 # Bit: 8 (No)  # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved

#frameControl_IEListPresent    = 0x0200 # Bit: 9 (Yes) # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved
frameControl_IEListPresent    = 0x0000 # Bit: 9 (No) # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved

frameControl_dstAddrMode    = 0x0800 # Bit: 10-11 (Short)

#frameControl_FrameVersion    = 0x0000 # Bit: 12-13 (IEEE Std 802.15.4-2003)
#frameControl_FrameVersion    = 0x1000 # Bit: 12-13 (IEEE Std 802.15.4-2006)
frameControl_FrameVersion    = 0x2000 # Bit: 12-13 (IEEE Std 802.15.4)
#frameControl_FrameVersion    = 0x3000 # Bit: 12-13 (Reserved)

frameControl_srcAddrMode    = 0x8000 # Bit: 14-15 (Short)

frameControl = ( frameControl_FrameType |
         frameControl_SecurityEnabled |
         frameControl_FramePending |
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
frameAuxSecCon_SecurityLevel      = 0x00 # Bit 0-2 (Tip: using 4 disables the use of MIC (the need to calculate and add the association bytes in the transparent send frame))
frameAuxSecCon_KeyIdentifierMode    = 0x18 # Bit 3-4
frameAuxSecCon_FrameCounterSuppression  = 0x00 # Bit 5 (No Suppression)
frameAuxSecCon_FrameCounterSize      = 0x00 # Bit 6 (4 Byte)
frameAuxSecCon_Reserved          = 0x00 # Bit 7

frameAuxSecCon = (  frameAuxSecCon_SecurityLevel |
          frameAuxSecCon_KeyIdentifierMode |
          frameAuxSecCon_FrameCounterSuppression |
          frameAuxSecCon_FrameCounterSize |
          frameAuxSecCon_Reserved )

dataFrame_1 = [
  frameControlByte0,
  frameControlByte1, # Frame Control
  dns, # Sequence number
  0x01, # Destination PanId
  0x00,
  0x20, # Destination address
  0x00,
#  0x01, # Source PanId # Frame version2 never has Source PanId 
#  0x00,
  0x10, # Source address
  0x00,
#  frameAuxSecCon, # Auxiliary security header: Security Control
#  0x00, # Auxiliary security header: Frame Counter (4 Byte)
#  0x00,
#  0x00,
#  0x01,
#  0x08, # Key Source (8 Byte)
#  0x09,
#  0x0a,
#  0x0b,
#  0x0c,
#  0x0d,
#  0x0e,
#  0x0f,
#  0x05, # Key Index
  0xFF, # Payload
  0xFF, # MIC32 or just extra payload
  0xFF,
  0xFF,
  0xFF,
  0x00, # FCS
  0x00
]

# Frame Control:
#frameControl_FrameType      = 0x0000 # Beacon
frameControl_FrameType      = 0x0001 # DataFrame
#frameControl_FrameType      = 0x0002 # Acknowledgment
#frameControl_FrameType      = 0x0003 # MAC command
#frameControl_FrameType      = 0x0004 # LLDN
#frameControl_FrameType      = 0x0005 # Multipurpose

#frameControl_SecurityEnabled  = 0x0008 # Bit: 3 (Yes)
frameControl_SecurityEnabled  = 0x0000 # Bit: 3 (No)

frameControl_FramePending    = 0x0000 # Bit: 4 (No)
#frameControl_FramePending    = 0x0010 # Bit: 4 (Yes)

frameControl_AckReq        = 0x0020 # Bit: 5 (Yes)
#frameControl_AckReq      = 0x0000 # Bit: 5 (No)

#frameControl_PANidCompression  = 0x0040 # Bit: 6 (Yes)
frameControl_PANidCompression  = 0x0000 # Bit: 6 (No)

frameControl_SequenceNrSup    = 0x0100 # Bit: 8 (Yes) # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved
#frameControl_SequenceNrSup    = 0x0000 # Bit: 8 (No)  # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved

#frameControl_IEListPresent    = 0x0200 # Bit: 9 (Yes) # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved
frameControl_IEListPresent    = 0x0000 # Bit: 9 (No) # Only applicable FrameVersion=IEEE Std 802.15.4 or FrameVersion=Reserved

frameControl_dstAddrMode    = 0x0800 # Bit: 10-11 (Short)

#frameControl_FrameVersion    = 0x0000 # Bit: 12-13 (IEEE Std 802.15.4-2003)
#frameControl_FrameVersion    = 0x1000 # Bit: 12-13 (IEEE Std 802.15.4-2006)
frameControl_FrameVersion    = 0x2000 # Bit: 12-13 (IEEE Std 802.15.4)
#frameControl_FrameVersion    = 0x3000 # Bit: 12-13 (Reserved)

frameControl_srcAddrMode    = 0x8000 # Bit: 14-15 (Short)

frameControl = ( frameControl_FrameType |
         frameControl_SecurityEnabled |
         frameControl_FramePending |
         frameControl_AckReq |
         frameControl_PANidCompression |
         frameControl_SequenceNrSup |
         frameControl_IEListPresent |
         frameControl_dstAddrMode |
         frameControl_FrameVersion |
         frameControl_srcAddrMode )

dataFrame_2 = [
  frameControlByte0,
  frameControlByte1+3, # Frame Control
  #dns, # Sequence number
  0x01, # Destination PanId
  0x00,
  0x20, # Destination address
  0x00,
#  0x01, # Source PanId # Frame version2 never has Source PanId 
#  0x00,
  0x10, # Source address
  0x00,
#  frameAuxSecCon, # Auxiliary security header: Security Control
#  0x00, # Auxiliary security header: Frame Counter (4 Byte)
#  0x00,
#  0x00,
#  0x01,
#  0x08, # Key Source (8 Byte)
#  0x09,
#  0x0a,
#  0x0b,
#  0x0c,
#  0x0d,
#  0x0e,
#  0x0f,
#  0x05, # Key Index
  0xFF, # Payload
  0xFF, # MIC32 or just extra payload
  0xFF,
  0xFF,
  0xFF,
  0x00, # FCS
  0x00
]

# TEST: Ehn Ack sequence number is copyed from received frame
if(result):
  # Enable Transparant Mode Transmitting DUT
  options = ( ftdf.FTDF_TRANSPARENT_PASS_ALL_FRAME_TYPES |
        ftdf.FTDF_TRANSPARENT_ENABLE_FCS_GENERATION |
        ftdf.FTDF_TRANSPARENT_ENABLE_CSMA_CA )
  enable = True
  DTS_enableTransparantMode( devId1, enable, options )

  length = len( dataFrame_1 )
  channel = 11
  handle = 0 # Application can pas data using this handle to itself
  csmaSuppress = ftdf.FTDF_FALSE
  DTS_sendFrameTransparant( devId1, length, dataFrame_1, channel, csmaSuppress, handle )

  res, ret = DTS_getMsg( devId2, responseTimeout )
  if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    result = False

if(result):
  res, ret = DTS_getMsg( devId1, responseTimeout )
  if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    result = False
  elif ret['msgId'] != ftdf.FTDF_TRANSPARENT_CONFIRM:
    logstr = ( 'SCRIPT: ERROR: Expected ftdf.FTDF_TRANSPARENT_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )
    result = False
  else:
    res, ret = DTS_getMsg( devId1, responseTimeout )
    if( res == False ):
      raise StopScript( 'SCRIPT: ERROR: No response received from device' )
      result = False
    elif ret['msgId'] != ftdf.FTDF_TRANSPARENT_INDICATION:
      logstr = ( 'SCRIPT: ERROR: Expected ftdf.FTDF_TRANSPARENT_INDICATION confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
      raise StopScript( ''.join( map( str, logstr ) ) )
      result = False
    else:
      # Check if Ack frame has the same DNS as the send data frame
      if( ret['frame'][2] != dns ):
        logstr = ( 'SCRIPT: ERROR: Expected DNS', dns, 'instead received: ', ret['frame'][2] )
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False
      elif( ret['frame'][1] != 0x20 ):
        raise StopScript( 'SCRIPT: ERROR: received frame no enhanced Acknowledgment frame' )
        result = False
      else:
        # Check received frame
        expectedFrame = [2, 32, 171, 82, 141]

        # Print received frame
        idx2 = 0
        while( idx2 < len( ret['frame'] ) ):
          idx2+=1

        # Check frame length
        if( len( expectedFrame ) != len( ret['frame'] ) ):
          raise StopScript( 'SCRIPT: ERROR: frame length incorrect' )
          result = False
        # Check frame bytes
        else:
          idx2 = 0
          while( idx2 < len( expectedFrame ) ):
            if( expectedFrame[idx2] != ret['frame'][idx2] ):
              logstr = ( 'SCRIPT: ERROR: frame byte number:', idx2, 'incorrect' )
              raise StopScript( ''.join( map( str, logstr ) ) )
              result = False
            idx2+=1


# TEST: SequenceNrSup in received frame sets SequenceNrSup in Enh Ack to
if(result):
  length = len( dataFrame_2 )
  channel = 11
  handle = 0 # Application can pas data using this handle to itself
  csmaSuppress = ftdf.FTDF_FALSE
  DTS_sendFrameTransparant( devId1, length, dataFrame_2, channel, csmaSuppress, handle )

  res, ret = DTS_getMsg( devId2, responseTimeout )
  if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device1' )
    result = False

if(result):
  res, ret = DTS_getMsg( devId1, responseTimeout )
  if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device2' )
    result = False
  elif ret['msgId'] != ftdf.FTDF_TRANSPARENT_CONFIRM:
    logstr = ( 'SCRIPT: ERROR: Expected ftdf.FTDF_TRANSPARENT_CONFIRM confirm, instead received ', ret['msgId'])
    raise StopScript( ''.join( map( str, logstr ) ) )
    result = False
  else:
    res, ret = DTS_getMsg( devId1, responseTimeout )
    if( res == False ):
      raise StopScript( 'SCRIPT: ERROR: No response received from device3' )
      result = False
    elif ret['msgId'] != ftdf.FTDF_TRANSPARENT_INDICATION:
      logstr = ( 'SCRIPT: ERROR: Expected ftdf.FTDF_TRANSPARENT_INDICATION confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
      raise StopScript( ''.join( map( str, logstr ) ) )
      result = False
    
if ( not result ):
    raise StopScript('SCRIPT: FAILED')
