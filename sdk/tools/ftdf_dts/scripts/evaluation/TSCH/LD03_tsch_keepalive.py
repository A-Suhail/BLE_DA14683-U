import sys  #cli arguments
import time  #sleep

from scriptIncludes import *

error = 0
PANId = 0x1234
channel = 11
keySource = [0 ,1, 2, 3, 4, 5, 6, 7]

msgSTART_REQ = {
    'msgId': ftdf.FTDF_START_REQUEST,
    'PANId': PANId,
    'channelNumber': channel,
    'channelPage': 0,
    'startTime': 0,
    'beaconOrder': 15,
    'superframeOrder': 0,
    'PANCoordinator': True,
    'batteryLifeExtension': 0,
    'coordRealignment': 0,
    'coordRealignSecurityLevel': 0,
    'coordRealignKeyIdMode': 0,
    'coordRealignKeySource': [0,0,0,0,0,0,0,0],
    'coordRealignKeyIndex': 0,
    'beaconSecurityLevel': 0,
    'beaconKeyIdMode': 0,
    'beaconKeySource': [0,0,0,0,0,0,0,0],
    'beaconKeyIndex': 0 }

msgTSCH_MODE_REQ = {
    'msgId': ftdf.FTDF_TSCH_MODE_REQUEST,
    'tschMode': ftdf.FTDF_TSCH_ON,
    'timeslotStartTime': 0 }

msgSCAN_REQ = {
    'msgId': ftdf.FTDF_SCAN_REQUEST,
    'scanType': ftdf.FTDF_PASSIVE_SCAN,
    'scanChannels': 0x00001800,
    'channelPage': 0,
    'scanDuration': 9,
    'securityLevel': 0,
    'keyIdMode': 0,
    'keySource': [],
    'keyIndex': 0}

msgEBR = {
    'msgId': ftdf.FTDF_BEACON_REQUEST,
    'beaconType': ftdf.FTDF_ENHANCED_BEACON,
    'channel': channel,
    'channelPage': 0,
    'superframeOrder': 0,
    'beaconSecurityLevel': 0,
    'beaconKeyIdMode': 0,
    'beaconKeySource': keySource,
    'beaconKeyIndex': 0,
    'dstAddrMode': ftdf.FTDF_SHORT_ADDRESS,
    'dstAddr': 0xFFFF,
    'BSNSuppression': 0, }

##################################
# Release info
##################################
DTS_getReleaseInfo( 1 )
DTS_getReleaseInfo( 2 )

# Retrieve results
res1, ret1 = DTS_getMsg( 1, 1 )
res2, ret2 = DTS_getMsg( 2, 1 )

if (res1 == False or res2 == False):
    raise StopScript( "No response received from device!" )
    error += 1
elif (ret1['msgId'] != ftdf.DTS_MSG_ID_REL_INFO or
      ret2['msgId'] != ftdf.DTS_MSG_ID_REL_INFO):
    raise StopScript( "Incorrect response received from device: ret1=%s ret2=%s" % (ret1['msgId'],ret2['msgId']))
    error += 1
    
##################################
# Reset requests
##################################
DTS_sndMsg( 1, msgRESET )
DTS_sndMsg( 2, msgRESET )

# Retrieve results
res1, ret1 = DTS_getMsg( 1, 1 )
res2, ret2 = DTS_getMsg( 2, 1 )

if (res1 == False or res2 == False):
    raise StopScript( "No response received from device!" )
    error += 1
elif (ret1['msgId'] != ftdf.FTDF_RESET_CONFIRM or
      ret2['msgId'] != ftdf.FTDF_RESET_CONFIRM):
    raise StopScript( "Incorrect response received from device: ret1=%s ret2=%s" % (ret1['msgId'],ret2['msgId']))
    error += 1
    
##################################
# Set PAN ID
##################################
msg = { 'msgId': ftdf.FTDF_SET_REQUEST, 'PIBAttribute': ftdf.FTDF_PIB_PAN_ID, 'PIBAttributeValue': PANId }

DTS_sndMsg( 1, msg )
DTS_sndMsg( 2, msg )

# Retrieve results
res1, ret1 = DTS_getMsg( 1, 1 )
res2, ret2 = DTS_getMsg( 2, 1 )

if (res1 == False or res2 == False):
    raise StopScript( "No response received from device!" )
    error += 1
elif (ret1['msgId'] != ftdf.FTDF_SET_CONFIRM or
      ret2['msgId'] != ftdf.FTDF_SET_CONFIRM):
    raise StopScript( "Incorrect response received from device: ret1=%s ret2=%s" % (ret1['msgId'],ret2['msgId']))
    error += 1

##################################
# Set short addresses
##################################
msg = { 'msgId': ftdf.FTDF_SET_REQUEST, 'PIBAttribute': ftdf.FTDF_PIB_SHORT_ADDRESS, 'PIBAttributeValue': 0x0001 }

DTS_sndMsg( 1, msg )

msg = { 'msgId': ftdf.FTDF_SET_REQUEST, 'PIBAttribute': ftdf.FTDF_PIB_SHORT_ADDRESS, 'PIBAttributeValue': 0x0002 }

DTS_sndMsg( 2, msg )

res1, ret1 = DTS_getMsg( 1, 1 )
res2, ret2 = DTS_getMsg( 2, 1 )

if (res1 == False or res2 == False):
    raise StopScript( "No response received from device!" )
    error += 1    
elif (ret1['msgId'] != ftdf.FTDF_SET_CONFIRM or
      ret2['msgId'] != ftdf.FTDF_SET_CONFIRM):
    raise StopScript( "Incorrect response received from device: ret1=%s ret2=%s" % (ret1['msgId'],ret2['msgId']))
    error += 1
    
##################################
# Set slotframes
##################################
for n in range( 0, 2 ):
    msg = { 'msgId': ftdf.FTDF_SET_SLOTFRAME_REQUEST, 'handle': n, 'operation': ftdf.FTDF_ADD, 'size': 7 + ( n * 6 ) }

    DTS_sndMsg( 1, msg )
    DTS_sndMsg( 2, msg )

    # Retrieve results
    res1, ret1 = DTS_getMsg( 1, 1 )
    res2, ret2 = DTS_getMsg( 2, 1 )

    if (res1 == False or res2 == False):
        raise StopScript( "No response received from device!" )
        error += 1
    elif (ret1['msgId'] != ftdf.FTDF_SET_SLOTFRAME_CONFIRM or
          ret2['msgId'] != ftdf.FTDF_SET_SLOTFRAME_CONFIRM):
        raise StopScript( "Incorrect response received from device: ret1=%s ret2=%s" % (ret1['msgId'],ret2['msgId']))
        error += 1

##################################
# Set links
##################################
links = [ { 'linkHandle': 0, 'linkOptions': 1, 'linkType': 0, 'slotframeHandle': 1, 'nodeAddress': 2, 'timeslot': 0, 'channelOffset': 0 },
          { 'linkHandle': 1, 'linkOptions': 2, 'linkType': 0, 'slotframeHandle': 1, 'nodeAddress': 0, 'timeslot': 12, 'channelOffset': 0 },
          { 'linkHandle': 2, 'linkOptions': 2, 'linkType': 0, 'slotframeHandle': 0, 'nodeAddress': 0, 'timeslot': 3, 'channelOffset': 0 },
          { 'linkHandle': 3, 'linkOptions': 5, 'linkType': 0, 'slotframeHandle': 0, 'nodeAddress': 2, 'timeslot': 2, 'channelOffset': 0 },
          { 'linkHandle': 4, 'linkOptions': 7, 'linkType': 1, 'slotframeHandle': 1, 'nodeAddress': 0xffff, 'timeslot': 6, 'channelOffset': 0 },
          { 'linkHandle': 5, 'linkOptions': 2, 'linkType': 0, 'slotframeHandle': 1, 'nodeAddress': 0, 'timeslot': 4, 'channelOffset': 0 } ]

for link in links:
    msg = link
    msg.update( { 'msgId': ftdf.FTDF_SET_LINK_REQUEST, 'operation': ftdf.FTDF_ADD } )

    DTS_sndMsg( 1, msg )

    # Retrieve results
    res1, ret1 = DTS_getMsg( 1, 1 )

    if (res1 == False):
        raise StopScript( "No response received from device!" )
        error += 1
    elif (ret1['msgId'] != ftdf.FTDF_SET_LINK_CONFIRM):
        raise StopScript( "Incorrect response received from device: ret1=%s" % ret1['msgId'])
        error += 1
links = [ { 'linkHandle': 0, 'linkOptions': 10, 'linkType': 0, 'slotframeHandle': 1, 'nodeAddress': 0, 'timeslot': 0, 'channelOffset': 0 },
          { 'linkHandle': 1, 'linkOptions': 9, 'linkType': 0, 'slotframeHandle': 1, 'nodeAddress': 1, 'timeslot': 12, 'channelOffset': 0 },
          { 'linkHandle': 2, 'linkOptions': 9, 'linkType': 0, 'slotframeHandle': 0, 'nodeAddress': 1, 'timeslot': 3, 'channelOffset': 0 },
          { 'linkHandle': 3, 'linkOptions': 10, 'linkType': 0, 'slotframeHandle': 0, 'nodeAddress': 0, 'timeslot': 2, 'channelOffset': 0 },
          { 'linkHandle': 4, 'linkOptions': 7, 'linkType': 0, 'slotframeHandle': 1, 'nodeAddress': 1, 'timeslot': 6, 'channelOffset': 0 },
          { 'linkHandle': 5, 'linkOptions': 2, 'linkType': 0, 'slotframeHandle': 1, 'nodeAddress': 1, 'timeslot': 4, 'channelOffset': 0 } ]
          
for link in links:
    msg = link
    msg.update( { 'msgId': ftdf.FTDF_SET_LINK_REQUEST, 'operation': ftdf.FTDF_ADD } )

    DTS_sndMsg( 2, msg )

    # Retrieve results
    res2, ret2 = DTS_getMsg( 2, 1 )

    if (res2 == False):
        raise StopScript( "No response received from device!" )
        error += 1
    elif (ret2['msgId'] != ftdf.FTDF_SET_LINK_CONFIRM):
        raise StopScript( "Incorrect response received from device: ret2=%s" % ret2['msgId'])
        error += 1

##################################
# Get slotframe table
##################################
msg = { 'msgId': ftdf.FTDF_GET_REQUEST, 'PIBAttribute': ftdf.FTDF_PIB_SLOTFRAME_TABLE }

DTS_sndMsg( 1, msg )
DTS_sndMsg( 2, msg )

# Retrieve results
res1, ret1 = DTS_getMsg( 1, 1 )
res2, ret2 = DTS_getMsg( 2, 1 )

if (res1 == False or res2 == False):
    raise StopScript( "No response received from device!" )
    error += 1
elif (ret1['msgId'] != ftdf.FTDF_GET_CONFIRM or
      ret2['msgId'] != ftdf.FTDF_GET_CONFIRM):
    raise StopScript( "Incorrect response received from device: ret1=%s ret2=%s" % (ret1['msgId'],ret2['msgId']))
    error += 1
    
##################################
# Get link table
##################################
msg = { 'msgId': ftdf.FTDF_GET_REQUEST, 'PIBAttribute': ftdf.FTDF_PIB_LINK_TABLE }

DTS_sndMsg( 1, msg )
DTS_sndMsg( 2, msg )

# Retrieve results
res1, ret1 = DTS_getMsg( 1, 1 )
res2, ret2 = DTS_getMsg( 2, 1 )

if (res1 == False or res2 == False):
    raise StopScript( "No response received from device!" )
    error += 1
elif (ret1['msgId'] != ftdf.FTDF_GET_CONFIRM or
      ret2['msgId'] != ftdf.FTDF_GET_CONFIRM):
    raise StopScript( "Incorrect response received from device: ret1=%s ret2=%s" % (ret1['msgId'],ret2['msgId']))
    error += 1
    
##################################
# Set macAutoRequest to false
##################################
msg = { 'msgId': ftdf.FTDF_SET_REQUEST, 'PIBAttribute': ftdf.FTDF_PIB_AUTO_REQUEST, 'PIBAttributeValue': 0 }
DTS_sndMsg( 2, msg )

# Retrieve results
res2, ret2 = DTS_getMsg( 2, 1 )

if res2 == False:
    raise StopScript( "No response received from device!" )
    error += 1
elif (ret2['msgId'] != ftdf.FTDF_SET_CONFIRM):
    raise StopScript( "Incorrect response received from device: ret2=%s" % ret2['msgId'])
    error += 1

##################################
# Start request
##################################
DTS_sndMsg(devId1,msgSTART_REQ)

res, ret = DTS_getMsg(devId1, 1)
if res == False or ret['msgId'] != ftdf.FTDF_START_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    raise StopScript("Expected FTDF_START_CONFIRM(FTDF_SUCCESS)")
    error += 1

##################################
# TSCH mode request
##################################
DTS_sndMsg(devId1,msgTSCH_MODE_REQ)

res, ret = DTS_getMsg(devId1, 1)
if res == False or ret['msgId'] != ftdf.FTDF_TSCH_MODE_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    raise StopScript("Expected FTDF_TSCH_MODE_CONFIRM(FTDF_SUCCESS)")
    error += 1

##################################
# Passive scan request
##################################
DTS_sndMsg(devId2,msgSCAN_REQ)

##################################
# Send enhanced beacon request
##################################
DTS_sndMsg(devId1,msgEBR)

res, ret = DTS_getMsg(devId1, 10)
if res == False or ret['msgId'] != ftdf.FTDF_BEACON_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    raise StopScript("Expected FTDF_BEACON_CONFIRM(FTDF_SUCCESS)")
    error += 1

##################################
# Wait for enhanced beacon notification
##################################
slotStartTime = 0

res, ret = DTS_getMsg(devId2, 1)
if res == False or ret['msgId'] != ftdf.FTDF_BEACON_NOTIFY_INDICATION:
    raise StopScript("Expected FTDF_BEACON_NOTIFICATION_INDICATION")
    error += 1
else:
    slotStartTime = ret['timestamp'] - 80
    shift = 0
    ASN = 0
    for n in range(5):
        ASN = ASN + (ret['IEList']['IEs'][0]['content']['subIEs'][0]['content'][n] << shift)
        shift = shift + 8

res, ret = DTS_getMsg(devId2, 20)
if res == False or ret['msgId'] != ftdf.FTDF_SCAN_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    raise StopScript("Expected FTDF_SCAN_CONFIRM(FTDF_SUCCESS)")
    error += 1

##################################
# Set 
##################################
msg = { 'msgId': ftdf.FTDF_SET_REQUEST, 'PIBAttribute': ftdf.FTDF_PIB_ASN, 'PIBAttributeValue': ASN }
DTS_sndMsg( 2, msg )

# Retrieve results
res2, ret2 = DTS_getMsg( 2, 1 )

if res2 == False:
    raise StopScript( "No response received from device!" )
    error += 1
elif (ret2['msgId'] != ftdf.FTDF_SET_CONFIRM):
    raise StopScript( "Incorrect response received from device: ret2=%s" % ret2['msgId'])
    error += 1

##################################
# TSCH mode request
##################################
msgTSCH_MODE_REQ['timeslotStartTime'] = slotStartTime

DTS_sndMsg(devId2,msgTSCH_MODE_REQ)

res, ret = DTS_getMsg(devId2, 1)
if res == False or ret['msgId'] != ftdf.FTDF_TSCH_MODE_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    raise StopScript("Expected FTDF_TSCH_MODE_CONFIRM(FTDF_SUCCESS)")
    error += 1
    
#keepalive

msg = { 'msgId': ftdf.FTDF_KEEP_ALIVE_REQUEST, 'dstAddress': 0x0002, 'keepAlivePeriod': 20 }
DTS_sndMsg( 1, msg )

# Retrieve results
res2, ret2 = DTS_getMsg( 1, 1 )

if res2 == False:
    raise StopScript( "No response received from device!" )
    error += 1
elif (ret2['msgId'] != ftdf.FTDF_KEEP_ALIVE_CONFIRM):
    raise StopScript( "Incorrect response received from device: ret2=%s" % ret2['msgId'])
    error += 1

##################################
# Data request
##################################
# Prepare MSDU payload
msdu = [0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0x8]

# Create a data request message
msg = {'msgId': ftdf.FTDF_DATA_REQUEST,
       'srcAddrMode': ftdf.FTDF_SHORT_ADDRESS,
       'dstAddrMode': ftdf.FTDF_SHORT_ADDRESS,
       'dstPANId': 0x1234,
       'dstAddr': 0x0002,
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

for x in range(0, 2):
    DTS_sndMsg( 1, msg )

    res1, ret1 = DTS_getMsg( 1, 10 )

    if (res1 == False):
        raise StopScript( "No response received from device!" )
        error += 1
    elif (ret1['msgId'] != ftdf.FTDF_DATA_CONFIRM):
        raise StopScript( "Incorrect response received from device: ret1=%s" % (ret1['msgId']))
        error += 1

    # Check if data indication is received on device 2
    res2, ret2 = DTS_getMsg( 2, 1 )

    if (res2 == False):
        raise StopScript( "No response received from device!" )
        error += 1
    elif (ret2['msgId'] != ftdf.FTDF_DATA_INDICATION):
        raise StopScript( "Incorrect response received from device: ret2=%s" % (ret2['msgId']))
        error += 1

    time.sleep(1)
    
time.sleep(30)

#keepalive

msg = { 'msgId': ftdf.FTDF_KEEP_ALIVE_REQUEST, 'dstAddress': 0x0002, 'keepAlivePeriod': 0 }
DTS_sndMsg( 1, msg )

# Retrieve results
res2, ret2 = DTS_getMsg( 1, 1 )

time.sleep(5)
    
##########################################
## END OF TEST, let examine the results ##
##########################################   
if error != 0:
  logstr = ('SCRIPT: test FAILED with ' , error , ' ERRORS')
  raise StopScript( ''.join( map( str, logstr ) ) )
