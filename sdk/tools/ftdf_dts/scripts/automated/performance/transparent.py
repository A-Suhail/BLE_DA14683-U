import sys, datetime
from scriptIncludes import *

nrOfFrames = 10000

msgSET_rxOnWhenIdle = { 'msgId': ftdf.FTDF_SET_REQUEST,
                        'PIBAttribute': ftdf.FTDF_PIB_RX_ON_WHEN_IDLE,
                        'PIBAttributeValue': True }

# Message order
msgFlow = ( devId1, msgRESET, ftdf.FTDF_RESET_CONFIRM,
            devId2, msgRESET, ftdf.FTDF_RESET_CONFIRM,

            devId1, msgSET_Dev1_ShortAddress, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_Dev2_ShortAddress, ftdf.FTDF_SET_CONFIRM,

            devId1, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,

            devId2, msgSET_rxOnWhenIdle, ftdf.FTDF_SET_CONFIRM )

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
DTS_enableTransparantMode( devId1, True, ftdf.FTDF_TRANSPARENT_ENABLE_FCS_GENERATION )

# Prepare transparent frame
fc_frameType    = 0x0001 # dataframe
fc_ackRequest   = 0x0000 # unacknowledged
fc_dstAddrMode  = 0x0800 # short
fc_frameVersion = 0x1000 # 2006
fc_srcAddrMode  = 0x8000 # short

frameControl = ( fc_frameType | fc_ackRequest | fc_dstAddrMode | fc_frameVersion | fc_srcAddrMode )

fc_byte0 = frameControl & 0xff
fc_byte1 = frameControl >> 8


logmsg = 'Transparent performance (unacknowledged):\n'
####################################
# 32
####################################
logmsg = logmsg + 'Frame size 32 : '


dataframe = [
    fc_byte0,
    fc_byte1,
    0xaa, # SN
    0x01, # dst PAN ID
    0x00,
    0x20, # dest addr
    0x00,
    0x01, # src PAN ID
    0x00,
    0x10, # src addr
    0x00
]

# Payload
for i in range( 19 ):
    dataframe.append( i )

# FCS
for i in range( 2 ):
    dataframe.append( 0x00 )


DTS_setQueueParameters( devId1,
                       ftdf.DTS_QUEUE_SND,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       nrOfFrames - 1, 0 )

DTS_sendFrameTransparant( devId1, len( dataframe ), dataframe, 11, True, 0 )

# Get current time
t1 = datetime.datetime.now( )

# start sending of frames
DTS_setQueueEnable( devId1, True )

# Since device 2 is not in queueing mode, 1 data frame is expected
# The rest of the frames is expected to be dropped by sequence nr duplication
res, ret = DTS_getMsg( devId2, responseTimeout )

if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgId'] != ftdf.FTDF_DATA_INDICATION:
    raise StopScript( 'Expected data indication' )


res, ret = DTS_getMsg( devId1, 100 )

if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgTotal'] != nrOfFrames:
    raise StopScript( 'Expected ' + str(nrOfFrames) + ' sent messages' )
elif ret['msgSuccess'] != nrOfFrames:
    raise StopScript( 'Expected ' + str(nrOfFrames) + ' successful messages' )


# get time after end of test
t2 = datetime.datetime.now( )
deltat = t2 - t1
fps = nrOfFrames / deltat.total_seconds()

logmsg = logmsg + str(nrOfFrames) + ' frames in ' + str( deltat.total_seconds() ) +\
         ' seconds (' + str(int(fps)) + ' frames per second)\n'



####################################
# 64
####################################
logmsg = logmsg + 'Frame size 64 : '


dataframe = [
    fc_byte0,
    fc_byte1,
    0xbb, # SN
    0x01, # dst PAN ID
    0x00,
    0x20, # dest addr
    0x00,
    0x01, # src PAN ID
    0x00,
    0x10, # src addr
    0x00
]

# Payload
for i in range( 51 ):
    dataframe.append( i )

# FCS
for i in range( 2 ):
    dataframe.append( 0x00 )


DTS_setQueueParameters( devId1,
                       ftdf.DTS_QUEUE_SND,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       nrOfFrames - 1, 0 )

DTS_sendFrameTransparant( devId1, len( dataframe ), dataframe, 11, True, 0 )

# Get current time
t1 = datetime.datetime.now( )

# start sending of frames
DTS_setQueueEnable( devId1, True )

# Since device 2 is not in queueing mode, 1 data frame is expected
# The rest of the frames is expected to be dropped by sequence nr duplication
res, ret = DTS_getMsg( devId2, responseTimeout )

if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgId'] != ftdf.FTDF_DATA_INDICATION:
    raise StopScript( 'Expected data indication' )


res, ret = DTS_getMsg( devId1, 100 )

if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgTotal'] != nrOfFrames:
    raise StopScript( 'Expected ' + str(nrOfFrames) + ' sent messages' )
elif ret['msgSuccess'] != nrOfFrames:
    raise StopScript( 'Expected ' + str(nrOfFrames) + ' successful messages' )


# get time after end of test
t2 = datetime.datetime.now( )
deltat = t2 - t1
fps = nrOfFrames / deltat.total_seconds()

logmsg = logmsg + str(nrOfFrames) + ' frames in ' + str( deltat.total_seconds() ) +\
         ' seconds (' + str(int(fps)) + ' frames per second)\n'



####################################
# 127
####################################
logmsg = logmsg + 'Frame size 127: '


dataframe = [
    fc_byte0,
    fc_byte1,
    0xcc, # SN
    0x01, # dst PAN ID
    0x00,
    0x20, # dest addr
    0x00,
    0x01, # src PAN ID
    0x00,
    0x10, # src addr
    0x00
]

# Payload
for i in range( 114 ):
    dataframe.append( i )

# FCS
for i in range( 2 ):
    dataframe.append( 0x00 )


DTS_setQueueParameters( devId1,
                       ftdf.DTS_QUEUE_SND,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       nrOfFrames - 1, 0 )

DTS_sendFrameTransparant( devId1, len( dataframe ), dataframe, 11, True, 0 )

# Get current time
t1 = datetime.datetime.now( )

# start sending of frames
DTS_setQueueEnable( devId1, True )

# Since device 2 is not in queueing mode, 1 data frame is expected
# The rest of the frames is expected to be dropped by sequence nr duplication
res, ret = DTS_getMsg( devId2, responseTimeout )

if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgId'] != ftdf.FTDF_DATA_INDICATION:
    raise StopScript( 'Expected data indication' )


res, ret = DTS_getMsg( devId1, 100 )

if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgTotal'] != nrOfFrames:
    raise StopScript( 'Expected ' + str(nrOfFrames) + ' sent messages' )
elif ret['msgSuccess'] != nrOfFrames:
    raise StopScript( 'Expected ' + str(nrOfFrames) + ' successful messages' )


# get time after end of test
t2 = datetime.datetime.now( )
deltat = t2 - t1
fps = nrOfFrames / deltat.total_seconds()

logmsg = logmsg + str(nrOfFrames) + ' frames in ' + str( deltat.total_seconds() ) +\
         ' seconds (' + str(int(fps)) + ' frames per second)\n'


# Return performance results via exception
raise PerformanceResults( logmsg )
