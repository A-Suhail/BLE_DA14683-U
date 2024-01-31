# Load-drop 2 Test: Indirect data transactions

import sys    #cli arguments
import time    #sleep

from scriptIncludes import *

PANId = 1

msgDATA_REQ = {'msgId': ftdf.FTDF_DATA_REQUEST,
               'srcAddrMode': ftdf.FTDF_EXTENDED_ADDRESS,
               'dstAddrMode': ftdf.FTDF_EXTENDED_ADDRESS,
               'dstPANId': PANId,
               'dstAddr': 0x20,
               'msduLength': 5,
               'msdu': [0,1,2,3,4],
               'msduHandle': 0,
               'ackTX': True,
               'GTSTX': False,
               'indirectTX': True,
               'securityLevel': 0,
               'keyIdMode': 0,
               'keySource': [0,0,0,0,0,0,0,0],
               'keyIndex': 0,
               'frameControlOptions': 0,
               'headerIEList': 0,
               'payloadIEList': 0,
               'sendMultiPurpose': False}

msgPOLL_REQ = {'msgId': ftdf.FTDF_POLL_REQUEST,
               'coordAddrMode': ftdf.FTDF_EXTENDED_ADDRESS,
               'coordPANId': PANId,
               'coordAddr': 0x10,
               'securityLevel': 0,
               'keyIdMode': 0,
               'keySource': [0,0,0,0,0,0,0,0],
               'keyIndex': 0}

msgPURGE_REQ = {'msgId': ftdf.FTDF_PURGE_REQUEST,
                'msduHandle': 1}

def error( logstr ):
    raise StopScript( logstr )


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

#############
# Set PIB attributes
#############

# PAN ID
DTS_sndMsg(devId1,msgSET_PANId)
DTS_sndMsg(devId2,msgSET_PANId)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Incorrect result")

res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Incorrect result")


################
# Data frames
################
# FR4600 + FR4620
# - Transaction overflow
# - Transaction expired
#################
'''
for i in range( 17 ):
    DTS_sndMsg(devId1, msgDATA_REQ)

res, ret = DTS_getMsg(devId1, 10)
if ret['msgId'] != ftdf.FTDF_DATA_CONFIRM or ret['status'] != ftdf.FTDF_TRANSACTION_OVERFLOW:
    error("Expected transaction overflow")

for i in range( 16 ):
    res, ret = DTS_getMsg(devId1, 10)
    if ret['msgId'] != ftdf.FTDF_DATA_CONFIRM or ret['status'] != ftdf.FTDF_TRANSACTION_EXPIRED:
        error("Expected transaction expired")
'''


#################
# FR4900
# - Purge request
#################
msgDATA_REQ['msduHandle'] = 1

DTS_sndMsg(devId1, msgDATA_REQ)
DTS_sndMsg(devId1, msgPURGE_REQ)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_PURGE_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS or ret['msduHandle'] != 1:
    error( "Purge confirm" )

DTS_sndMsg(devId1, msgPURGE_REQ)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_PURGE_CONFIRM or ret['status'] != ftdf.FTDF_INVALID_HANDLE or ret['msduHandle'] != 1:
    error( "Purge confirm" )

res, ret = DTS_getMsg(devId1, responseTimeout)
if res == True:
    error( "Data confirm rcvd after purge request" )

#################
# FR4700 - FR4750
# - Poll request
#################

#############
# Set radios on for both devices
#############
DTS_sndMsg(devId1, msgRxEnable_On)
DTS_sndMsg(devId2, msgRxEnable_On)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("rxEnable fail")

res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("rxEnable fail")


# Check for no-data result
DTS_sndMsg(devId2, msgPOLL_REQ)

res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_POLL_CONFIRM or ret['status'] != ftdf.FTDF_NO_DATA:
    error("Poll confirm" )


# Check for successful result
DTS_sndMsg(devId1, msgDATA_REQ)

time.sleep(1)

DTS_sndMsg(devId2, msgPOLL_REQ)

# First comes the poll confirm
res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_POLL_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Poll confirm" )

# Then comes the data indication
res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_DATA_INDICATION:
    error("Data indication")

# Data confirm on sending side
res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_DATA_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS or ret['msduHandle'] != msgDATA_REQ['msduHandle']:
    error("Data confirm")

