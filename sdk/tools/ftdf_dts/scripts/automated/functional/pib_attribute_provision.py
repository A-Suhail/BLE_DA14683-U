import sys    #cli arguments

from scriptIncludes import *


class errClass:
    def __init__( self ):
        self.errList = []
        self.errCnt  = 0
    def add_err( self, attr, logstr ):
        dtsLog.error( logstr )
        self.errCnt = self.errCnt + 1
        self.errList.append( {'PIBAttribute': attr,
                              'Error': logstr } )
    def __str__( self ):
        msg = 'Nr of errors: ' + str( self.errCnt ) + '\n'
        atr = 0

        for i in range( self.errCnt ):
            if atr != self.errList[ i ]['PIBAttribute']:
                msg = msg + 'PIBAttribute: ' + str( self.errList[ i ]['PIBAttribute'] ) + '\n'

            atr = self.errList[ i ]['PIBAttribute']
            msg = msg + '- Error     : ' + str( self.errList[ i ]['Error'] ) + '\n'

        if self.errCnt == 0:
            msg = 'SCRIPT: PASSED'
        else:
            msg = msg + 'SCRIPT: FAILED'

        return msg

err = errClass( )

def error( logstr ):
    raise StopScript( logstr )

def PIB_set_get( msgGet, msgSet, val1, val2, default={0} ):
    # Default value
    if default != {0}:
        DTS_sndMsg(1, msgGet)

        res, ret = DTS_getMsg(1, 5)
        if ret['msgId'] != ftdf.FTDF_GET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS or ret['PIBAttribute'] != msgGet['PIBAttribute'] or ret['PIBAttributeValue'] != default:
            err.add_err(msgGet['PIBAttribute'],"Default value not correct")

    # min and max
    for i in range( 2 ):
        if i == 0:
            msgSet['PIBAttributeValue'] = val1
        else:
            msgSet['PIBAttributeValue'] = val2

        DTS_sndMsg(1, msgSet)

        res, ret = DTS_getMsg(1, 5)
        if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS or ret['PIBAttribute'] != msgSet['PIBAttribute']:
            err.add_err(msgSet['PIBAttribute'],"Set confirm")

        DTS_sndMsg(1, msgGet)

        res, ret = DTS_getMsg(1, 5)
        if ret['msgId'] != ftdf.FTDF_GET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS or ret['PIBAttribute'] != msgGet['PIBAttribute'] or ret['PIBAttributeValue'] != msgSet['PIBAttributeValue']:
            err.add_err(msgGet['PIBAttribute'],"Get confirm")


def PIB_get_only( msgGet, msgSet, val ):
    #msgSet['PIBAttributeValue'] = 0
    msgSet['PIBAttributeValue'] = val

    DTS_sndMsg(1, msgSet)

    res, ret = DTS_getMsg(1, 5)
    if ret['msgId'] != ftdf.FTDF_SET_CONFIRM or ret['status'] != ftdf.FTDF_READ_ONLY or ret['PIBAttribute'] != msgSet['PIBAttribute']:
        err.add_err(msgSet['PIBAttribute'],"Attribute should be read only")

    DTS_sndMsg(1, msgGet)

    res, ret = DTS_getMsg(1, 5)
    if ret['msgId'] != ftdf.FTDF_GET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS or ret['PIBAttribute'] != msgGet['PIBAttribute'] or ret['PIBAttributeValue'] != val:
        err.add_err(msgGet['PIBAttribute'],"Default value not correct")



# Begin with reset request
DTS_sndMsg(devId1, msgRESET)
res, ret = DTS_getMsg(devId1, responseTimeout)
if res == False:
    error("No response")
elif ret['msgId'] != ftdf.FTDF_RESET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Incorrect result")


# PR1000 - MAC constants
if ftdf.FTDF_BASE_SLOT_DURATION != 60:
    error("FTDF_BASE_SLOT_DURATION")
elif ftdf.FTDF_BASE_SUPERFRAME_DURATION != 960:
    error("FTDF_BASE_SUPERFRAME_DURATION")
elif ftdf.FTDF_MAX_BEACON_OVERHEAD != 75:
    error("FTDF_MAX_BEACON_OVERHEAD")
elif ftdf.FTDF_MAX_BEACON_PAYLOAD_LENGTH != 52:
    error("FTDF_MAX_BEACON_PAYLOAD_LENGTH")
elif ftdf.FTDF_MAX_LOST_BEACONS != 4:
    error("FTDF_MAX_LOST_BEACONS")
elif ftdf.FTDF_MAX_PAYLOAD_SIZE != 118:
    error('FTDF_MAX_PAYLOAD_SIZE')
elif ftdf.FTDF_MAX_MAC_SAFE_PAYLOAD_SIZE != 102:
    error('FTDF_MAX_MAC_SAFE_PAYLOAD_SIZE')
elif ftdf.FTDF_MAX_MPDU_UNSECURED_OVERHEAD != 25:
    error('FTDF_MAX_MPDU_UNSECURED_OVERHEAD')
elif ftdf.FTDF_MAX_PHY_PACKET_SIZE != 127:
    error('FTDF_MAX_PHY_PACKET_SIZE')
elif ftdf.FTDF_MAX_SIFS_FRAME_SIZE != 18:
    error('FTDF_MAX_SIFS_FRAME_SIZE')
elif ftdf.FTDF_MIN_MPDU_OVERHEAD != 9:
    error('FTDF_MIN_MPDU_OVERHEAD')

# Loop over PIB attributes
for j in range( ftdf.FTDF_NR_OF_PIB_ATTRIBUTES ):
    i = j + 1

    msgGet['PIBAttribute'] = i
    msgSet['PIBAttribute'] = i

    if i == ftdf.FTDF_PIB_EXTENDED_ADDRESS:
        # PR2000
        PIB_set_get( msgGet, msgSet, 0, 0xffffffffffffffff )
    elif i == ftdf.FTDF_PIB_SHORT_ADDRESS:
        # PR2020
        PIB_set_get( msgGet, msgSet, 0, 0xffff, 0xffff )
    elif i == ftdf.FTDF_PIB_PAN_ID:
        # PR2040
        PIB_set_get( msgGet, msgSet, 0, 0xffff, 0xffff )
    elif i == ftdf.FTDF_PIB_COORD_EXTENDED_ADDRESS:
        # PR2060
        PIB_set_get( msgGet, msgSet, 0, 0xffffffffffffffff )
    elif i == ftdf.FTDF_PIB_COORD_SHORT_ADDRESS:
        # PR2080
        PIB_set_get( msgGet, msgSet, 0, 0xffff, 0xffff )
    elif i == ftdf.FTDF_PIB_IMPLICIT_BROADCAST:
        # PR2100
        PIB_set_get( msgGet, msgSet, True, False, False )
    elif i == ftdf.FTDF_PIB_ACK_WAIT_DURATION:
        # PR2500
        PIB_get_only( msgGet, msgSet, 54 )
    elif i == ftdf.FTDF_PIB_ENH_ACK_WAIT_DURATION:
        # PR2520
        PIB_set_get( msgGet, msgSet, 0, 0xffff, 864 )
    elif i == ftdf.FTDF_PIB_MAX_FRAME_TOTAL_WAIT_TIME:
        # PR2540
        PIB_set_get( msgGet, msgSet, 0, 0xffff )
    elif i == ftdf.FTDF_PIB_RESPONSE_WAIT_TIME:
        # PR2560
        PIB_set_get( msgGet, msgSet, 2, 64, 32 )
    elif i == ftdf.FTDF_PIB_TRANSACTION_PERSISTENCE_TIME:
        # PR2580
        PIB_set_get( msgGet, msgSet, 0, 0xffff, 500 )
    elif i == ftdf.FTDF_PIB_RX_ON_WHEN_IDLE:
        # PR2600
        PIB_set_get( msgGet, msgSet, True, False, False )
    elif i == ftdf.FTDF_PIB_KEEP_PHY_ENABLED:
        # PR2620
        PIB_set_get( msgGet, msgSet, True, False, False )
    elif i == ftdf.FTDF_PIB_CCA_MODE:
        # PR3000
        PIB_set_get( msgGet, msgSet, 4, 1, 1 )
    elif i == ftdf.FTDF_PIB_MAX_BE:
        # PR3020
        PIB_set_get( msgGet, msgSet, 3, 8, 5 )
    elif i == ftdf.FTDF_PIB_MIN_BE:
        # PR3040
        PIB_set_get( msgGet, msgSet, 0, 5, 3 )
    elif i == ftdf.FTDF_PIB_MAX_CSMA_BACKOFFS:
        # PR3060
        PIB_set_get( msgGet, msgSet, 0, 5, 4 )
    elif i == ftdf.FTDF_PIB_MAX_FRAME_RETRIES:
        # PR3080
        PIB_set_get( msgGet, msgSet, 0, 7, 3 )
    elif i == ftdf.FTDF_PIB_SIFS_PERIOD:
        # PR3500
        PIB_get_only( msgGet, msgSet, 12 )
    elif i == ftdf.FTDF_PIB_LIFS_PERIOD:
        # PR3520
        PIB_get_only( msgGet, msgSet, 40 )
    elif i == ftdf.FTDF_PIB_DSN:
        # PR3540
        PIB_set_get( msgGet, msgSet, 0, 255 )
    elif i == ftdf.FTDF_PIB_BSN:
        # PR3560
        PIB_set_get( msgGet, msgSet, 0, 255 )
    elif i == ftdf.FTDF_PIB_EBSN:
        # PR3580
        PIB_set_get( msgGet, msgSet, 0, 255 )
    elif i == ftdf.FTDF_PIB_AUTO_REQUEST:
        # PR3600
        PIB_set_get( msgGet, msgSet, False, True, True )
    elif i == ftdf.FTDF_PIB_GTS_PERMIT:
        # PR3620
        PIB_get_only( msgGet, msgSet, False )
    elif i == ftdf.FTDF_PIB_PROMISCUOUS_MODE:
        # PR3700
        PIB_set_get( msgGet, msgSet, True, False, False )
    elif i == ftdf.FTDF_PIB_SECURITY_ENABLED:
        # PR4000
        PIB_set_get( msgGet, msgSet, True, False, False )
    elif i == ftdf.FTDF_PIB_FRAME_COUNTER:
        # PR4020
        PIB_set_get( msgGet, msgSet, 0, 0xffffffff, 0 )
    elif i == ftdf.FTDF_PIB_FRAME_COUNTER_MODE:
        # PR4040
        PIB_set_get( msgGet, msgSet, 5, 4, 4 )
    elif i == ftdf.FTDF_PIB_KEY_TABLE:
        # PR4100
        # PR4120
        # PR4140
        # PR4160
        # PR4180
        keyIdLookupD = {'keyIdMode': 3,
                        'keySource': [1,2,3,4,8,7,6,5],
                        'keyIndex': 3,
                        'deviceAddrMode': ftdf.FTDF_EXTENDED_ADDRESS,
                        'devicePANId': 0xffff,
                        'deviceAddress': 0x20}
        keyUsageD = {'frameType': ftdf.FTDF_DATA_FRAME,
                     'commandFrameId': 0}

        val = {'nrOfKeyDescriptors': 1,
               'keyDescriptors': [{'nrOfKeyIdLookupDescriptors': 1,
                                   'keyIdLookupDescriptors': [keyIdLookupD],
                                   'nrOfDeviceDescriptorHandles': 0,
                                   'deviceDescriptorHandles': [],
                                   'nrOfKeyUsageDescriptors': 1,
                                   'keyUsageDescriptors': [keyUsageD],
                                   'key': [1,2,3,4,5,6,7,8,9,1,2,3,4,5,6,7]}] }

        PIB_set_get( msgGet, msgSet, val, val )
    elif i == ftdf.FTDF_PIB_DEVICE_TABLE:
        # PR4200
        val = {'nrOfDeviceDescriptors': 1,
               'deviceDescriptors': [{'PANId': 0xffff,
                                      'shortAddress': 0xffff,
                                      'extAddress': 0xffffffffffffffff,
                                      'frameCounter': 0xffffffffffffffff,
                                      'exempt': True}]}

        PIB_set_get( msgGet, msgSet, val, val )
    elif i == ftdf.FTDF_PIB_SECURITY_LEVEL_TABLE:
        # PR4220
        val = {'nrOfSecurityLevelDescriptors': 1,
               'securityLevelDescriptors': [{'frameType': ftdf.FTDF_BEACON_FRAME,
                                             'commandFrameId': 1,
                                             'securityMinimum': 0,
                                             'deviceOverrideSecurityMinimum': False,
                                             'allowedSecurityLevels': 2}]}

        PIB_set_get( msgGet, msgSet, val, val )
    elif i == ftdf.FTDF_PIB_DEFAULT_KEY_SOURCE:
        # PR4240
        PIB_set_get( msgGet, msgSet, [0,0,0,0,0,0,0,0], [0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff], [0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff] )
    elif i == ftdf.FTDF_PIB_PAN_COORD_EXTENDED_ADDRESS:
        # PR4260
        PIB_set_get( msgGet, msgSet, 0, 0xffffffffffffffff )
    elif i == ftdf.FTDF_PIB_PAN_COORD_SHORT_ADDRESS:
        # PR4280
        PIB_set_get( msgGet, msgSet, 0, 0xffff, 0 )
    elif i == ftdf.FTDF_PIB_MT_DATA_SECURITY_LEVEL:
        # PR4300
        PIB_set_get( msgGet, msgSet, 7, 0, 0 )
    elif i == ftdf.FTDF_PIB_MT_DATA_KEY_ID_MODE:
        # PR4320
        PIB_set_get( msgGet, msgSet, 0, 3 )
    elif i == ftdf.FTDF_PIB_MT_DATA_KEY_SOURCE:
        # PR4340
        PIB_set_get( msgGet, msgSet, [0,0,0,0,0,0,0,0], [0xff,0xff,0xff,0xff,0xff,0xff,0xff,0xff] )
    elif i == ftdf.FTDF_PIB_MT_DATA_KEY_INDEX:
        # PR4360
        PIB_set_get( msgGet, msgSet, 0, 0xff )
    elif i == ftdf.FTDF_PIB_ASSOCIATION_PAN_COORD:
        # PR4500
        PIB_set_get( msgGet, msgSet, True, False, False )
    elif i == ftdf.FTDF_PIB_ASSOCIATION_PERMIT:
        # PR4520
        PIB_set_get( msgGet, msgSet, True, False, False )
    elif i == ftdf.FTDF_PIB_LE_CAPABLE:
        # PR5000
        PIB_get_only( msgGet, msgSet, True )
    elif i == ftdf.FTDF_PIB_LE_ENABLED:
        # PR5020
        PIB_set_get( msgGet, msgSet, True, False, False )
    elif i == ftdf.FTDF_PIB_CSL_CHANNEL_MASK:
        # PR5040
        PIB_set_get( msgGet, msgSet, 0, 0xffffffff, 0 )
    elif i == ftdf.FTDF_PIB_CSL_PERIOD:
        # PR5060
        PIB_set_get( msgGet, msgSet, 0, 0xffff, 0 )
    elif i == ftdf.FTDF_PIB_CSL_MAX_PERIOD:
        # PR5080
        PIB_set_get( msgGet, msgSet, 0, 0xffff, 0 )
    elif i == ftdf.FTDF_PIB_CSL_FRAME_PENDING_WAIT_T:
        # PR5140
        PIB_set_get( msgGet, msgSet, 278, 0xffff )
    elif i == ftdf.FTDF_PIB_CSL_SYNC_TX_MARGIN:
        # PR5160
        PIB_set_get( msgGet, msgSet, 0, 0xffff )
    elif i == ftdf.FTDF_PIB_CSL_MAX_AGE_REMOTE_INFO:
        # PR5180
        PIB_set_get( msgGet, msgSet, 0, 0xffff )
    elif i == ftdf.FTDF_PIB_EB_IE_LIST:    
      val = {'nrOfIEs': 1, 'IEs': [{'ID': 1, 'length': 4, 'content': {'nrOfSubIEs': 1, 'subIEs': [{'type': 1, 'subID': 1, 'length': 3, 'subContent': [0,1,2]}]}}]}      
      
      PIB_set_get( msgGet, msgSet, val, val )
    elif i == ftdf.FTDF_PIB_EACK_IE_LIST:    
      val = {'nrOfIEs': 1, 'IEs': [{'ID': 1, 'length': 4, 'content': {'nrOfSubIEs': 1, 'subIEs': [{'type': 1, 'subID': 1, 'length': 3, 'subContent': [0,1,2]}]}}]}       
      PIB_set_get( msgGet, msgSet, val, val )       
    elif i == ftdf.FTDF_PIB_DISCONNECT_TIME:
        # PR5550
        PIB_set_get( msgGet, msgSet, 0, 65535 )     
    elif i == ftdf.FTDF_PIB_JOIN_PRIORITY:
        # PR5560
        PIB_set_get( msgGet, msgSet, 0, 63 ) 
    elif i == ftdf.FTDF_PIB_ASN:
        # PR5570
        PIB_set_get( msgGet, msgSet, 0, 0xff ) 
    elif i == ftdf.FTDF_PIB_NO_HL_BUFFERS:
        # PR5580
        PIB_set_get( msgGet, msgSet, False, False ) 
    elif i == ftdf.FTDF_PIB_SLOTFRAME_TABLE:
        # PR5600, PR5610
        val = {'nrOfSlotframes': 0,
               'slotframeEntries': []}
        PIB_get_only( msgGet, msgSet, val )
    elif i == ftdf.FTDF_PIB_LINK_TABLE:
        # PR5630, PR5640, PR5650, PR5660, PR5670, PR5680, PR5690
        # PR5700, PR5710, PR5720, PR5730, PR5740, PR5750, PR5760
        # PR5770, PR5780, PR5790, PR5800, PR5810, PR5820        
        val = {'nrOfLinks': 0,
               'linkEntries':  []}
        PIB_get_only( msgGet, msgSet, val )     
    elif i == ftdf.FTDF_PIB_TS_SYNC_CORRECT_THRESHOLD:
        # PR5890
        PIB_set_get( msgGet, msgSet, 0, 0xff )            
    elif i == ftdf.FTDF_PIB_BO_IRQ_THRESHOLD:
        # PR5890
        PIB_set_get( msgGet, msgSet, 0, 0xff )       
    elif i == ftdf.FTDF_PIB_BEACON_ORDER:
        # PR6000
        PIB_get_only( msgGet, msgSet, 15 )
    elif i == ftdf.FTDF_PIB_SUPERFRAME_ORDER:
        # PR6020
        PIB_get_only( msgGet, msgSet, 15 )
    elif i == ftdf.FTDF_PIB_BEACON_PAYLOAD:
        # PR6040
        tmp1 = []
        tmp2 = []
        for y in range( 52 ):
            tmp1.append( 0 )
            tmp2.append( 0xff )
        PIB_set_get( msgGet, msgSet, tmp1, tmp2 )
    elif i == ftdf.FTDF_PIB_BEACON_PAYLOAD_LENGTH:
        # PR6060
        PIB_set_get( msgGet, msgSet, 0, 52, 0 )
        
        
    elif i == ftdf.FTDF_PIB_EB_FILTERING_ENABLED:
        # PR6220
        PIB_set_get( msgGet, msgSet, True, False )
    elif i == ftdf.FTDF_PIB_EB_AUTO_SA:
        # PR6240
        PIB_set_get( msgGet, msgSet, ftdf.FTDF_AUTO_NONE, ftdf.FTDF_AUTO_SHORT, ftdf.FTDF_AUTO_FULL )
    elif i == ftdf.FTDF_PIB_METRICS_CAPABLE:
        # PR7000
        PIB_get_only( msgGet, msgSet, True )
    elif i == ftdf.FTDF_PIB_METRICS_ENABLED:
        # PR7020
        PIB_set_get( msgGet, msgSet, False, True, False )
    elif i == ftdf.FTDF_PIB_PERFORMANCE_METRICS:
        # PR7100 - PR7280
        val = {'counterOctets': 4,
               'retryCount': 0,
               'multipleRetryCount': 0,
               'TXFailCount': 0,
               'TXSuccessCount': 0,
               'FCSErrorCount': 0,
               'securityFailureCount': 0,
               'duplicateFrameCount': 0,
               'RXSuccessCount': 0,
               'NACKCount': 0,
               'RXExpiredCount': 0, 
               'BOIrqCount': 0 }

        PIB_set_get( msgGet, msgSet, val, val )
    elif i == ftdf.FTDF_PIB_TRAFFIC_COUNTERS:
        # PR7300 - PR7480
        val = {'txDataFrmCnt': 0,
               'txCmdFrmCnt': 0,
               'txStdAckFrmCnt': 0,
               'txEnhAckFrmCnt': 0,
               'txBeaconFrmCnt': 0,
               'txMultiPurpFrmCnt': 0,
               'rxDataFrmOkCnt': 0,
               'rxCmdFrmOkCnt': 0,
               'rxStdAckFrmOkCnt': 0,
               'rxEnhAckFrmOkCnt': 0,
               'rxBeaconFrmOkCnt': 0,
               'rxMultiPurpFrmOkCnt': 0 }

        PIB_get_only( msgGet, msgSet, val )
    elif i == ftdf.FTDF_PIB_LL_CAPABLE:
        # PR9000
        PIB_get_only( msgGet, msgSet, False )
    elif i == ftdf.FTDF_PIB_DSME_CAPABLE:
        # PR9020
        PIB_get_only( msgGet, msgSet, False )
    elif i == ftdf.FTDF_PIB_RFID_CAPABLE:
        # PR9040
        PIB_get_only( msgGet, msgSet, False )
    elif i == ftdf.FTDF_PIB_AMCA_CAPABLE:
        # PR9060
        PIB_get_only( msgGet, msgSet, False )
    elif i == ftdf.FTDF_PIB_RANGING_SUPPORTED:
        # PR9080
        PIB_get_only( msgGet, msgSet, False )
    elif i == ftdf.FTDF_PIB_TIMESTAMP_SUPPORTED:
        # PR9100
        PIB_get_only( msgGet, msgSet, True )

if str(err) != 'SCRIPT: PASSED':
    raise StopScript( 'SCRIPT: FAILED' )
