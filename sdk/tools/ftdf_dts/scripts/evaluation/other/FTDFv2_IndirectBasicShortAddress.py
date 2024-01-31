# Load-drop 2 Test: Indirect data transactions

import sys    #cli arguments
import time    #sleep

from scriptIncludes import *

PANId = 1

msgDATA_REQ = {'msgId': ftdf.FTDF_DATA_REQUEST,
               'srcAddrMode': ftdf.FTDF_SHORT_ADDRESS,
               'dstAddrMode': ftdf.FTDF_SHORT_ADDRESS,
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
               'coordAddrMode': ftdf.FTDF_SHORT_ADDRESS,
               'coordPANId': PANId,
               'coordAddr': 0x10,
               'securityLevel': 0,
               'keyIdMode': 0,
               'keySource': [0,0,0,0,0,0,0,0],
               'keyIndex': 0}

msgPURGE_REQ = {'msgId': ftdf.FTDF_PURGE_REQUEST,
                'msduHandle': 0}

msgFPPR_MODE_SET_REQ = {'msgId': ftdf.FTDF_FPPR_MODE_SET_REQUEST,
               'match_fp_value': 0,
               'fp_override': 0,
               'fp_force_value': 0,               
               }

msgSET_metricsEnabled = {
               'msgId': ftdf.FTDF_SET_REQUEST,
               'PIBAttribute': ftdf.FTDF_PIB_METRICS_ENABLED,
               'PIBAttributeValue': True
               }

msgGET_PerformanceMetrics = {
               'msgId': ftdf.FTDF_GET_REQUEST,
               'PIBAttribute': ftdf.FTDF_PIB_PERFORMANCE_METRICS,
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
DTS_setRegister( 1, 0x40090390, 4, 0x24 )
DTS_setRegister( 2, 0x40090390, 4, 0x01 )


# DTS_getRegister( 1, 0x40090048, 4 )
# res, ret = DTS_getMsg( devId1, responseTimeout )
# if (ret['val'] & 0xf000000) != 0x1000000:
#     error("Incorrect result")
#############
# Set PIB attributes
#############

# Short Address
DTS_sndMsg(devId1,msgSET_Dev1_ShortAddress)
DTS_sndMsg(devId2,msgSET_Dev2_ShortAddress)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Incorrect result")

res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Incorrect result")

# PAN ID
DTS_sndMsg(devId1,msgSET_PANId)
DTS_sndMsg(devId2,msgSET_PANId)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Incorrect result")

res, ret = DTS_getMsg(devId2, responseTimeout)
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

############
# Enable FPPR match mode
############
msgFPPR_MODE_SET_REQ['match_fp_value'] = 1
DTS_sndMsg(devId1, msgFPPR_MODE_SET_REQ)

#############
# Set Rx on devId1
#############
DTS_sndMsg(devId1, msgRxEnable_On)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("rxEnable fail")

####################################################################################################
# TC1 - Override FPPR to get FTDFv1 behavior 
####################################################################################################

msgFPPR_MODE_SET_REQ['match_fp_value'] = 0
msgFPPR_MODE_SET_REQ['fp_override'] = 1
msgFPPR_MODE_SET_REQ['fp_force_value'] = 1
DTS_sndMsg(devId1, msgFPPR_MODE_SET_REQ)

#######################
# Poll for no data 
#######################

# Check if FP bit is trully 1 via stats
DTS_sndMsg(devId2, msgGET_PerformanceMetrics)

res, ret = DTS_getMsg(devId2, responseTimeout)

stats1 = ret['PIBAttributeValue']

# Check for no-data result
DTS_sndMsg(devId2, msgPOLL_REQ)

res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_POLL_CONFIRM or ret['status'] != ftdf.FTDF_NO_DATA:
    error("Poll confirm" )

DTS_sndMsg(devId2, msgGET_PerformanceMetrics)

res, ret = DTS_getMsg(devId2, responseTimeout)

stats2 = ret['PIBAttributeValue']

if (stats1['RXSuccessCount'] == stats2['RXSuccessCount']):
    error("Empty data was not successfully received on devId2 (FP bit was 0 instead of 1)")

#######################
# Poll for data, receiving the data means that FP bit is trully 1
#######################

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

#######################
# Poll again for no data to check that everything is clear
#######################

# Check for no-data result
DTS_sndMsg(devId2, msgPOLL_REQ)

res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_POLL_CONFIRM or ret['status'] != ftdf.FTDF_NO_DATA:
    error("Poll confirm" )
    
####################################################################################################
# TC2 - FTDFv2 behavior (auto FP bit)
####################################################################################################

msgFPPR_MODE_SET_REQ['match_fp_value'] = 1
msgFPPR_MODE_SET_REQ['fp_override'] = 0
msgFPPR_MODE_SET_REQ['fp_force_value'] = 0
DTS_sndMsg(devId1, msgFPPR_MODE_SET_REQ)

#######################
# Poll for no data FP bit should be 0
#######################

# Check if FP bit is trully 0 via stats
DTS_sndMsg(devId2, msgGET_PerformanceMetrics)

res, ret = DTS_getMsg(devId2, responseTimeout)

stats1 = ret['PIBAttributeValue']

# Check for no-data result
DTS_sndMsg(devId2, msgPOLL_REQ)

res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_POLL_CONFIRM or ret['status'] != ftdf.FTDF_NO_DATA:
    error("Poll confirm" )

DTS_sndMsg(devId2, msgGET_PerformanceMetrics)

res, ret = DTS_getMsg(devId2, responseTimeout)

stats2 = ret['PIBAttributeValue']

if (stats1['RXSuccessCount'] != stats2['RXSuccessCount']):
    error("Empty data was successfully received on devId2 (FP bit was 1 instead of 0)")

if (stats1['RXExpiredCount'] != stats2['RXExpiredCount']):
    error("devId2 turned on its receiver waiting for data (FP bit was 1 instead of 0)")

#######################
# Poll for data, receiving the data means that FP bit is now 1
#######################

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

#######################
# Poll again for no data to check that everything is clear
#######################

# Check for no-data result
DTS_sndMsg(devId2, msgPOLL_REQ)

res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_POLL_CONFIRM or ret['status'] != ftdf.FTDF_NO_DATA:
    error("Poll confirm" )

#######################
# TC3 - Purge with FTDFv2: Send, Purge, and poll for no data
#######################

msgDATA_REQ['msduHandle'] = 1
msgPURGE_REQ['msduHandle'] = 1

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
    
# Check if FP bit is trully 0 via polling
DTS_sndMsg(devId2, msgGET_PerformanceMetrics)

res, ret = DTS_getMsg(devId2, responseTimeout)

stats1 = ret['PIBAttributeValue']

# Check for no-data result
DTS_sndMsg(devId2, msgPOLL_REQ)

res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_POLL_CONFIRM or ret['status'] != ftdf.FTDF_NO_DATA:
    error("Poll confirm" )
    
DTS_sndMsg(devId2, msgGET_PerformanceMetrics)

res, ret = DTS_getMsg(devId2, responseTimeout)

stats2 = ret['PIBAttributeValue']

if (stats1['RXSuccessCount'] != stats2['RXSuccessCount']):
    error("Empty data was successfully received on devId2 (FP bit was 1 instead of 0)")

if (stats1['RXExpiredCount'] != stats2['RXExpiredCount']):
    error("devId2 turned on its receiver waiting for data (FP bit was 1 instead of 0)")    


####################################################################################################
# TC4 - Forced mode to 0 data will be lost
####################################################################################################

msgFPPR_MODE_SET_REQ['match_fp_value'] = 0
msgFPPR_MODE_SET_REQ['fp_override'] = 1
msgFPPR_MODE_SET_REQ['fp_force_value'] = 0
DTS_sndMsg(devId1, msgFPPR_MODE_SET_REQ)

#######################
# Poll for no data FP bit should be 0
#######################

# Check if FP bit is trully 0 via stats
DTS_sndMsg(devId2, msgGET_PerformanceMetrics)

res, ret = DTS_getMsg(devId2, responseTimeout)

stats1 = ret['PIBAttributeValue']

# Check for no-data result
DTS_sndMsg(devId2, msgPOLL_REQ)

res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_POLL_CONFIRM or ret['status'] != ftdf.FTDF_NO_DATA:
    error("Poll confirm" )

DTS_sndMsg(devId2, msgGET_PerformanceMetrics)

res, ret = DTS_getMsg(devId2, responseTimeout)

stats2 = ret['PIBAttributeValue']

if (stats1['RXSuccessCount'] != stats2['RXSuccessCount']):
    error("Empty data was successfully received on devId2 (FP bit was 1 instead of 0)")

if (stats1['RXExpiredCount'] != stats2['RXExpiredCount']):
    error("devId2 turned on its receiver waiting for data (FP bit was 1 instead of 0)")

#######################
# Poll for data, data will be lost because Rx in devId2 is off
#######################

# Check for successful result
DTS_sndMsg(devId1, msgDATA_REQ)

time.sleep(1)

DTS_sndMsg(devId2, msgPOLL_REQ)

# First comes the poll confirm
res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_POLL_CONFIRM or ret['status'] != ftdf.FTDF_NO_DATA:
    error("Poll confirm" )

# Data confirm on sending side
res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_DATA_CONFIRM or ret['status'] != ftdf.FTDF_NO_ACK or ret['msduHandle'] != msgDATA_REQ['msduHandle']:
    error("Data confirm")


