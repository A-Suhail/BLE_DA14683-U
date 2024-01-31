# Load-drop 2 Test: Association Disassociation

#

import sys    #cli arguments
import time    #sleep

from scriptIncludes import *

# DEVID1 = COORD
# DEVID2 = NON-COORD

PANId = 1
channel = 11
assocShortAddr = 0x1234
fastAssocShortAddr = 0x4321
coordShortAddr = 0x1000

# Frames definition:
msgSET_ASSOC_PERMIT = {'msgId': ftdf.FTDF_SET_REQUEST,
                       'PIBAttribute': ftdf.FTDF_PIB_ASSOCIATION_PERMIT,
                       'PIBAttributeValue': True }
msgSET_COORD_ShortAddress = {'msgId': ftdf.FTDF_SET_REQUEST,
                             'PIBAttribute': ftdf.FTDF_PIB_SHORT_ADDRESS,
                             'PIBAttributeValue': coordShortAddr }
msgSET_responseWaitTime = {'msgId': ftdf.FTDF_SET_REQUEST,
                           'PIBAttribute': ftdf.FTDF_PIB_RESPONSE_WAIT_TIME,
                           'PIBAttributeValue': 64 }
msgSET_associatedPANCoord = {'msgId': ftdf.FTDF_SET_REQUEST,
                             'PIBAttribute': ftdf.FTDF_PIB_ASSOCIATION_PAN_COORD,
                             'PIBAttributeValue': True }
msgSET_coordShortAddress = {'msgId': ftdf.FTDF_SET_REQUEST,
                            'PIBAttribute': ftdf.FTDF_PIB_COORD_SHORT_ADDRESS,
                            'PIBAttributeValue': 0x1001 }

# Start request
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

# Association Request
msgASSOC_REQ = {
    'msgId': ftdf.FTDF_ASSOCIATE_REQUEST,
    'channelNumber': channel,
    'channelPage': 0,
    'coordAddrMode': ftdf.FTDF_EXTENDED_ADDRESS,
    'coordPANId': PANId,
    'coordAddr': 0x10,
    'capabilityInformation': 0xc0, #non-fast
    'securityLevel': 0,
    'keyIdMode': 0,
    'keySource': [0,0,0,0,0,0,0,0],
    'keyIndex': 0,
    'channelOffset': 0,
    'hoppingSequenceId': 0
}

# Fast association request
msgFAST_ASSOC_REQ = {
    'msgId': ftdf.FTDF_ASSOCIATE_REQUEST,
    'channelNumber': channel,
    'channelPage': 0,
    'coordAddrMode': ftdf.FTDF_EXTENDED_ADDRESS,
    'coordPANId': PANId,
    'coordAddr': 0x10,
    'capabilityInformation': 0xFF, #fast
    'securityLevel': 0,
    'keyIdMode': 0,
    'keySource': [0,0,0,0,0,0,0,0],
    'keyIndex': 0,
    'channelOffset': 0,
    'hoppingSequenceId': 0
}

# Association Response
msgASSOC_RESP = {
    'msgId': ftdf.FTDF_ASSOCIATE_RESPONSE,
    'deviceAddress': 0x20,
    'assocShortAddress': assocShortAddr,
    'status': ftdf.FTDF_ASSOCIATION_SUCCESSFUL,
    'fastA': False,
    'securityLevel':0,
    'keyIdMode': 0,
    'keySource': [0,0,0,0,0,0,0,0],
    'keyIndex': 0,
    'channelOffset': 0,
    'hoppingSequenceLength': 0
}

# Fast association Response
msgFAST_ASSOC_RESP = {
    'msgId': ftdf.FTDF_ASSOCIATE_RESPONSE,
    'deviceAddress': 0x20,
    'assocShortAddress': fastAssocShortAddr,
    'status': ftdf.FTDF_FAST_ASSOCIATION_SUCCESSFUL,
    'fastA': True,
    'securityLevel':0,
    'keyIdMode': 0,
    'keySource': [0,0,0,0,0,0,0,0],
    'keyIndex': 0,
    'channelOffset': 0,
    'hoppingSequenceLength': 0
}

# Device disassociate Request
msgDIS_REQ_fromDev = {
    'msgId': ftdf.FTDF_DISASSOCIATE_REQUEST,
    'deviceAddrMode': ftdf.FTDF_SHORT_ADDRESS,
    'devicePANId': PANId,
    'deviceAddress': coordShortAddr,
    'disassociateReason': ftdf.FTDF_DEVICE_WISH_LEAVE_PAN,
    'txIndirect': False,
    'securityLevel': 0,
    'keyIdMode': 0,
    'keySource': [0,0,0,0,0,0,0,0],
    'keyIndex': 0
}

# Coord disassociate Request
msgDIS_REQ_fromCoord = {
    'msgId': ftdf.FTDF_DISASSOCIATE_REQUEST,
    'deviceAddrMode': ftdf.FTDF_SHORT_ADDRESS,
    'devicePANId': PANId,
    'deviceAddress': fastAssocShortAddr,
    'disassociateReason': ftdf.FTDF_COORD_WISH_DEVICE_LEAVE_PAN,
    'txIndirect': True,
    'securityLevel': 0,
    'keyIdMode': 0,
    'keySource': [0,0,0,0,0,0,0,0],
    'keyIndex': 0
}

# Poll request
msgPOLL_REQ = {
    'msgId': ftdf.FTDF_POLL_REQUEST,
    'coordAddrMode': ftdf.FTDF_SHORT_ADDRESS,
    'coordPANId': PANId,
    'coordAddr': coordShortAddr,
    'securityLevel': 0,
    'keyIdMode': 0,
    'keySource': [0,0,0,0,0,0,0,0],
    'keyIndex': 0}

# Scan request
msgORPHAN_SCAN_REQ = {
    'msgId': ftdf.FTDF_SCAN_REQUEST,
    'scanType': ftdf.FTDF_ORPHAN_SCAN,
    'scanChannels': 0x800, #channel 11
    'channelPage': 0,
    'scanDuration': 0,
    'securityLevel': 0,
    'keyIdMode': 0,
    'keySource': [0,0,0,0,0,0,0,0],
    'keyIndex': 0}

# Orphan response
msgORPHAN_RESPONSE = {
    'msgId': ftdf.FTDF_ORPHAN_RESPONSE,
    'orphanAddress': 0x20,
    'shortAddress': fastAssocShortAddr,
    'associatedMember': True,
    'securityLevel': 0,
    'keyIdMode': 0,
    'keySource': [0,0,0,0,0,0,0,0],
    'keyIndex': 0}

# Beacon request
msgBEACON_REQ = {
    'msgId': ftdf.FTDF_BEACON_REQUEST,
    'beaconType': ftdf.FTDF_NORMAL_BEACON,
    'channel': channel,
    'channelPage': 0,
    'superframeOrder': 0,
    'beaconSecurityLevel': 0,
    'beaconKeyIdMode': 0,
    'beaconKeySource': [0,0,0,0,0,0,0,0],
    'beaconKeyIndex': 0,
    'dstAddrMode': ftdf.FTDF_SHORT_ADDRESS,
    'dstAddr': fastAssocShortAddr,
    'BSNSuppression': False}

msgBEACON_EXT_REQ = {
    'msgId': ftdf.FTDF_BEACON_REQUEST,
    'beaconType': ftdf.FTDF_NORMAL_BEACON,
    'channel': channel,
    'channelPage': 0,
    'superframeOrder': 0,
    'beaconSecurityLevel': 0,
    'beaconKeyIdMode': 0,
    'beaconKeySource': [0,0,0,0,0,0,0,0],
    'beaconKeyIndex': 0,
    'dstAddrMode': ftdf.FTDF_EXTENDED_ADDRESS,
    'dstAddr': 0x10,
    'BSNSuppression': False}


def error( logstr ):
    raise StopScript( logstr )


def checkPIB( dev, checkShortAddr, checkPANId, checkChannel ):
    msgGet = {'msgId': ftdf.FTDF_GET_REQUEST,
              'PIBAttribute': 0}

    #############
    # Short address
    #############
    msgGet['PIBAttribute'] = ftdf.FTDF_PIB_SHORT_ADDRESS
    DTS_sndMsg(dev,msgGet)

    res, ret = DTS_getMsg(dev, 10)
    if ret['msgId'] != ftdf.FTDF_GET_CONFIRM or ret['PIBAttributeValue'] != checkShortAddr:
        error("Short address not updated")

    #############
    # PAN ID
    #############
    msgGet['PIBAttribute'] = ftdf.FTDF_PIB_PAN_ID
    DTS_sndMsg(dev,msgGet)

    res, ret = DTS_getMsg(dev, 10)
    if ret['msgId'] != ftdf.FTDF_GET_CONFIRM or ret['PIBAttributeValue'] != checkPANId:
        error("PAN ID not updated")

    #############
    # CHANNEL
    #############
    msgGet['PIBAttribute'] = ftdf.FTDF_PIB_CURRENT_CHANNEL
    DTS_sndMsg(dev,msgGet)

    res, ret = DTS_getMsg(dev, 10)
    if ret['msgId'] != ftdf.FTDF_GET_CONFIRM or ret['PIBAttributeValue'] != checkChannel:
        error("Channel not updated")

    #############
    # COORD EXT ADDR
    #############
    msgGet['PIBAttribute'] = ftdf.FTDF_PIB_COORD_EXTENDED_ADDRESS
    DTS_sndMsg(dev,msgGet)

    res, ret = DTS_getMsg(dev, 10)
    if ret['msgId'] != ftdf.FTDF_GET_CONFIRM or ret['PIBAttributeValue'] != 0x10:
        error("macCoordExtendedAddress not updated")



# START OF TESTS

###############################
# 1+2> RESET
###############################
DTS_sndMsg(devId1, msgRESET)
DTS_sndMsg(devId2, msgRESET)

res, ret = DTS_getMsg(devId1, responseTimeout)
if res == False:
    error("No response")
elif ret['msgId'] != ftdf.FTDF_RESET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Incorrect result")

res, ret = DTS_getMsg(devId2, responseTimeout)
if res == False:
    error("No response")
elif ret['msgId'] != ftdf.FTDF_RESET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Incorrect result")


DTS_sndMsg(devId1,msgSET_responseWaitTime)
DTS_sndMsg(devId2,msgSET_responseWaitTime)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Could not set macResponseWaitTime")

res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Could not set macResponseWaitTime")


###############################
# 1> Send start request
###############################
DTS_sndMsg(devId1,msgSTART_REQ)

###############################
# 1< Receive NO_SHORT_ADDRESS start confirm
###############################
res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_START_CONFIRM or ret['status'] != ftdf.FTDF_NO_SHORT_ADDRESS:
    error("Expected FTDF_NO_SHORT_ADDRESS")

###############################
# 1> Set short address
###############################
DTS_sndMsg(devId1,msgSET_COORD_ShortAddress)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Incorrect result")

###############################
# 1> Send start request with beacon order = 10
###############################
msgSTART_REQ['beaconOrder'] = 10
DTS_sndMsg(devId1,msgSTART_REQ)

###############################
# 1< Receive INVALID_PARAMETER start confirm
###############################
res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_START_CONFIRM or ret['status'] != ftdf.FTDF_INVALID_PARAMETER:
    error("Expected FTDF_INVALID_PARAMETER")

###############################
# 1> Send start request with beacon order = 10
###############################
msgSTART_REQ['beaconOrder'] = 15
DTS_sndMsg(devId1,msgSTART_REQ)

###############################
# 1< Receive successful start confirm
###############################
res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_START_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Expected FTDF_SUCCESS")



###############################
# 1> Get macCoordShortAddress, macCurrentChannel and macPANId
# 1< Receive the attribute values matching start request parameters
###############################
msgGet['PIBAttribute'] = ftdf.FTDF_PIB_PAN_ID
DTS_sndMsg(devId1,msgGet)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_GET_CONFIRM or ret['PIBAttributeValue'] != PANId:
    error("PAN ID not updated")

msgGet['PIBAttribute'] = ftdf.FTDF_PIB_CURRENT_CHANNEL
DTS_sndMsg(devId1,msgGet)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_GET_CONFIRM or ret['PIBAttributeValue'] != channel:
    error("Channel not updated")

msgGet['PIBAttribute'] = ftdf.FTDF_PIB_COORD_SHORT_ADDRESS
DTS_sndMsg(devId1,msgGet)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_GET_CONFIRM or ret['PIBAttributeValue'] != coordShortAddr:
    error("macCoordShortAddress not updated")

msgGet['PIBAttribute'] = ftdf.FTDF_PIB_COORD_EXTENDED_ADDRESS
DTS_sndMsg(devId1,msgGet)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_GET_CONFIRM or ret['PIBAttributeValue'] != 0x10:
    error("macCoordExtendedAddress not updated")



###############################
# 1+2> Enable RX
###############################
DTS_sndMsg(devId1, msgRxEnable_On)
DTS_sndMsg(devId2, msgRxEnable_On)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("rxEnable fail")

res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("rxEnable fail")


###############################
# 2> Send associate request
###############################
DTS_sndMsg(devId2, msgASSOC_REQ)

# Expect no result on coord
res, ret = DTS_getMsg(devId1, responseTimeout)
if res == True:
    error("Association indication rcvd with macAssociationPermit False")


###############################
# 2< Receive NO_DATA associate confirm
###############################
res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_ASSOCIATE_CONFIRM or ret['status'] != ftdf.FTDF_NO_DATA:
    error("Expected FTDF_NO_DATA")


###############################
# 1> Set macAssociatePermit to true
###############################
DTS_sndMsg(devId1,msgSET_ASSOC_PERMIT)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Could not set macAssociatePermit")



###############################
# 2> Send associate request
###############################
DTS_sndMsg(devId2, msgASSOC_REQ)

###############################
# 1< Receive associate indication with matching capabilities
###############################
res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_ASSOCIATE_INDICATION or ret['capabilityInformation'] != msgASSOC_REQ['capabilityInformation']:
    error("Incorrect association capability information rcvd")

###############################
# 2< Receive NO_DATA confirm
###############################
res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_ASSOCIATE_CONFIRM or ret['status'] != ftdf.FTDF_NO_DATA:
    error("Expected FTDF_NO_DATA")


###############################
# 1> Send associate response with PAN access denied
###############################
msgASSOC_RESP['status'] = ftdf.FTDF_ASSOCIATION_PAN_ACCESS_DENIED
DTS_sndMsg(devId1, msgASSOC_RESP)

time.sleep( 1 )

###############################
# 2> Send associate request
###############################
DTS_sndMsg(devId2, msgASSOC_REQ)

###############################
# 1< Receive associate indication
###############################
res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_ASSOCIATE_INDICATION or ret['capabilityInformation'] != msgASSOC_REQ['capabilityInformation']:
    error("Incorrect association capability information rcvd")

###############################
# 2< Receive PAN_ACCESS_DENIED associate confirm
###############################
res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_ASSOCIATE_CONFIRM or ret['status'] != ftdf.FTDF_PAN_ACCESS_DENIED or ret['assocShortAddress'] != 0xffff:
    error("Incorrect associate confirm received")

###############################
# 1< Successful comm status indication
###############################
res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_COMM_STATUS_INDICATION or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Incorrect COMM_STATUS_INDICATION")



###############################
# 1> Send 17 associate responses
###############################
for i in range( maxBuffers + 1 ):
    DTS_sndMsg(devId1, msgASSOC_RESP)

###############################
# 1< Receive 1 TRANSACTION_OVERFLOW comm status indication
###############################
res, ret = DTS_getMsg(devId1, 10 )
if ret['msgId'] != ftdf.FTDF_COMM_STATUS_INDICATION or ret['status'] != ftdf.FTDF_TRANSACTION_OVERFLOW:
    error("Expected transaction overflow" )

###############################
# 1< Receive 16 TRANSACTION_EXPIRED comm status indication
###############################
for i in range( maxBuffers ):
    res, ret = DTS_getMsg(devId1, 10 )
    if ret['msgId'] != ftdf.FTDF_COMM_STATUS_INDICATION or ret['status'] != ftdf.FTDF_TRANSACTION_EXPIRED:
        error("Transaction expired expected")



###############################
# 2> Send associate request
###############################
DTS_sndMsg(devId2, msgASSOC_REQ)

###############################
# 1< Receive associate indication
###############################
res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_ASSOCIATE_INDICATION or ret['capabilityInformation'] != msgASSOC_REQ['capabilityInformation']:
    error("Incorrect association capability information rcvd")

###############################
# 1> Send associate response
###############################
msgASSOC_RESP['status'] = ftdf.FTDF_ASSOCIATION_SUCCESSFUL
DTS_sndMsg(devId1, msgASSOC_RESP)

###############################
# 2< Receive successful associate confirm
###############################
res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_ASSOCIATE_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS or ret['assocShortAddress'] != msgASSOC_RESP['assocShortAddress']:
    error("Incorrect associate confirm received")

###############################
# 1< Receive successful comm status indication
###############################
res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_COMM_STATUS_INDICATION or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Incorrect COMM_STATUS_INDICATION")


#################
# 2> Get macCoordShortAddress, macCurrentChannel, macPANId and macCoordExtendedAddress
# 2< Receive macCoordShortAddress, macCurrentChannel, macPANId and macCoordExtendedAddress
#    values matching the associate response parameters
#################
checkPIB( devId2, assocShortAddr, PANId, channel )

