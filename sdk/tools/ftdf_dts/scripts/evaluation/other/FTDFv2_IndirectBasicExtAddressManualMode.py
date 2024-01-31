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

# ############
# # Enable FPPR match mode
# ############
# msgFPPR_MODE_SET_REQ['match_fp_value'] = 1
# DTS_sndMsg(devId1, msgFPPR_MODE_SET_REQ)

#############
# Set Rx on devId1
#############
DTS_sndMsg(devId1, msgRxEnable_On)

res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("rxEnable fail")
    
####################################################################################################
# TC1 - FTDFv2 behavior (manual FP bit)
####################################################################################################

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


