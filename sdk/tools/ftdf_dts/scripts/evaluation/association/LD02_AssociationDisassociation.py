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
msgGET_PM = {'msgId': ftdf.FTDF_GET_REQUEST,
             'PIBAttribute': ftdf.FTDF_PIB_PERFORMANCE_METRICS}
msgGET_TC = {'msgId': ftdf.FTDF_GET_REQUEST,
             'PIBAttribute': ftdf.FTDF_PIB_TRAFFIC_COUNTERS}

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



# START OF TESTS #
############
# RESET
############
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

#####################
#####################
# FR8700 - FR8720 | START REQUEST
#####################
#####################

#############
# FR8720
# MLME-START.confirm status checking:
#   status = FTDF_NO_SHORT_ADDRESS when macShortAddress == 0xffff
#   status = FTDF_INVALID_PARAMETER when beaconOrder parameter != 15
#   status = FTDF_SUCCESS otherwise
#############

# TEST 1:
#   status = FTDF_NO_SHORT_ADDRESS when macShortAddress == 0xffff
DTS_sndMsg(devId1,msgSTART_REQ)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_START_CONFIRM or ret['status'] != ftdf.FTDF_NO_SHORT_ADDRESS:
    error("Expected FTDF_NO_SHORT_ADDRESS")

# Now set macShortAddress and try with an invalid beacon order
DTS_sndMsg(devId1,msgSET_COORD_ShortAddress)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Incorrect result")

# TEST 2:
#   status = FTDF_INVALID_PARAMETER when beaconOrder parameter != 15
msgSTART_REQ['beaconOrder'] = 10
DTS_sndMsg(devId1,msgSTART_REQ)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_START_CONFIRM or ret['status'] != ftdf.FTDF_INVALID_PARAMETER:
    error("Expected FTDF_INVALID_PARAMETER")

# TEST 3:
#   status = FTDF_SUCCESS otherwise
msgSTART_REQ['beaconOrder'] = 15
DTS_sndMsg(devId1,msgSTART_REQ)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_START_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Expected FTDF_SUCCESS")

#############
# FR8700
# Check if the PIB was updated correctly
#############

#############
# PAN ID
#############
msgGet['PIBAttribute'] = ftdf.FTDF_PIB_PAN_ID
DTS_sndMsg(devId1,msgGet)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_GET_CONFIRM or ret['PIBAttributeValue'] != PANId:
    error("PAN ID not updated")

#############
# CHANNEL
#############
msgGet['PIBAttribute'] = ftdf.FTDF_PIB_CURRENT_CHANNEL
DTS_sndMsg(devId1,msgGet)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_GET_CONFIRM or ret['PIBAttributeValue'] != channel:
    error("Channel not updated")

#############
# COORD ADDRESSES
#############
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


#####################
#####################
# END OF
# FR8700 - FR8720 | START REQUEST
#####################
#####################


#####################
#####################
# FR8100 - FR8160 | ASSOCIATION REQUEST
# FR8200 - FR8220 | ASSOCIATION RESPONSE
# FR8400 - FR8420 | DISASSOCIATION NOTIFICATION
#####################
#####################

DTS_sndMsg(devId1,msgSET_responseWaitTime)
DTS_sndMsg(devId2,msgSET_responseWaitTime)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Could not set macResponseWaitTime")

res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Could not set macResponseWaitTime")



# Set radios on for both devices
DTS_sndMsg(devId1, msgRxEnable_On)
DTS_sndMsg(devId2, msgRxEnable_On)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("rxEnable fail")

res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("rxEnable fail")


#################
# Try associating when macAssociationPermit is False, this should not be possible
#################


# association request on device 2
DTS_sndMsg(devId2, msgASSOC_REQ)

# Expect no result on coord
res, ret = DTS_getMsg(devId1, responseTimeout)
if res == True:
    error("Association indication rcvd with macAssociationPermit False")

# Check result on NO_DATA
res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_ASSOCIATE_CONFIRM or ret['status'] != ftdf.FTDF_NO_DATA:
    error("Expected FTDF_NO_DATA")


# Allow association on the PAN coordinator
DTS_sndMsg(devId1,msgSET_ASSOC_PERMIT)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Could not set macAssociatePermit")

################
# Association request without response should result in no data
################
# association request on device 2
DTS_sndMsg(devId2, msgASSOC_REQ)

# should result in an association indication on device 1
res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_ASSOCIATE_INDICATION or ret['capabilityInformation'] != msgASSOC_REQ['capabilityInformation']:
    error("Incorrect association capability information rcvd")

res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_ASSOCIATE_CONFIRM or ret['status'] != ftdf.FTDF_NO_DATA:
    error("Expected FTDF_NO_DATA")

#################
# Check for an unsuccessful assocation result
#################
# Do not allow the device to associate, so send the ASSOCIATE.response
msgASSOC_RESP['status'] = ftdf.FTDF_ASSOCIATION_PAN_ACCESS_DENIED
DTS_sndMsg(devId1, msgASSOC_RESP)

time.sleep( 1 )

# association request on device 2
DTS_sndMsg(devId2, msgASSOC_REQ)

# should result in an association indication on device 1
res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_ASSOCIATE_INDICATION or ret['capabilityInformation'] != msgASSOC_REQ['capabilityInformation']:
    error("Incorrect association capability information rcvd")

# should result in the associate confirm on device 2
res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_ASSOCIATE_CONFIRM or ret['status'] != ftdf.FTDF_PAN_ACCESS_DENIED or ret['assocShortAddress'] != 0xffff:
    error("Incorrect associate confirm received")

# Which in turn results in a COMM-STATUS.indication on device 1
res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_COMM_STATUS_INDICATION or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Incorrect COMM_STATUS_INDICATION")


#################
# Check for transaction expired + transaction overflow
#################
for i in range( maxBuffers + 1 ):
    DTS_sndMsg(devId1, msgASSOC_RESP)

res, ret = DTS_getMsg(devId1, 10 )
if ret['msgId'] != ftdf.FTDF_COMM_STATUS_INDICATION or ret['status'] != ftdf.FTDF_TRANSACTION_OVERFLOW:
    error("Expected transaction overflow" )

for i in range( maxBuffers ):
    res, ret = DTS_getMsg(devId1, 10 )
    if ret['msgId'] != ftdf.FTDF_COMM_STATUS_INDICATION or ret['status'] != ftdf.FTDF_TRANSACTION_EXPIRED:
        error("Transaction expired expected")


#################
# Check for a successful assocation result
#################
# association request on device 2
DTS_sndMsg(devId2, msgASSOC_REQ)

# should result in an association indication on device 1
res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_ASSOCIATE_INDICATION or ret['capabilityInformation'] != msgASSOC_REQ['capabilityInformation']:
    error("Incorrect association capability information rcvd")

# Allow the device to associate, so send the ASSOCIATE.response
msgASSOC_RESP['status'] = ftdf.FTDF_ASSOCIATION_SUCCESSFUL
DTS_sndMsg(devId1, msgASSOC_RESP)

# should result in the associate confirm on device 2
res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_ASSOCIATE_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS or ret['assocShortAddress'] != msgASSOC_RESP['assocShortAddress']:
    error("Incorrect associate confirm received")

# Which in turn results in a COMM-STATUS.inidcation on device 1
res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_COMM_STATUS_INDICATION or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Incorrect COMM_STATUS_INDICATION")


#################
# Check if the PIB was updated correctly
#################
checkPIB( devId2, assocShortAddr, PANId, channel )

#########################
# Disassociation initiated by device
#########################


# Try disassociation with a different PANId
msgDIS_REQ_fromDev['devicePANId'] = 0x1234
DTS_sndMsg(devId2,msgDIS_REQ_fromDev)

res, ret = DTS_getMsg(devId2,responseTimeout)
if ret['msgId'] != ftdf.FTDF_DISASSOCIATE_CONFIRM or ret['status'] != ftdf.FTDF_INVALID_PARAMETER:
    error("FTDF_DISASSOCIATE_CONFIRM expected invalid parameter")

# There should be no indication on the coord
res, ret = DTS_getMsg(devId1, responseTimeout)
if res == True:
    error("Unexpected message in queue")


# Disassociation initiated by device
msgDIS_REQ_fromDev['devicePANId'] = PANId
DTS_sndMsg(devId2,msgDIS_REQ_fromDev)

# Should result in disassociation indication on coord
res, ret = DTS_getMsg(devId1,responseTimeout)
if ret['msgId'] != ftdf.FTDF_DISASSOCIATE_INDICATION or ret['deviceAddress'] != 0x20 or ret['disassociateReason'] != ftdf.FTDF_DEVICE_WISH_LEAVE_PAN:
    error("FTDF_DISASSOCIATE_INDICATION unexpected results")

res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_DISASSOCIATE_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("FTDF_DISASSOCIATE_CONFIRM unexpected results")

###################
# Check if the PIB values were correctly reset
###################
checkPIB( devId2, 0xffff, 0xffff, channel )


#######################
# Fast association
#######################


# fast association request on device 2
DTS_sndMsg(devId2, msgFAST_ASSOC_REQ)

# should result in an association indication on device 1
res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_ASSOCIATE_INDICATION or ret['capabilityInformation'] != msgFAST_ASSOC_REQ['capabilityInformation']:
    error("Incorrect association capability information rcvd")

# Allow the device to associate, so send the ASSOCIATE.response
DTS_sndMsg(devId1, msgFAST_ASSOC_RESP)

# should result in the associate confirm on device 2
res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_ASSOCIATE_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS or ret['assocShortAddress'] != msgFAST_ASSOC_RESP['assocShortAddress']:
    error("Incorrect associate confirm received")

# Which in turn results in a COMM-STATUS.inidcation on device 1
res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_COMM_STATUS_INDICATION or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Incorrect COMM_STATUS_INDICATION")


#################
# Check if the PIB was updated correctly
#################
checkPIB( devId2, fastAssocShortAddr, PANId, channel )


#########################
# Disassociation initiated by coordinator
#########################


#################
# Check for transaction expired
#################
DTS_sndMsg(devId1, msgDIS_REQ_fromCoord)

res, ret = DTS_getMsg(devId1, 10)
if ret['msgId'] != ftdf.FTDF_DISASSOCIATE_CONFIRM or ret['status'] != ftdf.FTDF_TRANSACTION_EXPIRED:
    error("Transaction expired expected")


#################
# Successful disassociation
#################

# Disassociation initiated by coord
DTS_sndMsg(devId1,msgDIS_REQ_fromCoord)

time.sleep(1)

# Send poll request to device to retrieve the command
DTS_sndMsg(devId2,msgPOLL_REQ)

# First comes poll confirm
res, ret = DTS_getMsg(devId2,responseTimeout)
if ret['msgId'] != ftdf.FTDF_POLL_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Poll confirm")

# Then comes disassociation indication
res, ret = DTS_getMsg(devId2,responseTimeout)
if ret['msgId'] != ftdf.FTDF_DISASSOCIATE_INDICATION or ret['deviceAddress'] != 0x10 or ret['disassociateReason'] != ftdf.FTDF_COORD_WISH_DEVICE_LEAVE_PAN:
    error("Incorrect disassociate indication")

# Check for confirm on coord
res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_DISASSOCIATE_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("FTDF_DISASSOCIATE_CONFIRM unexpected results")


###################
# Check if the PIB values were correctly reset
###################
checkPIB( devId2, 0xffff, 0xffff, channel )


#######################
#######################
# Orphan scan
#######################
#######################


# First associate again

#######################
# Fast association
#######################
# fast association request on device 2
DTS_sndMsg(devId2, msgFAST_ASSOC_REQ)

# should result in an association indication on device 1
res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_ASSOCIATE_INDICATION or ret['capabilityInformation'] != msgFAST_ASSOC_REQ['capabilityInformation']:
    error("Incorrect association capability information rcvd")

# Allow the device to associate, so send the ASSOCIATE.response
DTS_sndMsg(devId1, msgFAST_ASSOC_RESP)

# should result in the associate confirm on device 2
res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_ASSOCIATE_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS or ret['assocShortAddress'] != msgFAST_ASSOC_RESP['assocShortAddress']:
    error("Incorrect associate confirm received")

# Which in turn results in a COMM-STATUS.inidcation on device 1
res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_COMM_STATUS_INDICATION or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Incorrect COMM_STATUS_INDICATION")


#################
# Check if the PIB was updated correctly
#################
checkPIB( devId2, fastAssocShortAddr, PANId, channel )


##################
# Orphan scan
##################

# Check for NO_BEACON result
DTS_sndMsg(devId2, msgORPHAN_SCAN_REQ)

# Orphan indication should be received on coord, ignore it
res, ret = DTS_getMsg(devId1,responseTimeout)
if ret['msgId'] != ftdf.FTDF_ORPHAN_INDICATION:
    error("Orphan indication")

# Then no beacon scan result is returned
res, ret = DTS_getMsg(devId2,responseTimeout)
if ret['msgId'] != ftdf.FTDF_SCAN_CONFIRM or ret['status'] != ftdf.FTDF_NO_BEACON or ret['resultListSize'] != 0:
    error("Scan confirm")


##############
# Orphan scan again
DTS_sndMsg(devId2, msgORPHAN_SCAN_REQ)

res, ret = DTS_getMsg(devId1,responseTimeout)
if ret['msgId'] != ftdf.FTDF_ORPHAN_INDICATION or ret['orphanAddress'] != 0x20:
    error("Orphan indication")

# Send orphan response
DTS_sndMsg(devId1, msgORPHAN_RESPONSE)

res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_SCAN_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Scan confirm")

des = ret['coordRealignDescriptor']
if des['coordPANId'] != PANId or des['coordShortAddr'] != coordShortAddr or des['channelNumber'] != channel or des['shortAddr'] != fastAssocShortAddr:
    error("Scan confirm")

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_COMM_STATUS_INDICATION:
    error("Comm status")


# Set radios on for both devices
DTS_sndMsg(devId1, msgRxEnable_On)
DTS_sndMsg(devId2, msgRxEnable_On)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("rxEnable fail")

res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("rxEnable fail")

#######################
#######################
# PAN ID conflict
#######################
#######################


# Set macAssociatedPANCoord
DTS_sndMsg( devId2, msgSET_associatedPANCoord )

res, ret = DTS_getMsg(devId2, responseTimeout )
if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Set confirm")

# Set macCoordShortAddress to a different value
DTS_sndMsg( devId2, msgSET_coordShortAddress )

res, ret = DTS_getMsg(devId2, responseTimeout )
if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Set confirm")


# Beacon request on coord
DTS_sndMsg( devId1, msgBEACON_REQ )

res, ret = DTS_getMsg(devId1, responseTimeout )
if ret['msgId'] != ftdf.FTDF_BEACON_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Beacon request")


# Sync-Loss should be generated on both devices
res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_SYNC_LOSS_INDICATION or ret['lossReason'] != ftdf.FTDF_PAN_ID_CONFLICT or ret['PANId'] != PANId or ret['channelNumber'] != channel:
    error("Sync loss indication")

res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_SYNC_LOSS_INDICATION or ret['lossReason'] != ftdf.FTDF_PAN_ID_CONFLICT or ret['PANId'] != PANId or ret['channelNumber'] != channel:
    error("Sync loss indication")


# Make device 2 a coordinator as well
DTS_sndMsg(devId2,msgSTART_REQ)

res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_START_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Expected FTDF_SUCCESS")


# Beacon request on dev 2
DTS_sndMsg( devId2, msgBEACON_EXT_REQ )

res, ret = DTS_getMsg(devId2, responseTimeout )
if ret['msgId'] != ftdf.FTDF_BEACON_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Beacon request")


# Sync-Loss should be generated on dev 1
res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_SYNC_LOSS_INDICATION or ret['lossReason'] != ftdf.FTDF_PAN_ID_CONFLICT or ret['PANId'] != PANId or ret['channelNumber'] != channel:
    error("Sync loss indication")

# No sync-loss expected on dev 2
res, ret = DTS_getMsg(devId2, responseTimeout)
if res == True:
    error("Expected no sync loss")


###############
# PM counters
###############
DTS_sndMsg(devId1, msgGET_PM)
DTS_sndMsg(devId2, msgGET_PM)

res, ret = DTS_getMsg(devId1,responseTimeout)
if ret['msgId'] != ftdf.FTDF_GET_CONFIRM:
    error("Get PM")

res, ret = DTS_getMsg(devId2,responseTimeout)
if ret['msgId'] != ftdf.FTDF_GET_CONFIRM:
    error("Get PM")

###############
# Traffic counters
###############
DTS_sndMsg(devId1, msgGET_TC)
DTS_sndMsg(devId2, msgGET_TC)

res, ret = DTS_getMsg(devId1,responseTimeout)
if ret['msgId'] != ftdf.FTDF_GET_CONFIRM:
    error("Get PM")

res, ret = DTS_getMsg(devId2,responseTimeout)
if ret['msgId'] != ftdf.FTDF_GET_CONFIRM:
    error("Get PM")

