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
               'ackTX': False,
               'GTSTX': False,
               'indirectTX': False,
               'securityLevel': 0,
               'keyIdMode': 0,
               'keySource': [0,0,0,0,0,0,0,0],
               'keyIndex': 0,
               'frameControlOptions': 0,
               'headerIEList': 0,
               'payloadIEList': 0,
               'sendMultiPurpose': False}


msgSET_metricsEnabled = {
    'msgId': ftdf.FTDF_SET_REQUEST,
    'PIBAttribute': ftdf.FTDF_PIB_METRICS_ENABLED,
    'PIBAttributeValue': True
}

msgSET_boIrqInfinite = {
    'msgId': ftdf.FTDF_SET_REQUEST,
    'PIBAttribute': ftdf.FTDF_PIB_BO_IRQ_THRESHOLD,
    'PIBAttributeValue': 0xff
}

msgSET_boIrqOne = {
    'msgId': ftdf.FTDF_SET_REQUEST,
    'PIBAttribute': ftdf.FTDF_PIB_BO_IRQ_THRESHOLD,
    'PIBAttributeValue': 0x1
}

msgSET_maxBe = {
    'msgId': ftdf.FTDF_SET_REQUEST,
    'PIBAttribute': ftdf.FTDF_PIB_MAX_BE,
    'PIBAttributeValue': 0x8
}

msgSET_minBe = {
    'msgId': ftdf.FTDF_SET_REQUEST,
    'PIBAttribute': ftdf.FTDF_PIB_MIN_BE,
    'PIBAttributeValue': 0x8
}

msgGET_PerformanceMetrics = {
    'msgId': ftdf.FTDF_GET_REQUEST,
    'PIBAttribute': ftdf.FTDF_PIB_PERFORMANCE_METRICS,
}

msgDbgModeSetRequest = {
    'msgId': ftdf.FTDF_DBG_MODE_SET_REQUEST,
    'dbgMode': 0x1,
}




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

############
# Enable Debug
############
# DTS_sndMsg(devId1,msgDbgModeSetRequest);

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


# Min/Max BE on node 1
DTS_sndMsg(devId1,msgSET_maxBe)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Incorrect result")

DTS_sndMsg(devId1,msgSET_minBe)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Incorrect result")

############
# Enable metrics
############
DTS_sndMsg(devId1, msgSET_metricsEnabled)
DTS_sndMsg(devId2, msgSET_metricsEnabled)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Incorrect result")

res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Incorrect result")

#############
# Set Rx on devId2
#############
DTS_sndMsg(devId2, msgRxEnable_On)

res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("rxEnable fail")

####################################################################################################
# TC1 - Interrupts and counter
####################################################################################################

# Check stats before
DTS_sndMsg(devId1, msgGET_PerformanceMetrics)

res, ret = DTS_getMsg(devId1, responseTimeout)

stats1 = ret['PIBAttributeValue']

DTS_sndMsg(devId1,msgSET_boIrqInfinite)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Incorrect result")

# Send message 
DTS_sndMsg(devId1, msgDATA_REQ)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_DATA_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("tx fail")
    
res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_DATA_INDICATION:
    error("rx fail")

# Check stats after
DTS_sndMsg(devId1, msgGET_PerformanceMetrics)

res, ret = DTS_getMsg(devId1, responseTimeout)

stats2 = ret['PIBAttributeValue']

if (stats1['BOIrqCount'] != stats2['BOIrqCount']):
    error("Unexpected BO interrupts received!")

stats1 = stats2

# This will cause DDPHY to give negative CCA
if targetFPGA == 1:
    DTS_ddphySet(devId1, 1)
else:
    DTS_ArbiterSetConfig(devId1, 1, 0, 0, 
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
    # Turn on external on devId1
    DTS_ArbiterSetExtStatus(devId1, 1)

DTS_sndMsg(devId1,msgSET_boIrqOne)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Incorrect result")

# Send message 
DTS_sndMsg(devId1, msgDATA_REQ)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_DATA_CONFIRM or ret['status'] != ftdf.FTDF_CHANNEL_ACCESS_FAILURE:
    error("Incorrect result")

# Check stats after
DTS_sndMsg(devId1, msgGET_PerformanceMetrics)

res, ret = DTS_getMsg(devId1, responseTimeout)

stats2 = ret['PIBAttributeValue']

if (stats1['BOIrqCount'] + 5 != stats2['BOIrqCount']):
    error("Expected 5 interrupts.")

# Now test correct sending

stats1 = stats2

# This will cause DDPHY to give negative CCA
if targetFPGA == 1:
    DTS_ddphySet(devId1, 0)
else:
    DTS_ArbiterReset(devId1)
    # Turn off external on devId1
    DTS_ArbiterSetExtStatus(devId1, 0)

DTS_sndMsg(devId1,msgSET_boIrqOne)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Incorrect result")

# Send message 
DTS_sndMsg(devId1, msgDATA_REQ)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_DATA_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("tx fail")
    
res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_DATA_INDICATION:
    error("rx fail")

# Verify MSDU
if ret['msdu'] != msgDATA_REQ['msdu']:
    error("Rx MSDU error")

# Check stats after
DTS_sndMsg(devId1, msgGET_PerformanceMetrics)

res, ret = DTS_getMsg(devId1, responseTimeout)

stats2 = ret['PIBAttributeValue']

if (stats1['BOIrqCount'] + 1 != stats2['BOIrqCount']):
    error("Expected 1 interrupt.")

