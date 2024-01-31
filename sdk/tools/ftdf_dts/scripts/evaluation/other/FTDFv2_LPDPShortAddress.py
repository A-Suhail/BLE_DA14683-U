# LPDP test with extended addresses

import sys    #cli arguments
import time    #sleep

from scriptIncludes import *

PANId = 1

msgDATA_REQ_1 = {'msgId': ftdf.FTDF_DATA_REQUEST,
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


msgDATA_REQ_2 = {'msgId': ftdf.FTDF_DATA_REQUEST,
               'srcAddrMode': ftdf.FTDF_SHORT_ADDRESS,
               'dstAddrMode': ftdf.FTDF_SHORT_ADDRESS,
               'dstPANId': PANId,
               'dstAddr': 0x10,
               'msduLength': 5,
               'msdu': [0,1,2,3,4],
               'msduHandle': 0,
               'ackTX': True,
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
DTS_setRegister( 1, 0x40090390, 4, 0x01 )
DTS_setRegister( 2, 0x40090390, 4, 0x01 )

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

# Short Address
DTS_sndMsg(devId1,msgSET_Dev1_ShortAddress)
DTS_sndMsg(devId2,msgSET_Dev2_ShortAddress)

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
# TC1 - no LPDP
####################################################################################################

# Disable LPDP

DTS_getRegister( devId1, 0x40090048, 4 )
res, ret = DTS_getMsg( devId1, responseTimeout )
reg_val = ret['val']
reg_val &= ~(1 << 27)
DTS_setRegister(devId1,  0x40090048, 4, reg_val)

# Check if FP bit is trully 0 via stats
DTS_sndMsg(devId2, msgGET_PerformanceMetrics)

res, ret = DTS_getMsg(devId2, responseTimeout)

stats1 = ret['PIBAttributeValue']


DTS_sndMsg(devId1, msgDATA_REQ_1)

time.sleep(1)

DTS_sndMsg(devId2, msgDATA_REQ_2)

# First comes the data confirm
res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_DATA_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Data confirm" )

# Then nothing
res, ret = DTS_getMsg(devId2, responseTimeout)
if res == True:
    error("Expected no message")
 
# Data indication on the sending side
res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_DATA_INDICATION:
    error("Data indication") 
    
# Wait for indirect Tx expiration on sending side
res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_DATA_CONFIRM or ret['status'] != ftdf.FTDF_TRANSACTION_EXPIRED or ret['msduHandle'] != msgDATA_REQ_1['msduHandle']:
    error("Data confirm")

# Check if FP bit was trully zero
DTS_sndMsg(devId2, msgGET_PerformanceMetrics)

res, ret = DTS_getMsg(devId2, responseTimeout)

stats2 = ret['PIBAttributeValue']

if (stats1['RXExpiredCount'] != stats2['RXExpiredCount']):
    error("devId2 turned on its receiver waiting for data (FP bit was 1 instead of 0)")

####################################################################################################
# TC2 - LPDP
####################################################################################################

# Enable LPDP

DTS_getRegister( 1, 0x40090048, 4 )
res, ret = DTS_getMsg( devId1, responseTimeout )
reg_val = ret['val']
reg_val |= 1 << 27
DTS_setRegister(1,  0x40090048, 4, reg_val)

#######################
# Poll for data, receiving the data means that FP bit is now 1
#######################

DTS_sndMsg(devId1, msgDATA_REQ_1)

time.sleep(1)

DTS_sndMsg(devId2, msgDATA_REQ_2)

# First comes the data confirm
res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_DATA_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Data confirm" )

# Then comes the data indication
res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_DATA_INDICATION:
    error("Data indication")

# Data indication on the sending side
res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_DATA_INDICATION:
    error("Data indication")

# Data confirm on sending side
res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_DATA_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS or ret['msduHandle'] != msgDATA_REQ_1['msduHandle']:
    error("Data confirm")

####################################################################################################
# TC3 - LPDP with burst
####################################################################################################

# for i in range(maxBuffers):
#     msgDATA_REQ_1['msduHandle'] = i
#     DTS_sndMsg(devId1, msgDATA_REQ_1)
#     
# time.sleep(1)
# 
# DTS_sndMsg(devId2, msgDATA_REQ_2)
# 
# # First comes the data confirm
# res, ret = DTS_getMsg(devId2, responseTimeout)
# if ret['msgId'] != ftdf.FTDF_DATA_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
#     error("Poll confirm" )
# 
# # Then comes a burst of data indications
# for i in range(maxBuffers):
#     res, ret = DTS_getMsg(devId2, responseTimeout)
#     if ret['msgId'] != ftdf.FTDF_DATA_INDICATION:
#         error("Data indication")
# 
# # Data indication on the sending side
# res, ret = DTS_getMsg(devId1, responseTimeout)
# if ret['msgId'] != ftdf.FTDF_DATA_INDICATION:
#     error("Data indication")
# 
# # Burst if data confirm on sending side
# for i in range(maxBuffers):
#     res, ret = DTS_getMsg(devId1, responseTimeout)
#     if ret['msgId'] != ftdf.FTDF_DATA_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS or ret['msduHandle'] != i:
#         error("Data confirm")

