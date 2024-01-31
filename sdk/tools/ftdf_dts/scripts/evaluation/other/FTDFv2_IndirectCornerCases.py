# Load-drop 2 Test: Indirect data transactions

import sys    #cli arguments
import time    #sleep
import random
#random.seed(135)

from scriptIncludes import *
from time import sleep

trxExpirationTimeShort  = 460
trxExpirationTimeMedium   = 1500
trxExpirationTimeLong   = 4500

iterationSleepInterval = 0.2

extAddressEntries = 24

shortAddressSeq = [i + 1 for i in range(extAddressEntries * 4)]
shortAddressRand = list(shortAddressSeq)
random.shuffle(shortAddressRand)

extAddressSeq = [i + 1 for i in range(extAddressEntries)]
extAddressRand = list(extAddressSeq)
random.shuffle(extAddressRand)

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
    global trxExpirationTimeLong

    # Wait to make sure that all transactions have expired. 
    time.sleep(trxExpirationTimeLong * 60 * 16 * 16 / 1000000)
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
# TC1: Full table - transaction expiration
####################################################################################################
 
#############################
# Set Transaction persistence time to 1400 (* 60 * 16 * 16) usec
# This time makes sure that no transactions expire before we finish adding frames.
#############################
  
msgSET_TransactionPersistenceTime = { 'msgId': ftdf.FTDF_SET_REQUEST,
                                'PIBAttribute': ftdf.FTDF_PIB_TRANSACTION_PERSISTENCE_TIME,
                                'PIBAttributeValue': trxExpirationTimeMedium }
  
DTS_sndMsg(devId1, msgSET_TransactionPersistenceTime)
res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Incorrect result")
 
#############################
# Fill FPPR, wait for transaction expiration
#############################
msgDATA_REQ['srcAddrMode'] = ftdf.FTDF_SHORT_ADDRESS
msgDATA_REQ['dstAddrMode'] = ftdf.FTDF_SHORT_ADDRESS
 
for i in shortAddressSeq:
    time.sleep(iterationSleepInterval)
    msgDATA_REQ['msduHandle'] = i
    msgDATA_REQ['dstAddr'] = i
    DTS_sndMsg(devId1, msgDATA_REQ)
 
for i in shortAddressSeq:
    res, ret = DTS_getMsg(devId1, responseTimeout)
    if ret['msgId'] != ftdf.FTDF_DATA_CONFIRM or ret['status'] != ftdf.FTDF_TRANSACTION_EXPIRED or ret['msduHandle'] != i:
        error("Data confirm")
 
#############################
# Set Transaction persistence time to trxExpirationTimeShort (* 60 * 16 * 16) usec
# This time makes sure that no transactions expire before we finish adding frames.
#############################
 
msgSET_TransactionPersistenceTime = { 'msgId': ftdf.FTDF_SET_REQUEST,
                                'PIBAttribute': ftdf.FTDF_PIB_TRANSACTION_PERSISTENCE_TIME,
                                'PIBAttributeValue': trxExpirationTimeShort }
  
DTS_sndMsg(devId1, msgSET_TransactionPersistenceTime)
res, ret = DTS_getMsg(devId1, responseTimeout)
  
if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Incorrect result")
 
#############################
# Fill FPPR, wait for transaction expiration
#############################
 
msgDATA_REQ['srcAddrMode'] = ftdf.FTDF_EXTENDED_ADDRESS
msgDATA_REQ['dstAddrMode'] = ftdf.FTDF_EXTENDED_ADDRESS
 
for i in extAddressSeq:
    time.sleep(iterationSleepInterval)
    msgDATA_REQ['msduHandle'] = i
    msgDATA_REQ['dstAddr'] = i
    DTS_sndMsg(devId1, msgDATA_REQ)
 
 
for i in extAddressSeq:
    res, ret = DTS_getMsg(devId1, responseTimeout)
    if ret['msgId'] != ftdf.FTDF_DATA_CONFIRM or ret['status'] != ftdf.FTDF_TRANSACTION_EXPIRED or ret['msduHandle'] != i:
        error("Data confirm")

###################################################################################################
# TC2: Full table - poll for data with random polling
###################################################################################################
#############################
# Set Transaction persistence time to maximum
#############################
 
msgSET_TransactionPersistenceTime = { 'msgId': ftdf.FTDF_SET_REQUEST,
                                'PIBAttribute': ftdf.FTDF_PIB_TRANSACTION_PERSISTENCE_TIME,
                                'PIBAttributeValue': trxExpirationTimeLong }
 
DTS_sndMsg(devId1, msgSET_TransactionPersistenceTime)
res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Incorrect result")
 
#################
# - Poll request for data
#################

msgSET_ShortAddress = { 'msgId': ftdf.FTDF_SET_REQUEST,
                             'PIBAttribute': ftdf.FTDF_PIB_SHORT_ADDRESS,
                             'PIBAttributeValue': 0x0000 }

# Set devId1 short address so that short address is used with the data indication.
msgSET_ShortAddress['PIBAttributeValue'] = 0x10
DTS_sndMsg(devId1, msgSET_ShortAddress)
res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Incorrect result")
 
msgDATA_REQ['srcAddrMode'] = ftdf.FTDF_SHORT_ADDRESS
msgDATA_REQ['dstAddrMode'] = ftdf.FTDF_SHORT_ADDRESS
msgPOLL_REQ['coordAddrMode'] = ftdf.FTDF_SHORT_ADDRESS

for i in shortAddressSeq:
    time.sleep(iterationSleepInterval)
    msgDATA_REQ['msduHandle'] = i
    msgDATA_REQ['dstAddr'] = i
    DTS_sndMsg(devId1, msgDATA_REQ)

for i in shortAddressRand:
    time.sleep(iterationSleepInterval)
    msgSET_ShortAddress['PIBAttributeValue'] = i
    DTS_sndMsg(devId2, msgSET_ShortAddress)
    res, ret = DTS_getMsg(devId2, responseTimeout)
    if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
        error("Incorrect result")
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
    if ret['msgId'] != ftdf.FTDF_DATA_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS or ret['msduHandle'] != i:
        error("Data confirm")
 
 
#################
# - Poll request for data
#################

# Set devId1 short address so that extended address is used with the data indication.
msgSET_ShortAddress['PIBAttributeValue'] = 0xffff
DTS_sndMsg(devId1, msgSET_ShortAddress)
res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Incorrect result")

# Set short address = 0xffff so that extended address is used with the data request command.
msgSET_ShortAddress['PIBAttributeValue'] = 0xffff
DTS_sndMsg(devId2, msgSET_ShortAddress)
res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Incorrect result")

msgDATA_REQ['srcAddrMode'] = ftdf.FTDF_EXTENDED_ADDRESS
msgDATA_REQ['dstAddrMode'] = ftdf.FTDF_EXTENDED_ADDRESS
msgPOLL_REQ['coordAddrMode'] = ftdf.FTDF_EXTENDED_ADDRESS
 
for i in extAddressSeq:
    time.sleep(iterationSleepInterval)
    msgDATA_REQ['msduHandle'] = i
    msgDATA_REQ['dstAddr'] = i
    DTS_sndMsg(devId1, msgDATA_REQ)


msgSET_ExtendedAddress = { 'msgId': ftdf.FTDF_SET_REQUEST,
                                'PIBAttribute': ftdf.FTDF_PIB_EXTENDED_ADDRESS,
                                'PIBAttributeValue': 0x0000000000000000 }
 
for i in extAddressRand:
    time.sleep(iterationSleepInterval)
    msgSET_ExtendedAddress['PIBAttributeValue'] = i
    DTS_sndMsg(devId2, msgSET_ExtendedAddress)
    res, ret = DTS_getMsg(devId2, responseTimeout)
    if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
        error("Incorrect result")
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
    if ret['msgId'] != ftdf.FTDF_DATA_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS or ret['msduHandle'] != i:
        error("Data confirm")

###################################################################################################
# TC3: Full table - poll for data with reversed polling
###################################################################################################
#############################
# Set Transaction persistence time to maximum
#############################
 
msgSET_TransactionPersistenceTime = { 'msgId': ftdf.FTDF_SET_REQUEST,
                                'PIBAttribute': ftdf.FTDF_PIB_TRANSACTION_PERSISTENCE_TIME,
                                'PIBAttributeValue': trxExpirationTimeLong }
 
DTS_sndMsg(devId1, msgSET_TransactionPersistenceTime)
res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Incorrect result")
 
#################
# - Poll request for data
#################

msgSET_ShortAddress = { 'msgId': ftdf.FTDF_SET_REQUEST,
                             'PIBAttribute': ftdf.FTDF_PIB_SHORT_ADDRESS,
                             'PIBAttributeValue': 0x0000 }

# Set devId1 short address so that short address is used with the data indication.
msgSET_ShortAddress['PIBAttributeValue'] = 0x10
DTS_sndMsg(devId1, msgSET_ShortAddress)
res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Incorrect result")
 
msgDATA_REQ['srcAddrMode'] = ftdf.FTDF_SHORT_ADDRESS
msgDATA_REQ['dstAddrMode'] = ftdf.FTDF_SHORT_ADDRESS
msgPOLL_REQ['coordAddrMode'] = ftdf.FTDF_SHORT_ADDRESS

for i in shortAddressSeq:
    time.sleep(iterationSleepInterval)
    msgDATA_REQ['msduHandle'] = i
    msgDATA_REQ['dstAddr'] = i
    DTS_sndMsg(devId1, msgDATA_REQ)
   
for i in reversed(shortAddressSeq):
    time.sleep(iterationSleepInterval)
    msgSET_ShortAddress['PIBAttributeValue'] = i
    DTS_sndMsg(devId2, msgSET_ShortAddress)
    res, ret = DTS_getMsg(devId2, responseTimeout)
    if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
        error("Incorrect result")
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
    if ret['msgId'] != ftdf.FTDF_DATA_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS or ret['msduHandle'] != i:
        error("Data confirm")
 
 
#################
# - Poll request for data
#################

# Set devId1 short address so that extended address is used with the data indication.
msgSET_ShortAddress['PIBAttributeValue'] = 0xffff
DTS_sndMsg(devId1, msgSET_ShortAddress)
res, ret = DTS_getMsg(devId1, responseTimeout)
if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Incorrect result")

# Set short address = 0xffff so that extended address is used with the data request command.
msgSET_ShortAddress['PIBAttributeValue'] = 0xffff
DTS_sndMsg(devId2, msgSET_ShortAddress)
res, ret = DTS_getMsg(devId2, responseTimeout)
if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Incorrect result")

msgDATA_REQ['srcAddrMode'] = ftdf.FTDF_EXTENDED_ADDRESS
msgDATA_REQ['dstAddrMode'] = ftdf.FTDF_EXTENDED_ADDRESS
msgPOLL_REQ['coordAddrMode'] = ftdf.FTDF_EXTENDED_ADDRESS
 
for i in extAddressSeq:
    time.sleep(iterationSleepInterval)
    msgDATA_REQ['msduHandle'] = i
    msgDATA_REQ['dstAddr'] = i
    DTS_sndMsg(devId1, msgDATA_REQ)


msgSET_ExtendedAddress = { 'msgId': ftdf.FTDF_SET_REQUEST,
                                'PIBAttribute': ftdf.FTDF_PIB_EXTENDED_ADDRESS,
                                'PIBAttributeValue': 0x0000000000000000 }
 
for i in reversed(extAddressSeq):
    time.sleep(iterationSleepInterval)
    msgSET_ExtendedAddress['PIBAttributeValue'] = i
    DTS_sndMsg(devId2, msgSET_ExtendedAddress)
    res, ret = DTS_getMsg(devId2, responseTimeout)
    if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
        error("Incorrect result")
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
    if ret['msgId'] != ftdf.FTDF_DATA_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS or ret['msduHandle'] != i:
        error("Data confirm")

