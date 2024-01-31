import sys, datetime, time
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



logmsg = 'Normal unsecure performance (acknowledged):\n'
####################################
# 11 + 16
####################################
logmsg = logmsg + 'Frame size 11 + 16 : '

msdu = []
for i in range( 16 ):
    msdu.append( i )

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

DTS_setQueueParameters( devId1,
                       ftdf.DTS_QUEUE_SND,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       nrOfFrames - 1, 0 )

DTS_setQueueParameters( devId2,
                       ftdf.DTS_QUEUE_RCV,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       0, 0 )

DTS_sndMsg( devId1, msgDATA )

# Get current time
t1 = datetime.datetime.now( )

# start sending of frames
DTS_setQueueEnable( devId1, True )

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

time.sleep(2)

DTS_setQueueParameters( devId2,
                       ftdf.DTS_QUEUE_DIS,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       0, 0 )

res, ret = DTS_getMsg( devId2, responseTimeout )

if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgTotal'] != nrOfFrames:
    dtsLog.warning( 'Expected ' + str(nrOfFrames) + ' rcvd messages' )
elif ret['msgSuccess'] != nrOfFrames:
    dtsLog.warning( 'Expected ' + str(nrOfFrames) + ' successful messages' )




####################################
# 11 + 64
####################################
logmsg = logmsg + 'Frame size 11 + 64 : '

msdu = []
for i in range( 64 ):
    msdu.append( i )

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

DTS_setQueueParameters( devId1,
                       ftdf.DTS_QUEUE_SND,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       nrOfFrames - 1, 0 )

DTS_setQueueParameters( devId2,
                       ftdf.DTS_QUEUE_RCV,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       0, 0 )

DTS_sndMsg( devId1, msgDATA )

# Get current time
t1 = datetime.datetime.now( )

# start sending of 1000 frames
DTS_setQueueEnable( devId1, True )

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

time.sleep(2)

DTS_setQueueParameters( devId2,
                       ftdf.DTS_QUEUE_DIS,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       0, 0 )

res, ret = DTS_getMsg( devId2, responseTimeout )

if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgTotal'] != nrOfFrames:
    dtsLog.warning( 'Expected ' + str(nrOfFrames) + ' rcvd messages' )
elif ret['msgSuccess'] != nrOfFrames:
    dtsLog.warning( 'Expected ' + str(nrOfFrames) + ' successful messages' )



####################################
# 11 + 116
####################################
logmsg = logmsg + 'Frame size 11 + 116: '

msdu = []
for i in range( 116 ):
    msdu.append( i )

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

DTS_setQueueParameters( devId1,
                       ftdf.DTS_QUEUE_SND,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       nrOfFrames - 1, 0 )

DTS_setQueueParameters( devId2,
                       ftdf.DTS_QUEUE_RCV,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       0, 0 )

DTS_sndMsg( devId1, msgDATA )

# Get current time
t1 = datetime.datetime.now( )

# start sending of 1000 frames
DTS_setQueueEnable( devId1, True )

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

time.sleep(2)

DTS_setQueueParameters( devId2,
                       ftdf.DTS_QUEUE_DIS,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       0, 0 )

res, ret = DTS_getMsg( devId2, responseTimeout )

if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgTotal'] != nrOfFrames:
    dtsLog.warning( 'Expected ' + str(nrOfFrames) + ' rcvd messages' )
elif ret['msgSuccess'] != nrOfFrames:
    dtsLog.warning( 'Expected ' + str(nrOfFrames) + ' successful messages' )


logmsg = logmsg + '\nNormal unsecure performance (unacknowledged):\n'
####################################
# 11 + 16
####################################
logmsg = logmsg + 'Frame size 11 + 16 : '

msdu = []
for i in range( 16 ):
    msdu.append( i )

msgDATA = {
    'msgId': ftdf.FTDF_DATA_REQUEST,
    'srcAddrMode': ftdf.FTDF_SHORT_ADDRESS,
    'dstAddrMode': ftdf.FTDF_SHORT_ADDRESS,
    'dstPANId': 0x0001,
    'dstAddr': 0x0020,
    'msduLength': len( msdu ),
    'msdu': msdu,
    'msduHandle': 1,
    'ackTX': False,
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

DTS_setQueueParameters( devId1,
                       ftdf.DTS_QUEUE_SND,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       nrOfFrames - 1, 0 )

DTS_setQueueParameters( devId2,
                       ftdf.DTS_QUEUE_RCV,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       0, 0 )

DTS_sndMsg( devId1, msgDATA )

# Get current time
t1 = datetime.datetime.now( )

# start sending of frames
DTS_setQueueEnable( devId1, True )

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

time.sleep(2)

DTS_setQueueParameters( devId2,
                       ftdf.DTS_QUEUE_DIS,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       0, 0 )

res, ret = DTS_getMsg( devId2, responseTimeout )

if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgTotal'] != nrOfFrames:
    dtsLog.warning( 'Expected ' + str(nrOfFrames) + ' rcvd messages' )
elif ret['msgSuccess'] != nrOfFrames:
    dtsLog.warning( 'Expected ' + str(nrOfFrames) + ' successful messages' )




####################################
# 11 + 64
####################################
logmsg = logmsg + 'Frame size 11 + 64 : '

msdu = []
for i in range( 64 ):
    msdu.append( i )

msgDATA = {
    'msgId': ftdf.FTDF_DATA_REQUEST,
    'srcAddrMode': ftdf.FTDF_SHORT_ADDRESS,
    'dstAddrMode': ftdf.FTDF_SHORT_ADDRESS,
    'dstPANId': 0x0001,
    'dstAddr': 0x0020,
    'msduLength': len( msdu ),
    'msdu': msdu,
    'msduHandle': 1,
    'ackTX': False,
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

DTS_setQueueParameters( devId1,
                       ftdf.DTS_QUEUE_SND,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       nrOfFrames - 1, 0 )

DTS_setQueueParameters( devId2,
                       ftdf.DTS_QUEUE_RCV,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       0, 0 )

DTS_sndMsg( devId1, msgDATA )

# Get current time
t1 = datetime.datetime.now( )

# start sending of 1000 frames
DTS_setQueueEnable( devId1, True )

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

time.sleep(2)

DTS_setQueueParameters( devId2,
                       ftdf.DTS_QUEUE_DIS,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       0, 0 )

res, ret = DTS_getMsg( devId2, responseTimeout )

if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgTotal'] != nrOfFrames:
    dtsLog.warning( 'Expected ' + str(nrOfFrames) + ' rcvd messages' )
elif ret['msgSuccess'] != nrOfFrames:
    dtsLog.warning( 'Expected ' + str(nrOfFrames) + ' successful messages' )



####################################
# 11 + 116
####################################
logmsg = logmsg + 'Frame size 11 + 116: '

msdu = []
for i in range( 116 ):
    msdu.append( i )

msgDATA = {
    'msgId': ftdf.FTDF_DATA_REQUEST,
    'srcAddrMode': ftdf.FTDF_SHORT_ADDRESS,
    'dstAddrMode': ftdf.FTDF_SHORT_ADDRESS,
    'dstPANId': 0x0001,
    'dstAddr': 0x0020,
    'msduLength': len( msdu ),
    'msdu': msdu,
    'msduHandle': 1,
    'ackTX': False,
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

DTS_setQueueParameters( devId1,
                       ftdf.DTS_QUEUE_SND,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       nrOfFrames - 1, 0 )

DTS_setQueueParameters( devId2,
                       ftdf.DTS_QUEUE_RCV,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       0, 0 )

DTS_sndMsg( devId1, msgDATA )

# Get current time
t1 = datetime.datetime.now( )

# start sending of 1000 frames
DTS_setQueueEnable( devId1, True )

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

time.sleep(2)

DTS_setQueueParameters( devId2,
                       ftdf.DTS_QUEUE_DIS,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       0, 0 )

res, ret = DTS_getMsg( devId2, responseTimeout )

if res == False:
    raise StopScript( 'No response from device' )
elif ret['msgTotal'] != nrOfFrames:
    dtsLog.warning( 'Expected ' + str(nrOfFrames) + ' rcvd messages' )
elif ret['msgSuccess'] != nrOfFrames:
    dtsLog.warning( 'Expected ' + str(nrOfFrames) + ' successful messages' )


# Return performance results via exception
raise PerformanceResults( logmsg )
