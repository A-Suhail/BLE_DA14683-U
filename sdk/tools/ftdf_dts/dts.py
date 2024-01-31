####################################################################################################
#
# @file dts.py
#
# @brief DTS main Python script
#
# Copyright (C) 2015 Dialog Semiconductor.
# This computer program includes Confidential, Proprietary Information
# of Dialog Semiconductor. All Rights Reserved.
#
####################################################################################################

import sys, time, logging, traceback, dtsparam, serial, threading, ftdf
from queue import Queue

class StopScript(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)

class PerformanceResults(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)

#############################
# UART
#############################
DTS_serList  = {} # Dictionary of serial.Serial items per port
DTS_serQueue = {} # Dictionary of Queue items per port
DTS_ackQueue = {} # Dictionary of Queue items per port for acks
DTS_thrList  = {} # Dictionary of UART rcv threads per port

def DTS_calcXor( data ):
    xor = 0
    for i in range( len( data ) ):
        xor ^= data[i]
    return xor

class DTS_uartThread( threading.Thread ):
    def __init__(self, comId):
        threading.Thread.__init__(self)
        self.comId    = comId
        self.stopflag = threading.Event()
        self.rawhdr   = b''
    def stop(self):
        self.stopflag.set( )
    def run(self):
        first    = True
        msglen   = 0
        uarttype = ftdf.UART_HDR_TYPE_FTDF
        while self.stopflag.is_set( ) == False:
            if first:
                # First=True => get the length
                self.rawhdr = DTS_serList[ self.comId ].read( 4 )

                if len(self.rawhdr) == 0:
                    continue
                elif len(self.rawhdr) == 4:
                    msghdr    = int.from_bytes( self.rawhdr, 'little' )
                    startflag = ( msghdr >> 24 ) & 0xff

                    if startflag != ftdf.UART_START_FLAG:
                        continue

                    uarttype = ( msghdr >> 16 ) & 0xff
                    msglen   = msghdr & 0xffff
                    first    = False
                    continue
                else:
                    lenleft = 4 - len(self.rawhdr)
                    rawhdr2 = DTS_serList[ self.comId ].read( lenleft )

                    if len(rawhdr2) != lenleft:
                        # Something went wrong
                        continue
                    else:
                        self.rawhdr = b"".join([self.rawhdr, rawhdr2])

                        msghdr    = int.from_bytes( self.rawhdr, 'little' )
                        startflag = ( msghdr >> 24 ) & 0xff

                        if startflag != ftdf.UART_START_FLAG:
                            continue

                        uarttype = ( msghdr >> 16 ) & 0xff
                        msglen   = msghdr & 0xffff
                        first    = False
                        continue
            else:
                # First=False => get the msg
                rawmsg = DTS_serList[ self.comId ].read( msglen - 4 )

                if len(rawmsg) != msglen - 4:
                    # Something went wrong, start over
                    first = True
                    continue
                else:
                    # check checksum
                    uart_data = b''.join( [self.rawhdr,rawmsg[:len(rawmsg)-1]] )
                    uart_xor  = rawmsg[ len(rawmsg) - 1 ]
                    calc_xor  = DTS_calcXor( uart_data )

                    if uart_dbg:
                        print('(' + str(self.comId) + ') UART RX data : ' + str(b''.join([self.rawhdr,rawmsg])))

                    if uart_xor != calc_xor:
                        # checksum mismatch
                        first = True
                        continue

                    if uarttype == ftdf.UART_HDR_TYPE_FTDF:
                        # Put raw msg w/o chsum in the queue
                        DTS_serQueue[ self.comId ].put( rawmsg[:len(rawmsg)-1] )
                        first = True
                        continue
                    elif uarttype == ftdf.UART_HDR_TYPE_ACK:
                        # Put ack msg in queue
                        DTS_ackQueue[ self.comId ].put( rawmsg[:len(rawmsg)-1] )
                        first = True
                        continue
                    else: # BLE
                        first = True
                        continue


def DTS_waitForAck( comId ):
    # wait for ack
    try:
        qitem = DTS_ackQueue[ comId ].get( block=True, timeout=5 )
    except:
        dtsLog.info( 'No uart ack rcvd, retrying' )
        return False

    DTS_ackQueue[ comId ].task_done( )
    return True

def DTS_sndToUart( comId, tmpList ):
    if not comId in DTS_serList.keys( ):
        return

    uarttype = ftdf.UART_HDR_TYPE_FTDF
    length   = 0

    for i in tmpList:
        length = length + len( i )

    length += 5

    hdr      = ( ftdf.UART_START_FLAG << 24 ) | ( uarttype << 16 ) | length
    hdr      = hdr.to_bytes( 4, 'little' )
    rawbytes = b"".join( tmpList )
    data     = b"".join( [hdr, rawbytes] )
    xor      = DTS_calcXor( data )
    data     = b"".join( [data, xor.to_bytes( 1, 'little' )] )

    if uart_dbg:
        print('(' + str(comId) + ') UART TX data: ' + str(data))

    # retry maximum 3 times
    for i in range( 3 ):
        # write data to serial
        DTS_serList[ comId ].write( data )

        ack = DTS_waitForAck( comId )

        if ack:
            break


def DTS_openPort( comId, port, extAddress ):
    if comId in DTS_serList.keys( ):
        return False

    try:
        DTS_serList[ comId ] = serial.Serial( port, 115200, timeout=1 )
    except:
        if comId in DTS_serList.keys( ):
            del DTS_serList[ comId ]
        return False

    DTS_serQueue[ comId ] = Queue()
    DTS_ackQueue[ comId ] = Queue()
    DTS_thrList[ comId ]  = DTS_uartThread( comId )
    DTS_thrList[ comId ].start( )

    # set extended address via DTS target API
    data = []
    data.append( [ftdf.DTS_MSG_ID_SET_EXT_ADDR, 4] )
    data.append( [extAddress, 8 ] )

    data = DTS_setParams( data )
    DTS_sndToUart( comId, data )
    return True

def DTS_closePort( comId ):
    if comId in DTS_serList.keys( ):
        DTS_thrList[ comId ].stop( )
        DTS_thrList[ comId ].join( 5 )

        if DTS_thrList[ comId ].is_alive( ):
            print( 'Unable to stop UART rcv thread!' )

        DTS_serList[ comId ].close( )

        del DTS_thrList[ comId ]
        del DTS_serQueue[ comId ]
        del DTS_ackQueue[ comId ]
        del DTS_serList[ comId ]

def DTS_closeAllPorts( ):
    while True:
        try:
            i = list( DTS_serList.keys( ) )[0]
            DTS_closePort( i )
        except:
            return


#############################
# HELPER FUNCTIONS
#############################
def DTS_getDeviceTable( bs ):
    devDes = []
    be     = 0

    nrOfDeviceDescriptors = int.from_bytes( bs[be:be+4], 'little' )
    be = be + 4

    for i in range( nrOfDeviceDescriptors ):
        devDes.append( {'PANId'       : int.from_bytes( bs[be:be+4], 'little' ),
                        'shortAddress': int.from_bytes( bs[be+4:be+8], 'little' ),
                        'extAddress'  : int.from_bytes( bs[be+8:be+16], 'little' ),
                        'frameCounter': int.from_bytes( bs[be+16:be+24], 'little' ),
                        'exempt'      : int.from_bytes( bs[be+24:be+28], 'little' ) } )
        be = be + 28

    return {'nrOfDeviceDescriptors': nrOfDeviceDescriptors, 'deviceDescriptors': devDes }


def DTS_setDeviceTable( val ):
    tmpList = []
    tmpList.append( val['nrOfDeviceDescriptors'].to_bytes( 4, 'little' ) )

    for i in range( val['nrOfDeviceDescriptors'] ):
        subVal = val['deviceDescriptors'][i]

        tmpList.append( subVal['PANId'].to_bytes( 4, 'little' ) )
        tmpList.append( subVal['shortAddress'].to_bytes( 4, 'little' ) )
        tmpList.append( subVal['extAddress'].to_bytes( 8, 'little' ) )
        tmpList.append( subVal['frameCounter'].to_bytes( 8, 'little' ) )
        tmpList.append( subVal['exempt'].to_bytes( 4, 'little' ) )

    return b''.join( tmpList )


def DTS_getSecurityLevelTable( bs ):
    secDes = []
    be     = 0

    nrOfSecurityLevelDescriptors = int.from_bytes( bs[be:be+4], 'little' )
    be = be + 4

    for i in range( nrOfSecurityLevelDescriptors ):
        secDes.append( {'frameType'                    : int.from_bytes( bs[be:be+4], 'little' ),
                        'commandFrameId'               : int.from_bytes( bs[be+4:be+8], 'little' ),
                        'securityMinimum'              : int.from_bytes( bs[be+8:be+12], 'little' ),
                        'deviceOverrideSecurityMinimum': int.from_bytes( bs[be+12:be+16], 'little' ),
                        'allowedSecurityLevels'        : int.from_bytes( bs[be+16:be+20], 'little' ) } )
        be = be + 20

    return {'nrOfSecurityLevelDescriptors': nrOfSecurityLevelDescriptors,
            'securityLevelDescriptors': secDes}


def DTS_setSecurityLevelTable( val ):
    tmpList = []
    tmpList.append( val['nrOfSecurityLevelDescriptors'].to_bytes( 4, 'little' ) )

    for i in range( val['nrOfSecurityLevelDescriptors'] ):
        subVal = val['securityLevelDescriptors'][i]

        tmpList.append( subVal['frameType'].to_bytes( 4, 'little' ) )
        tmpList.append( subVal['commandFrameId'].to_bytes( 4, 'little' ) )
        tmpList.append( subVal['securityMinimum'].to_bytes( 4, 'little' ) )
        tmpList.append( subVal['deviceOverrideSecurityMinimum'].to_bytes( 4, 'little' ) )
        tmpList.append( subVal['allowedSecurityLevels'].to_bytes( 4, 'little' ) )

    return b''.join( tmpList )


def DTS_getKeyTable( bs ):
    keyDes = []
    be     = 0

    nrOfKeyDescriptors = int.from_bytes( bs[be:be+4], 'little' )
    be = be + 4

    for i in range( nrOfKeyDescriptors ):
        nrOfKeyIdLookupDescriptors = int.from_bytes( bs[be:be+4], 'little' )
        be    = be + 4
        idDes = []

        for j in range( nrOfKeyIdLookupDescriptors ):
            keyIdMode = int.from_bytes( bs[be:be+4], 'little' )
            be        = be + 4
            keySource = []

            for k in range( 8 ):
                keySource.append( int.from_bytes( bs[be:be+1], 'little' ) )
                be = be + 1

            keyIndex       = int.from_bytes( bs[be:be+4], 'little' )
            deviceAddrMode = int.from_bytes( bs[be+4:be+8], 'little' )
            devicePANId    = int.from_bytes( bs[be+8:be+12], 'little' )
            deviceAddr     = int.from_bytes( bs[be+12:be+20], 'little' )
            be             = be + 20

            idDes.append( {'keyIdMode'      : keyIdMode,
                           'keySource'      : keySource,
                           'keyIndex'       : keyIndex,
                           'deviceAddrMode' : deviceAddrMode,
                           'devicePANId'    : devicePANId,
                           'deviceAddress'  : deviceAddr} )

        nrOfDeviceDescriptorHandles = int.from_bytes( bs[be:be+4], 'little' )
        be     = be + 4
        devDes = []

        for j in range( nrOfDeviceDescriptorHandles ):
            devDes.append( int.from_bytes( bs[be:be+4], 'little' ) )
            be = be + 4

        nrOfKeyUsageDescriptors = int.from_bytes( bs[be:be+4], 'little' )
        be    = be + 4
        usDes = []

        for j in range( nrOfKeyUsageDescriptors ):
            usDes.append( {'frameType'     : int.from_bytes( bs[be:be+4], 'little' ),
                           'commandFrameId': int.from_bytes( bs[be+4:be+8], 'little' ) })
            be = be + 8

        key = []
        for j in range( 16 ):
            key.append( int.from_bytes( bs[be:be+1], 'little' ) )
            be = be + 1

        keyDes.append( {'nrOfKeyIdLookupDescriptors' : nrOfKeyIdLookupDescriptors,
                        'keyIdLookupDescriptors'     : idDes,
                        'nrOfDeviceDescriptorHandles': nrOfDeviceDescriptorHandles,
                        'deviceDescriptorHandles'    : devDes,
                        'nrOfKeyUsageDescriptors'    : nrOfKeyUsageDescriptors,
                        'keyUsageDescriptors'        : usDes,
                        'key'                        : key} )

    return {'nrOfKeyDescriptors': nrOfKeyDescriptors, 'keyDescriptors': keyDes}


def DTS_setKeyTable( val ):
    tmpList = []
    tmpList.append( val['nrOfKeyDescriptors'].to_bytes( 4, 'little' ) )

    for i in range( val['nrOfKeyDescriptors'] ):
        tmpList.append( val['keyDescriptors'][i]['nrOfKeyIdLookupDescriptors'].to_bytes( 4, 'little' ) )

        for j in range( val['keyDescriptors'][i]['nrOfKeyIdLookupDescriptors'] ):
            subVal = val['keyDescriptors'][i]['keyIdLookupDescriptors'][j]

            tmpList.append( subVal['keyIdMode'].to_bytes( 4, 'little' ) )

            for k in range( 8 ):
                if k < len( subVal['keySource'] ):
                    tmpList.append( subVal['keySource'][k].to_bytes( 1, 'little' ) )
                else:
                    tmpList.append( int(0).to_bytes( 1, 'little' ) )

            tmpList.append( subVal['keyIndex'].to_bytes( 4, 'little' ) )
            tmpList.append( subVal['deviceAddrMode'].to_bytes( 4, 'little' ) )
            tmpList.append( subVal['devicePANId'].to_bytes( 4, 'little' ) )
            tmpList.append( subVal['deviceAddress'].to_bytes( 8, 'little' ) )

        tmpList.append( val['keyDescriptors'][i]['nrOfDeviceDescriptorHandles'].to_bytes( 4, 'little' ) )

        for j in range( val['keyDescriptors'][i]['nrOfDeviceDescriptorHandles'] ):
            subVal = val['keyDescriptors'][i]['deviceDescriptorHandles'][j]
            tmpList.append( subVal.to_bytes( 4, 'little' ) )

        tmpList.append( val['keyDescriptors'][i]['nrOfKeyUsageDescriptors'].to_bytes( 4, 'little' ) )

        for j in range( val['keyDescriptors'][i]['nrOfKeyUsageDescriptors'] ):
            subVal = val['keyDescriptors'][i]['keyUsageDescriptors'][j]
            tmpList.append( subVal['frameType'].to_bytes( 4, 'little' ) )
            tmpList.append( subVal['commandFrameId'].to_bytes( 4, 'little' ) )

        for j in range( 16 ):
            if j < len( val['keyDescriptors'][i]['key'] ):
                tmpList.append( val['keyDescriptors'][i]['key'][j].to_bytes( 1, 'little' ) )
            else:
                tmpList.append( int(0).to_bytes( 1, 'little' ) )

    return b''.join( tmpList )


def DTS_getPerformanceMetrics( bs ):
    return {'counterOctets'       : int.from_bytes( bs[0:4], 'little' ),
            'retryCount'          : int.from_bytes( bs[4:8], 'little' ),
            'multipleRetryCount'  : int.from_bytes( bs[8:12], 'little' ),
            'TXFailCount'         : int.from_bytes( bs[12:16], 'little' ),
            'TXSuccessCount'      : int.from_bytes( bs[16:20], 'little' ),
            'FCSErrorCount'       : int.from_bytes( bs[20:24], 'little' ),
            'securityFailureCount': int.from_bytes( bs[24:28], 'little' ),
            'duplicateFrameCount' : int.from_bytes( bs[28:32], 'little' ),
            'RXSuccessCount'      : int.from_bytes( bs[32:36], 'little' ),
            'NACKCount'           : int.from_bytes( bs[36:40], 'little' ),
            'RXExpiredCount'      : int.from_bytes( bs[40:44], 'little' ), 
            'BOIrqCount'          : int.from_bytes( bs[44:48], 'little' ), }


def DTS_setPerformanceMetrics( val ):
    tmpList = []
    tmpList.append( val['counterOctets'].to_bytes( 4, 'little' ) )
    tmpList.append( val['retryCount'].to_bytes( 4, 'little' ) )
    tmpList.append( val['multipleRetryCount'].to_bytes( 4, 'little' ) )
    tmpList.append( val['TXFailCount'].to_bytes( 4, 'little' ) )
    tmpList.append( val['TXSuccessCount'].to_bytes( 4, 'little' ) )
    tmpList.append( val['FCSErrorCount'].to_bytes( 4, 'little' ) )
    tmpList.append( val['securityFailureCount'].to_bytes( 4, 'little' ) )
    tmpList.append( val['duplicateFrameCount'].to_bytes( 4, 'little' ) )
    tmpList.append( val['RXSuccessCount'].to_bytes( 4, 'little' ) )
    tmpList.append( val['NACKCount'].to_bytes( 4, 'little' ) )
    tmpList.append( val['RXExpiredCount'].to_bytes( 4, 'little' ) )
    tmpList.append( val['BOIrqCount'].to_bytes( 4, 'little' ) )

    return b''.join( tmpList )


def DTS_getTrafficCounters( bs ):
    return {'txDataFrmCnt'       : int.from_bytes( bs[0:4], 'little' ),
            'txCmdFrmCnt'        : int.from_bytes( bs[4:8], 'little' ),
            'txStdAckFrmCnt'     : int.from_bytes( bs[8:12], 'little' ),
            'txEnhAckFrmCnt'     : int.from_bytes( bs[12:16], 'little' ),
            'txBeaconFrmCnt'     : int.from_bytes( bs[16:20], 'little' ),
            'txMultiPurpFrmCnt'  : int.from_bytes( bs[20:24], 'little' ),
            'rxDataFrmOkCnt'     : int.from_bytes( bs[24:28], 'little' ),
            'rxCmdFrmOkCnt'      : int.from_bytes( bs[28:32], 'little' ),
            'rxStdAckFrmOkCnt'   : int.from_bytes( bs[32:36], 'little' ),
            'rxEnhAckFrmOkCnt'   : int.from_bytes( bs[36:40], 'little' ),
            'rxBeaconFrmOkCnt'   : int.from_bytes( bs[40:44], 'little' ),
            'rxMultiPurpFrmOkCnt': int.from_bytes( bs[44:48], 'little' ) }


def DTS_setTrafficCounters( val ):
    tmpList = []
    tmpList.append( val['txDataFrmCnt'].to_bytes( 4, 'little' ) )
    tmpList.append( val['txCmdFrmCnt'].to_bytes( 4, 'little' ) )
    tmpList.append( val['txStdAckFrmCnt'].to_bytes( 4, 'little' ) )
    tmpList.append( val['txEnhAckFrmCnt'].to_bytes( 4, 'little' ) )
    tmpList.append( val['txBeaconFrmCnt'].to_bytes( 4, 'little' ) )
    tmpList.append( val['txMultiPurpFrmCnt'].to_bytes( 4, 'little' ) )
    tmpList.append( val['rxDataFrmOkCnt'].to_bytes( 4, 'little' ) )
    tmpList.append( val['rxCmdFrmOkCnt'].to_bytes( 4, 'little' ) )
    tmpList.append( val['rxStdAckFrmOkCnt'].to_bytes( 4, 'little' ) )
    tmpList.append( val['rxEnhAckFrmOkCnt'].to_bytes( 4, 'little' ) )
    tmpList.append( val['rxBeaconFrmOkCnt'].to_bytes( 4, 'little' ) )
    tmpList.append( val['rxMultiPurpFrmOkCnt'].to_bytes( 4, 'little' ) )

    return b''.join( tmpList )


def DTS_getSlotframeTable( bs ):
    entries = []
    be      = 0

    nrOfSlotframes = int.from_bytes( bs[be:be+4], 'little' )
    be = be + 4

    for i in range( nrOfSlotframes ):
        entries.append( {'slotframeHandle': int.from_bytes( bs[be:be+4], 'little' ),
                         'slotframeSize'  : int.from_bytes( bs[be+4:be+8], 'little' )} )
        be = be + 8

    return {'nrOfSlotframes': nrOfSlotframes, 'slotframeEntries': entries}


def DTS_getLinkTable( bs ):
    entries = []
    be      = 0

    nrOfLinks = int.from_bytes( bs[be:be+4], 'little' )
    be = be + 4

    for i in range( nrOfLinks ):
        entries.append( {'linkHandle'     : int.from_bytes( bs[be:be+4], 'little' ),
                         'linkOptions'    : int.from_bytes( bs[be+4:be+8], 'little' ),
                         'linkType'       : int.from_bytes( bs[be+8:be+12], 'little' ),
                         'slotframeHandle': int.from_bytes( bs[be+12:be+16], 'little' ),
                         'nodeAddress'    : int.from_bytes( bs[be+16:be+20], 'little' ),
                         'timeslot'       : int.from_bytes( bs[be+20:be+24], 'little' ),
                         'channelOffset'  : int.from_bytes( bs[be+24:be+28], 'little' ) } )
        be = be + 28

    return {'nrOfLinks': nrOfLinks, 'linkEntries': entries}



def DTS_getHoppingSequenceList( bs ):
    hop = []

    for i in range( ftdf.FTDF_MAX_HOPPING_SEQUENCE_LENGTH ):
        hop.append( int.from_bytes( bs[i*4:i*4+4], 'little' ) )

    return hop


def DTS_getTimeslotTemplate( bs ):
    params = []
    params.append( {'timeslotTemplateId': 4} )
    params.append( {'tsCCAOffset': 4} )
    params.append( {'tsCCA': 4} )
    params.append( {'tsTxOffset': 4} )
    params.append( {'tsRxOffset': 4} )
    params.append( {'tsRxAckDelay': 4} )
    params.append( {'tsTxAckDelay': 4} )
    params.append( {'tsRxWait': 4} )
    params.append( {'tsAckWait': 4} )
    params.append( {'tsRxTx': 4} )
    params.append( {'tsMaxAck': 4} )
    params.append( {'tsMaxTs': 4} )
    params.append( {'tsTimeslotLength': 4} )

    return DTS_getParams( bs, params )


def DTS_setTimeslotTemplate( val ):
    data = []
    data.append( [val['timeslotTemplateId'], 4] )
    data.append( [val['tsCCAOffset'], 4] )
    data.append( [val['tsCCA'], 4] )
    data.append( [val['tsTxOffset'], 4] )
    data.append( [val['tsRxOffset'], 4] )
    data.append( [val['tsRxAckDelay'], 4] )
    data.append( [val['tsTxAckDelay'], 4] )
    data.append( [val['tsRxWait'], 4] )
    data.append( [val['tsAckWait'], 4] )
    data.append( [val['tsRxTx'], 4] )
    data.append( [val['tsMaxAck'], 4] )
    data.append( [val['tsMaxTs'], 4] )
    data.append( [val['tsTimeslotLength'], 4] )

    data = DTS_setParams( data )
    return b''.join( data )


def DTS_getPIBAttributeValue( atr, bs ):
    ret = 0

    # 32-bit signed integers
    if atr == ftdf.FTDF_PIB_TX_POWER:
        ret = int.from_bytes( bs[0:4], 'little', signed=True )

    # 64-bit unsigned integers
    elif (atr == ftdf.FTDF_PIB_EXTENDED_ADDRESS or
          atr == ftdf.FTDF_PIB_COORD_EXTENDED_ADDRESS or
          atr == ftdf.FTDF_PIB_FRAME_COUNTER or
          atr == ftdf.FTDF_PIB_PAN_COORD_EXTENDED_ADDRESS or
          atr == ftdf.FTDF_PIB_ASN):
        ret = int.from_bytes( bs[0:8], 'little' )

    # 32-bit unsigned integers
    elif (atr == ftdf.FTDF_PIB_ACK_WAIT_DURATION or
         atr == ftdf.FTDF_PIB_ASSOCIATION_PAN_COORD or
         atr == ftdf.FTDF_PIB_ASSOCIATION_PERMIT or
         atr == ftdf.FTDF_PIB_AUTO_REQUEST or
         atr == ftdf.FTDF_PIB_BATT_LIFE_EXT or
         atr == ftdf.FTDF_PIB_BATT_LIFE_EXT_PERIODS or
         atr == ftdf.FTDF_PIB_BEACON_PAYLOAD_LENGTH or
         atr == ftdf.FTDF_PIB_BEACON_ORDER or
         atr == ftdf.FTDF_PIB_BEACON_TX_TIME or
         atr == ftdf.FTDF_PIB_BSN or
         atr == ftdf.FTDF_PIB_COORD_SHORT_ADDRESS or
         atr == ftdf.FTDF_PIB_DSN or
         atr == ftdf.FTDF_PIB_GTS_PERMIT or
         atr == ftdf.FTDF_PIB_MAX_BE or
         atr == ftdf.FTDF_PIB_MAX_CSMA_BACKOFFS or
         atr == ftdf.FTDF_PIB_MAX_FRAME_TOTAL_WAIT_TIME or
         atr == ftdf.FTDF_PIB_MAX_FRAME_RETRIES or
         atr == ftdf.FTDF_PIB_MIN_BE or
         atr == ftdf.FTDF_PIB_LIFS_PERIOD or
         atr == ftdf.FTDF_PIB_SIFS_PERIOD or
         atr == ftdf.FTDF_PIB_PAN_ID or
         atr == ftdf.FTDF_PIB_PROMISCUOUS_MODE or
         atr == ftdf.FTDF_PIB_RESPONSE_WAIT_TIME or
         atr == ftdf.FTDF_PIB_RX_ON_WHEN_IDLE or
         atr == ftdf.FTDF_PIB_SECURITY_ENABLED or
         atr == ftdf.FTDF_PIB_SHORT_ADDRESS or
         atr == ftdf.FTDF_PIB_SUPERFRAME_ORDER or
         atr == ftdf.FTDF_PIB_SYNC_SYMBOL_OFFSET or
         atr == ftdf.FTDF_PIB_TIMESTAMP_SUPPORTED or
         atr == ftdf.FTDF_PIB_TRANSACTION_PERSISTENCE_TIME or
         atr == ftdf.FTDF_PIB_ENH_ACK_WAIT_DURATION or
         atr == ftdf.FTDF_PIB_IMPLICIT_BROADCAST or
         atr == ftdf.FTDF_PIB_SIMPLE_ADDRESS or
         atr == ftdf.FTDF_PIB_DISCONNECT_TIME or
         atr == ftdf.FTDF_PIB_JOIN_PRIORITY or
         atr == ftdf.FTDF_PIB_NO_HL_BUFFERS or
         atr == ftdf.FTDF_PIB_HOPPINGSEQUENCE_ID or
         atr == ftdf.FTDF_PIB_CHANNEL_PAGE or
         atr == ftdf.FTDF_PIB_NUMBER_OF_CHANNELS or
         atr == ftdf.FTDF_PIB_PHY_CONFIGURATION or
         atr == ftdf.FTDF_PIB_EXTENTED_BITMAP or
         atr == ftdf.FTDF_PIB_HOPPING_SEQUENCE_LENGTH or
         atr == ftdf.FTDF_PIB_CURRENT_HOP or
         atr == ftdf.FTDF_PIB_DWELL_TIME or
         atr == ftdf.FTDF_PIB_CSL_PERIOD or
         atr == ftdf.FTDF_PIB_CSL_MAX_PERIOD or
         atr == ftdf.FTDF_PIB_CSL_CHANNEL_MASK or
         atr == ftdf.FTDF_PIB_CSL_FRAME_PENDING_WAIT_T or
         atr == ftdf.FTDF_PIB_LOW_ENERGY_SUPERFRAME_SUPPORTED or
         atr == ftdf.FTDF_PIB_LOW_ENERGY_SUPERFRAME_SYNC_INTERVAL or
         atr == ftdf.FTDF_PIB_USE_ENHANCED_BEACON or
         atr == ftdf.FTDF_PIB_EB_FILTERING_ENABLED or
         atr == ftdf.FTDF_PIB_EBSN or
         atr == ftdf.FTDF_PIB_EB_AUTO_SA or
         atr == ftdf.FTDF_PIB_MT_DATA_SECURITY_LEVEL or
         atr == ftdf.FTDF_PIB_MT_DATA_KEY_ID_MODE or
         atr == ftdf.FTDF_PIB_MT_DATA_KEY_INDEX or
         atr == ftdf.FTDF_PIB_PAN_COORD_SHORT_ADDRESS or
         atr == ftdf.FTDF_PIB_FRAME_COUNTER_MODE or
         atr == ftdf.FTDF_PIB_CSL_SYNC_TX_MARGIN or
         atr == ftdf.FTDF_PIB_CSL_MAX_AGE_REMOTE_INFO or
         atr == ftdf.FTDF_PIB_TSCH_ENABLED or
         atr == ftdf.FTDF_PIB_LE_ENABLED or
         atr == ftdf.FTDF_PIB_CURRENT_CHANNEL or
         atr == ftdf.FTDF_PIB_TX_POWER_TOLERANCE or
         atr == ftdf.FTDF_PIB_CCA_MODE or
         atr == ftdf.FTDF_PIB_CURRENT_PAGE or
         atr == ftdf.FTDF_PIB_MAX_FRAME_DURATION or
         atr == ftdf.FTDF_PIB_LE_CAPABLE or
         atr == ftdf.FTDF_PIB_LL_CAPABLE or
         atr == ftdf.FTDF_PIB_DSME_CAPABLE or
         atr == ftdf.FTDF_PIB_RFID_CAPABLE or
         atr == ftdf.FTDF_PIB_AMCA_CAPABLE or
         atr == ftdf.FTDF_PIB_TSCH_CAPABLE or
         atr == ftdf.FTDF_PIB_METRICS_CAPABLE or
         atr == ftdf.FTDF_PIB_METRICS_ENABLED or
         atr == ftdf.FTDF_PIB_BEACON_AUTO_RESPOND or
         atr == ftdf.FTDF_PIB_RANGING_SUPPORTED or
         atr == ftdf.FTDF_PIB_KEEP_PHY_ENABLED or
         atr == ftdf.FTDF_PIB_TS_SYNC_CORRECT_THRESHOLD or
         atr == ftdf.FTDF_PIB_BO_IRQ_THRESHOLD or
         atr == ftdf.FTDF_PIB_SHR_DURATION):
        ret = int.from_bytes( bs[0:4], 'little' )

    # Octet pointers
    elif atr == ftdf.FTDF_PIB_BEACON_PAYLOAD:
        ret = []
        for i in range( ftdf.FTDF_MAX_BEACON_PAYLOAD_LENGTH ):
            ret.append( int.from_bytes( bs[i:i+1], 'little' ) )
    elif (atr == ftdf.FTDF_PIB_MT_DATA_KEY_SOURCE or
          atr == ftdf.FTDF_PIB_PTI_CONFIG or
          atr == ftdf.FTDF_PIB_DEFAULT_KEY_SOURCE):
        ret = []
        for i in range( 8 ):
            ret.append( int.from_bytes( bs[i:i+1], 'little' ) )

    # Others
    elif atr == ftdf.FTDF_PIB_DEVICE_TABLE:
        ret = DTS_getDeviceTable( bs )
    elif atr == ftdf.FTDF_PIB_SECURITY_LEVEL_TABLE:
        ret = DTS_getSecurityLevelTable( bs )
    elif atr == ftdf.FTDF_PIB_KEY_TABLE:
        ret = DTS_getKeyTable( bs )
    elif atr == ftdf.FTDF_PIB_PERFORMANCE_METRICS:
        ret = DTS_getPerformanceMetrics( bs )
    elif atr == ftdf.FTDF_PIB_TRAFFIC_COUNTERS:
        ret = DTS_getTrafficCounters( bs )
    elif atr == ftdf.FTDF_PIB_SLOTFRAME_TABLE:
        ret = DTS_getSlotframeTable( bs )
    elif atr == ftdf.FTDF_PIB_LINK_TABLE:
        ret = DTS_getLinkTable( bs )
    elif atr == ftdf.FTDF_PIB_EB_IE_LIST:
        ret = DTS_getPayloadIEList( bs, True )
    elif atr == ftdf.FTDF_PIB_EACK_IE_LIST:
        ret = DTS_getPayloadIEList( bs, True )
    elif atr == ftdf.FTDF_PIB_HOPPING_SEQUENCE_LIST:
        ret = DTS_getHoppingSequenceList( bs )
    elif atr == ftdf.FTDF_PIB_TIMESLOT_TEMPLATE:
        ret = DTS_getTimeslotTemplate( bs )
    else:
        dtsLog.error( 'Unknown PIB attribute!' )

    return ret


def DTS_setPIBAttributeValue( atr, val ):
    tmpList = []

    # 32-bit signed integers
    if atr == ftdf.FTDF_PIB_TX_POWER:
        tmpList.append( val.to_bytes( 4, 'little', signed=True ) )

    # 64-bit unsigned integers
    elif (atr == ftdf.FTDF_PIB_EXTENDED_ADDRESS or
          atr == ftdf.FTDF_PIB_COORD_EXTENDED_ADDRESS or
          atr == ftdf.FTDF_PIB_FRAME_COUNTER or
          atr == ftdf.FTDF_PIB_PAN_COORD_EXTENDED_ADDRESS or
          atr == ftdf.FTDF_PIB_ASN):
        tmpList.append( val.to_bytes( 8, 'little' ) )

    # 32-bit unsigned integers
    elif (atr == ftdf.FTDF_PIB_ACK_WAIT_DURATION or
         atr == ftdf.FTDF_PIB_ASSOCIATION_PAN_COORD or
         atr == ftdf.FTDF_PIB_ASSOCIATION_PERMIT or
         atr == ftdf.FTDF_PIB_AUTO_REQUEST or
         atr == ftdf.FTDF_PIB_BATT_LIFE_EXT or
         atr == ftdf.FTDF_PIB_BATT_LIFE_EXT_PERIODS or
         atr == ftdf.FTDF_PIB_BEACON_PAYLOAD_LENGTH or
         atr == ftdf.FTDF_PIB_BEACON_ORDER or
         atr == ftdf.FTDF_PIB_BEACON_TX_TIME or
         atr == ftdf.FTDF_PIB_BSN or
         atr == ftdf.FTDF_PIB_COORD_SHORT_ADDRESS or
         atr == ftdf.FTDF_PIB_DSN or
         atr == ftdf.FTDF_PIB_GTS_PERMIT or
         atr == ftdf.FTDF_PIB_MAX_BE or
         atr == ftdf.FTDF_PIB_MAX_CSMA_BACKOFFS or
         atr == ftdf.FTDF_PIB_MAX_FRAME_TOTAL_WAIT_TIME or
         atr == ftdf.FTDF_PIB_MAX_FRAME_RETRIES or
         atr == ftdf.FTDF_PIB_MIN_BE or
         atr == ftdf.FTDF_PIB_LIFS_PERIOD or
         atr == ftdf.FTDF_PIB_SIFS_PERIOD or
         atr == ftdf.FTDF_PIB_PAN_ID or
         atr == ftdf.FTDF_PIB_PROMISCUOUS_MODE or
         atr == ftdf.FTDF_PIB_RESPONSE_WAIT_TIME or
         atr == ftdf.FTDF_PIB_RX_ON_WHEN_IDLE or
         atr == ftdf.FTDF_PIB_SECURITY_ENABLED or
         atr == ftdf.FTDF_PIB_SHORT_ADDRESS or
         atr == ftdf.FTDF_PIB_SUPERFRAME_ORDER or
         atr == ftdf.FTDF_PIB_SYNC_SYMBOL_OFFSET or
         atr == ftdf.FTDF_PIB_TIMESTAMP_SUPPORTED or
         atr == ftdf.FTDF_PIB_TRANSACTION_PERSISTENCE_TIME or
         atr == ftdf.FTDF_PIB_ENH_ACK_WAIT_DURATION or
         atr == ftdf.FTDF_PIB_IMPLICIT_BROADCAST or
         atr == ftdf.FTDF_PIB_SIMPLE_ADDRESS or
         atr == ftdf.FTDF_PIB_DISCONNECT_TIME or
         atr == ftdf.FTDF_PIB_JOIN_PRIORITY or
         atr == ftdf.FTDF_PIB_NO_HL_BUFFERS or
         atr == ftdf.FTDF_PIB_HOPPINGSEQUENCE_ID or
         atr == ftdf.FTDF_PIB_CHANNEL_PAGE or
         atr == ftdf.FTDF_PIB_NUMBER_OF_CHANNELS or
         atr == ftdf.FTDF_PIB_PHY_CONFIGURATION or
         atr == ftdf.FTDF_PIB_EXTENTED_BITMAP or
         atr == ftdf.FTDF_PIB_HOPPING_SEQUENCE_LENGTH or
         atr == ftdf.FTDF_PIB_CURRENT_HOP or
         atr == ftdf.FTDF_PIB_DWELL_TIME or
         atr == ftdf.FTDF_PIB_CSL_PERIOD or
         atr == ftdf.FTDF_PIB_CSL_MAX_PERIOD or
         atr == ftdf.FTDF_PIB_CSL_CHANNEL_MASK or
         atr == ftdf.FTDF_PIB_CSL_FRAME_PENDING_WAIT_T or
         atr == ftdf.FTDF_PIB_LOW_ENERGY_SUPERFRAME_SUPPORTED or
         atr == ftdf.FTDF_PIB_LOW_ENERGY_SUPERFRAME_SYNC_INTERVAL or
         atr == ftdf.FTDF_PIB_USE_ENHANCED_BEACON or
         atr == ftdf.FTDF_PIB_EB_FILTERING_ENABLED or
         atr == ftdf.FTDF_PIB_EBSN or
         atr == ftdf.FTDF_PIB_EB_AUTO_SA or
         atr == ftdf.FTDF_PIB_MT_DATA_SECURITY_LEVEL or
         atr == ftdf.FTDF_PIB_MT_DATA_KEY_ID_MODE or
         atr == ftdf.FTDF_PIB_MT_DATA_KEY_INDEX or
         atr == ftdf.FTDF_PIB_PAN_COORD_SHORT_ADDRESS or
         atr == ftdf.FTDF_PIB_CSL_SYNC_TX_MARGIN or
         atr == ftdf.FTDF_PIB_CSL_MAX_AGE_REMOTE_INFO or
         atr == ftdf.FTDF_PIB_FRAME_COUNTER_MODE or
         atr == ftdf.FTDF_PIB_TSCH_ENABLED or
         atr == ftdf.FTDF_PIB_LE_ENABLED or
         atr == ftdf.FTDF_PIB_CURRENT_CHANNEL or
         atr == ftdf.FTDF_PIB_TX_POWER_TOLERANCE or
         atr == ftdf.FTDF_PIB_CCA_MODE or
         atr == ftdf.FTDF_PIB_CURRENT_PAGE or
         atr == ftdf.FTDF_PIB_MAX_FRAME_DURATION or
         atr == ftdf.FTDF_PIB_LE_CAPABLE or
         atr == ftdf.FTDF_PIB_LL_CAPABLE or
         atr == ftdf.FTDF_PIB_DSME_CAPABLE or
         atr == ftdf.FTDF_PIB_RFID_CAPABLE or
         atr == ftdf.FTDF_PIB_AMCA_CAPABLE or
         atr == ftdf.FTDF_PIB_TSCH_CAPABLE or
         atr == ftdf.FTDF_PIB_METRICS_CAPABLE or
         atr == ftdf.FTDF_PIB_METRICS_ENABLED or
         atr == ftdf.FTDF_PIB_BEACON_AUTO_RESPOND or
         atr == ftdf.FTDF_PIB_RANGING_SUPPORTED or
         atr == ftdf.FTDF_PIB_KEEP_PHY_ENABLED or
         atr == ftdf.FTDF_PIB_TS_SYNC_CORRECT_THRESHOLD or
         atr == ftdf.FTDF_PIB_BO_IRQ_THRESHOLD or
         atr == ftdf.FTDF_PIB_SHR_DURATION):
        tmpList.append( val.to_bytes( 4, 'little' ) )

    # Octet pointers
    elif atr == ftdf.FTDF_PIB_BEACON_PAYLOAD:
        for i in range( ftdf.FTDF_MAX_BEACON_PAYLOAD_LENGTH ):
            if i < len( val ):
                tmpList.append( val[i].to_bytes( 1, 'little' ) )
            else:
                tmpList.append( int(0).to_bytes( 1, 'little' ) )
    elif (atr == ftdf.FTDF_PIB_MT_DATA_KEY_SOURCE or
          atr == ftdf.FTDF_PIB_PTI_CONFIG or
          atr == ftdf.FTDF_PIB_DEFAULT_KEY_SOURCE):
        for i in range( 8 ):
            if i < len( val ):
                tmpList.append( val[i].to_bytes( 1, 'little' ) )
            else:
                tmpList.append( int(0).to_bytes( 1, 'little' ) )

    # Others
    elif (atr == ftdf.FTDF_PIB_SLOTFRAME_TABLE or
          atr == ftdf.FTDF_PIB_LINK_TABLE ):
        tmpList.append( int(0).to_bytes( 4, 'little' ) )
    elif atr == ftdf.FTDF_PIB_HOPPING_SEQUENCE_LIST:
        for i in range( ftdf.FTDF_MAX_HOPPING_SEQUENCE_LENGTH ):
            if i < len( val ):
                tmpList.append( val[i].to_bytes( 4, 'little' ) )
            else:
                tmpList.append( int(0).to_bytes( 4, 'little' ) )
    elif (atr == ftdf.FTDF_PIB_EB_IE_LIST or
          atr == ftdf.FTDF_PIB_EACK_IE_LIST ):
        tmpList.append( DTS_setPayloadIEList( val ) )
    elif atr == ftdf.FTDF_PIB_PERFORMANCE_METRICS:
        tmpList.append( DTS_setPerformanceMetrics( val ) )
    elif atr == ftdf.FTDF_PIB_TRAFFIC_COUNTERS:
        tmpList.append( DTS_setTrafficCounters( val ) )
    elif atr == ftdf.FTDF_PIB_KEY_TABLE:
        tmpList.append( DTS_setKeyTable( val ) )
    elif atr == ftdf.FTDF_PIB_DEVICE_TABLE:
        tmpList.append( DTS_setDeviceTable( val ) )
    elif atr == ftdf.FTDF_PIB_SECURITY_LEVEL_TABLE:
        tmpList.append( DTS_setSecurityLevelTable( val ) )
    elif atr == ftdf.FTDF_PIB_TIMESLOT_TEMPLATE:
        tmpList.append( DTS_setTimeslotTemplate( val ) )
    else:
        dtsLog.error( 'Unknown PIB attribute!' )

    return b''.join( tmpList )


def DTS_getPayloadIEList( bs, pib ):
    be  = 0
    IEs = []

    nrOfIEs = int.from_bytes( bs[be:be+4], 'little' )
    be      = be + 4

    for n in range( nrOfIEs ):
        ID     = int.from_bytes( bs[be:be+4], 'little' )
        length = int.from_bytes( bs[be+4:be+8], 'little' )
        be     = be + 8

        if ID == 1:
            subIEs     = []
            nrOfSubIEs = int.from_bytes( bs[be:be+4], 'little' )
            be         = be + 4

            for m in range( nrOfSubIEs ):
                subType = int.from_bytes( bs[be:be+4], 'little' )
                subID   = int.from_bytes( bs[be+4:be+8], 'little' )
                subLen  = int.from_bytes( bs[be+8:be+12], 'little' )
                be      = be + 12
                subContent = []

                for i in range( subLen ):
                    subContent.append( int.from_bytes( bs[be:be+1], 'little' ) )
                    be = be + 1

                pad = ( ( int( subLen / 4 ) + 1 ) * 4 ) - subLen
                be  = be + pad

                if pib:
                    subIEs.append( {'type': subType, 'subID': subID, 'length': subLen, 'subContent': subContent} )
                else:
                    subIEs.append( {'type': subType, 'subID': subID, 'length': subLen, 'content': subContent} )

            content = {'nrOfSubIEs': nrOfSubIEs, 'subIEs': subIEs}
        else:
            content = []

            for i in range( length ):
                content.append( int.from_bytes( bs[be:be+1], 'little' ) )
                be = be + 1

            pad = ( ( int( length / 4 ) + 1 ) * 4 ) - length
            be  = be + pad

        IEs.append( {'ID': ID, 'length': length, 'content': content} )

    if pib:
        return {'nrOfIEs': nrOfIEs, 'IEs': IEs}
    else:
        return {'nrOfIEs': nrOfIEs, 'IEs': IEs}, be


def DTS_setPayloadIEList( val ):
    if val == 0:
        nrOfIEs = 0
        return nrOfIEs.to_bytes( 4, 'little' )

    nrOfIEs = val['nrOfIEs']
    tmpList = []
    tmpList.append( nrOfIEs.to_bytes( 4, 'little' ) )

    for n in range( nrOfIEs ):
        tmpList.append( val['IEs'][n]['ID'].to_bytes( 4, 'little' ) )
        tmpList.append( val['IEs'][n]['length'].to_bytes( 4, 'little' ) )

        if val['IEs'][n]['ID'] == 1:
            nrOfSubIEs = val['IEs'][n]['content']['nrOfSubIEs']
            tmpList.append( nrOfSubIEs.to_bytes( 4, 'little' ) )

            for m in range( nrOfSubIEs ):
                tmp = val['IEs'][n]['content']['subIEs'][m]
                tmpList.append( tmp['type'].to_bytes( 4, 'little' ) )
                tmpList.append( tmp['subID'].to_bytes( 4, 'little' ) )
                tmpList.append( tmp['length'].to_bytes( 4, 'little' ) )

                for i in range( tmp['length'] ):
                    tmpList.append( tmp['subContent'][i].to_bytes( 1, 'little' ) )

                pad = ( ( int( tmp['length'] / 4 ) + 1 ) * 4 ) - tmp['length']

                for i in range( pad ):
                    tmpList.append( int(0).to_bytes( 1, 'little' ) )
        else:
            for i in range( val['IEs'][n]['length'] ):
                tmpList.append( val['IEs'][n]['content'][i].to_bytes( 1, 'little' ) )

            pad = ( ( int( val['IEs'][n]['length'] / 4 ) + 1 ) * 4 ) - val['IEs'][n]['length']

            for i in range( pad ):
                tmpList.append( int(0).to_bytes( 1, 'little' ) )

    return b''.join( tmpList )


def DTS_setParams( params ):
    # Function creates a list prepared for sndToUart with the values and sizes from params
    # params is a list of lists with the value and size in which the value will be put in the bytestream
    # e.g.: [[21, 4], [60, 8]]
    # A sublist can also consist of 3 values instead of 2. This means special action is to be taken.
    # e.g.: [[[1,2,3,4,5],5,'memcpy'],[1,2]] => A memcpy like action is taken

    tmpList = []
    for i in params:
        if len(i) == 2:
            # Nothing special to be done here, just convert int
            tmpList.append( i[0].to_bytes( i[1], 'little' ) )
        elif len(i) == 3:
            # There is something special to do here
            special = i[ len( i ) - 1 ]

            if special == 'memcpy':
                # memcpy means first list entry is a list of bytes and 2nd entry is size of the list
                # the resulting bytestream must be word aligned so take that into considiration here
                # e.g. add padding bytes if nessessary
                for j in range( i[ 1 ] ):
                    tmpList.append( i[0][j].to_bytes( 1, 'little' ) )

                pad = ( ( int( i[ 1 ] / 4 ) + 1 ) * 4 ) - i[ 1 ]

                for j in range( pad ):
                    tmpList.append( int(0).to_bytes( 1, 'little' ) )

            elif special == 'keySource':
                # keySource is always array of 8, but user doesn't have to fill in the whole array
                # If array is not 8 bytes yet, just append nonsense bytes till it is
                while ( len( i[ 0 ] ) < 8 ):
                    i[ 0 ].append( 0 )

                for j in range( 8 ):
                    tmpList.append( i[0][j].to_bytes( 1, 'little' ) )

            elif special == 'IEList':
                # IE list has to be inserted
                tmpList.append( DTS_setPayloadIEList( i[ 0 ] ) )

            elif special == 'PIBAttributeValue':
                # PIB attribute value must be inserted
                tmpList.append( DTS_setPIBAttributeValue( i[ 1 ], i[ 0 ] ) )

    return tmpList


def DTS_getParams( bytestream, params ):
    # Function creates a dict with keys from params and values from bytestream
    # params is a list of dictionary keys with their actual size in the bytestream (4 or 8 mostly)
    # e.g.: [{'msgId': 4}, {'status': 4}]
    # A dictionary value can also be a list instead of a number. This means that some special
    # something must be done. This can for example be a memcpy action
    # e.g.: [{'msgId': 4}, {'msdu': ['msduLength', 'memcpy']}]
    # In this example the msdu list means that a memcpy must be done, and that the length is dependant
    # on another attribute in the dictionary (msduLength). This could also be a fixed nr (e.g. 5).

    d  = {}
    be = 0
    for i in params:
        for j in i.keys():
            if type( i[j] ) == int:
                # Nothing special to do here
                d[j] = int.from_bytes(bytestream[be:be+i[j]],'little')
                be   = be + i[j]
            elif type( i[j] ) == list:
                # Something special must be done here, special action type is last entry in sublist
                special = i[j][len( i[j] ) - 1]

                if special == 'memcpy':
                    # memcpy means first list entry is either a previously retreived entry or fixed nr
                    # That nr is the nr of bytes to copy, but padding bytes must be taken into consideration
                    # e.g. skip padding bytes if nessessary
                    nrOfBytes = 0

                    if type( i[j][0] ) == str:
                        # Nr of bytes depend on previously retrieved dict entry
                        nrOfBytes = d[ i[j][0] ]
                    elif type( i[j][0] ) == int:
                        # Fixed nr of bytes
                        nrOfBytes = i[j][0]

                    d[j] = []
                    for byte in range( nrOfBytes ):
                        d[j].append( int.from_bytes(bytestream[be:be+1], 'little') )
                        be = be + 1

                    pad = ( ( int( nrOfBytes / 4 ) + 1 ) * 4 ) - nrOfBytes
                    be  = be + pad

                elif special == 'strcpy':
                    # strcpy must be done, this is used for release info
                    l = []

                    for char in range( i[j][0] ):
                        l.append( chr( int.from_bytes( bytestream[be:be+1], 'little' ) ) )
                        be = be + 1

                    d[j] = ''.join(l)

                    if d[j].find('\x00') >= 0:
                        d[j] = d[j][:d[j].find('\x00')]

                elif special == 'keySource':
                    # keySource is always 8 bytes
                    d[j] = []
                    for byte in range( 8 ):
                        d[j].append( int.from_bytes(bytestream[be:be+1], 'little') )
                        be = be + 1

                elif special == 'IEList':
                    # IE list must be retrieved, function also returns bytes read so be can be adjusted properly
                    d[j], bytesRead = DTS_getPayloadIEList( bytestream[be:], False )
                    be = be + bytesRead

                elif special == 'PIBAttributeValue':
                    # Retrieve PIB attribute value
                    # NOTE: this is expected to be the last entry so nothing is done with be afterwards
                    d[j] = DTS_getPIBAttributeValue( d[ i[j][0] ], bytestream[be:] )

                elif special == 'list_dict':
                    # A list of dictionaries must be created, use this function recursively for that
                    nrOfEntries = 0

                    if type( i[j][0] ) == str:
                        # Nr of list entries depend on previously retrieved dict entry
                        nrOfEntries = d[ i[j][0] ]
                    elif type( i[j][0] ) == int:
                        # Fixed nr of entries
                        nrOfEntries = i[j][0]

                    l = []
                    for entry in range( nrOfEntries ):
                        l.append( DTS_getParams( bytestream[be:], i[j][1] ) )
                        for cnt in i[j][1]:
                            for cnt2 in cnt.keys():
                                be = be + cnt[cnt2]

                    d[j] = l

                elif special == 'dict':
                    # A single dictionary must be created, use this function recursively
                    d[j] = DTS_getParams( bytestream[be:], i[j][0] )

                    for cnt in i[j][0]:
                        for cnt2 in cnt.keys():
                            be = be + cnt[cnt2]

                elif special == 'beacon_address_list':
                    # Used in the beacon notify indication, a list of addresses must be retrieved
                    addrSpec       = d[ i[j][0] ]
                    nrOfShortAddrs = addrSpec & 0x07
                    nrOfExtAddrs   = ( addrSpec & 0x70 ) >> 4
                    addrList       = []

                    for addr in range( nrOfShortAddrs ):
                        addrList.append( {'shortAddress': int.from_bytes( bytestream[be:be+8], 'little' ) } )
                        be = be + 8

                    for addr in range( nrOfExtAddrs ):
                        addrList.append( {'extAddress': int.from_bytes( bytestream[be:be+8], 'little' ) } )
                        be = be + 8

                    d[j] = addrList

    return d

#############################
# Generic msg functions
#############################
def DTS_sndMsg( com, msg ):
    dtsLog.info( 'Sending message (COM port ID: %s)' % com )
    dtsLog.debug( '%s' % msg )

    if type(msg) != dict:
        dtsLog.error( 'Message must be a dictionary' )
        return False

    if 'msgId' not in msg:
        dtsLog.error( "'msgId' not found in dictionary" )
        return False

    if msg['msgId'] == ftdf.FTDF_RESET_REQUEST:
        DTS_sndResetRequest( com, msg )
    elif msg['msgId'] == ftdf.FTDF_GET_REQUEST:
        DTS_sndGetRequest( com, msg )
    elif msg['msgId'] == ftdf.FTDF_SET_REQUEST:
        DTS_sndSetRequest( com, msg )
    elif msg['msgId'] == ftdf.FTDF_DATA_REQUEST:
        DTS_sndDataRequest( com, msg )
    elif msg['msgId'] == ftdf.FTDF_RX_ENABLE_REQUEST:
        DTS_sndRxEnableRequest( com, msg )
    elif msg['msgId'] == ftdf.FTDF_POLL_REQUEST:
        DTS_sndPollRequest( com, msg )
    elif msg['msgId'] == ftdf.FTDF_PURGE_REQUEST:
        DTS_sndPurgeRequest( com, msg )
    elif msg['msgId'] == ftdf.FTDF_SCAN_REQUEST:
        DTS_sndScanRequest( com, msg )
    elif msg['msgId'] == ftdf.FTDF_TSCH_MODE_REQUEST:
        DTS_sndTschModeRequest( com, msg )
    elif msg['msgId'] == ftdf.FTDF_SET_SLOTFRAME_REQUEST:
        DTS_sndSetSlotframeRequest( com, msg )
    elif msg['msgId'] == ftdf.FTDF_SET_LINK_REQUEST:
        DTS_sndSetLinkRequest( com, msg )
    elif msg['msgId'] == ftdf.FTDF_BEACON_REQUEST:
        DTS_sndBeaconRequest( com, msg )
    elif msg['msgId'] == ftdf.FTDF_START_REQUEST:
        DTS_sndStartRequest( com, msg )
    elif msg['msgId'] == ftdf.FTDF_ASSOCIATE_REQUEST:
        DTS_sndAssociateRequest( com, msg )
    elif msg['msgId'] == ftdf.FTDF_ASSOCIATE_RESPONSE:
        DTS_sndAssociateResponse( com, msg )
    elif msg['msgId'] == ftdf.FTDF_DISASSOCIATE_REQUEST:
        DTS_sndDisassociateRequest( com, msg )
    elif msg['msgId'] == ftdf.FTDF_ORPHAN_RESPONSE:
        DTS_sndOrphanResponse( com, msg )
    elif msg['msgId'] == ftdf.FTDF_KEEP_ALIVE_REQUEST:
        DTS_sndKeepAliveRequest( com, msg )
    elif msg['msgId'] == ftdf.FTDF_SLEEP_REQUEST:
        DTS_sndSleepRequest( com, msg )
    elif msg['msgId'] == ftdf.FTDF_DBG_MODE_SET_REQUEST:
        DTS_setDbgMode( com, msg )  
    elif msg['msgId'] == ftdf.FTDF_FPPR_MODE_SET_REQUEST:
        DTS_setFpprMode( com, msg )        
    else:
        dtsLog.error( "Unsupported msgId given" )
        return False
    return True


def DTS_getSubMsg( msgId, qitem ):

    # non-msg API
    if msgId == ftdf.FTDF_TRANSPARENT_CONFIRM:
        return True, DTS_rcvSendFrameTransparantConfirm( qitem )
    elif msgId == ftdf.FTDF_TRANSPARENT_INDICATION:
        return True, DTS_rcvFrameTransparant( qitem )
    elif msgId == ftdf.DTS_MSG_ID_CAN_POWER_OFF_CONF:
        return True, DTS_rcvCanSleep( qitem )
    elif msgId == ftdf.DTS_MSG_ID_PREP_POWER_OFF_CONF:
        return True, DTS_rcvPrepareForSleep( qitem )
    elif msgId == ftdf.DTS_MSG_ID_WAKE_UP_READY:
        return True, DTS_rcvWakeUpReady( qitem )
    elif msgId == ftdf.DTS_MSG_ID_REL_INFO:
        return True, DTS_rcvReleaseInfo( qitem )
    elif msgId == ftdf.DTS_MSG_ID_GET_REG:
        return True, DTS_rcvGetRegister( qitem )
    elif msgId == ftdf.DTS_MSG_ID_SND_QUEUE_SUMMARY:
        return True, DTS_rcvQueueSummary( qitem )
    elif msgId == ftdf.DTS_MSG_ID_BLE_EVT:
        return True, DTS_rcvBLEEvt( qitem )
    elif msgId == ftdf.DTS_MSG_ID_BLE_STATUS:
        return True, DTS_rcvBLEStatus( qitem )
    elif msgId == ftdf.DTS_MSG_ID_BLE_OK:
        return True, DTS_rcvBLEGeneric( qitem )
    elif msgId == ftdf.DTS_MSG_ID_BLE_MSG_LOG:
        return True, DTS_rcvBLEMsgLog ( qitem )
    elif msgId == ftdf.DTS_MSG_ID_BLE_STATS:
        return True, DTS_rcvBLEStats ( qitem )
    elif msgId == ftdf.DTS_MSG_ID_COEX_STATS:
        return True, DTS_rcvCoexStats ( qitem )
    # msg API
    elif msgId == ftdf.FTDF_EXPLICIT_WAKE_UP:
        return True, DTS_rcvExplicitWakeUp( qitem )
    elif msgId == ftdf.FTDF_RESET_CONFIRM:
        return True, DTS_rcvResetConfirm( qitem )
    elif msgId == ftdf.FTDF_GET_CONFIRM:
        return True, DTS_rcvGetConfirm( qitem )
    elif msgId == ftdf.FTDF_SET_CONFIRM:
        return True, DTS_rcvSetConfirm( qitem )
    elif msgId == ftdf.FTDF_DATA_CONFIRM:
        return True, DTS_rcvDataConfirm( qitem )
    elif msgId == ftdf.FTDF_DATA_INDICATION:
        return True, DTS_rcvDataIndication( qitem )
    elif msgId == ftdf.FTDF_RX_ENABLE_CONFIRM:
        return True, DTS_rcvRxEnableConfirm( qitem )
    elif msgId == ftdf.FTDF_POLL_CONFIRM:
        return True, DTS_rcvPollConfirm( qitem )
    elif msgId == ftdf.FTDF_PURGE_CONFIRM:
        return True, DTS_rcvPurgeConfirm( qitem )
    elif msgId == ftdf.FTDF_SCAN_CONFIRM:
        return True, DTS_rcvScanConfirm( qitem )
    elif msgId == ftdf.FTDF_SET_SLOTFRAME_CONFIRM:
        return True, DTS_rcvSetSlotframeConfirm( qitem )
    elif msgId == ftdf.FTDF_SET_LINK_CONFIRM:
        return True, DTS_rcvSetLinkConfirm( qitem )
    elif msgId == ftdf.FTDF_TSCH_MODE_CONFIRM:
        return True, DTS_rcvTschModeConfirm( qitem )
    elif msgId == ftdf.FTDF_BEACON_NOTIFY_INDICATION:
        return True, DTS_rcvBeaconNotifyIndication( qitem )
    elif msgId == ftdf.FTDF_BEACON_CONFIRM:
        return True, DTS_rcvBeaconConfirm( qitem )
    elif msgId == ftdf.FTDF_BEACON_REQUEST_INDICATION:
        return True, DTS_rcvBeaconRequestIndication( qitem )
    elif msgId == ftdf.FTDF_START_CONFIRM:
        return True, DTS_rcvStartConfirm( qitem )
    elif msgId == ftdf.FTDF_ASSOCIATE_INDICATION:
        return True, DTS_rcvAssociateIndication( qitem )
    elif msgId == ftdf.FTDF_ASSOCIATE_CONFIRM:
        return True, DTS_rcvAssociateConfirm( qitem )
    elif msgId == ftdf.FTDF_DISASSOCIATE_CONFIRM:
        return True, DTS_rcvDisassociateConfirm( qitem )
    elif msgId == ftdf.FTDF_DISASSOCIATE_INDICATION:
        return True, DTS_rcvDisassociateIndication( qitem )
    elif msgId == ftdf.FTDF_ORPHAN_INDICATION:
        return True, DTS_rcvOrphanIndication( qitem )
    elif msgId == ftdf.FTDF_SYNC_LOSS_INDICATION:
        return True, DTS_rcvSyncLossIndication( qitem )
    elif msgId == ftdf.FTDF_COMM_STATUS_INDICATION:
        return True, DTS_rcvCommStatusIndication( qitem )
    elif msgId == ftdf.FTDF_KEEP_ALIVE_CONFIRM:
        return True, DTS_rcvKeepAliveConfirm( qitem )
    else:
        return False, 0


def DTS_getMsg( com, timeout=None ):
    if not com in DTS_serQueue.keys( ):
        return False, 0

    dtsLog.info( 'Checking queue for messages (COM port ID: %s)' % com )

    qitem = 0

    if timeout == None:
        block = False
    else:
        block = True

    try:
        qitem = DTS_serQueue[ com ].get( block=block, timeout=timeout )
    except KeyboardInterrupt:
        dtsLog.error( 'Test stopped by keyboard interrupt' )
        DTS_quit( )
    except:
        dtsLog.info( 'No message in queue' )
        return False, 0

    msgId = int.from_bytes( qitem[0:4], 'little' )

    res, ret = DTS_getSubMsg( msgId, qitem )
    DTS_serQueue[ com ].task_done( )

    dtsLog.info( 'Received message (COM port ID: %s)' % com )
    dtsLog.debug( '%s' % ret )

    return res, ret


#############################
# Msg specific functions
#############################

#############################
# RESET
#############################
def DTS_sndResetRequest( com, msg ):
    data = []
    data.append( [msg['msgId'], 4] )
    data.append( [msg['setDefaultPIB'], 4] )

    data = DTS_setParams( data )
    DTS_sndToUart( com, data )

def DTS_rcvResetConfirm( qitem ):
    params = []
    params.append( {'msgId': 4} )
    params.append( {'status': 4} )

    msg = DTS_getParams( qitem, params )

    return msg


#############################
# GET
#############################
def DTS_sndGetRequest( com, msg ):
    data = []
    data.append( [msg['msgId'], 4] )
    data.append( [msg['PIBAttribute'], 4] )

    data = DTS_setParams( data )
    DTS_sndToUart( com, data )

def DTS_rcvGetConfirm( qitem ):
    params = []
    params.append( {'msgId': 4} )
    params.append( {'status': 4} )
    params.append( {'PIBAttribute': 4} )
    params.append( {'PIBAttributeValue': ['PIBAttribute', 'PIBAttributeValue']} )

    msg = DTS_getParams( qitem, params )

    return msg


#############################
# SET
#############################
def DTS_sndSetRequest( com, msg ):
    data = []
    data.append( [msg['msgId'], 4] )
    data.append( [msg['PIBAttribute'], 4] )
    data.append( [msg['PIBAttributeValue'], msg['PIBAttribute'], 'PIBAttributeValue'] )

    data = DTS_setParams( data )
    DTS_sndToUart( com, data )

def DTS_rcvSetConfirm( qitem ):
    params = []
    params.append( {'msgId': 4} )
    params.append( {'status': 4} )
    params.append( {'PIBAttribute': 4} )

    msg = DTS_getParams( qitem, params )

    return msg


#############################
# DATA
#############################
def DTS_sndDataRequest( com, msg ):
    data = []
    data.append( [msg['msgId'], 4] )
    data.append( [msg['srcAddrMode'], 4] )
    data.append( [msg['dstAddrMode'], 4] )
    data.append( [msg['dstPANId'], 4] )
    data.append( [msg['dstAddr'], 8] )
    data.append( [msg['msduLength'], 4] )
    data.append( [msg['msdu'], msg['msduLength'], 'memcpy'] )
    data.append( [msg['msduHandle'], 4] )
    data.append( [msg['ackTX'], 4] )
    data.append( [msg['GTSTX'], 4] )
    data.append( [msg['indirectTX'], 4] )
    data.append( [msg['securityLevel'], 4] )
    data.append( [msg['keyIdMode'], 4] )
    data.append( [msg['keySource'], len( msg['keySource'] ), 'keySource'] )
    data.append( [msg['keyIndex'], 4] )
    data.append( [msg['frameControlOptions'], 4] )
    # Header IE list not used in data request
    data.append( [msg['payloadIEList'], 0, 'IEList'] )
    data.append( [msg['sendMultiPurpose'], 4] )

    data = DTS_setParams( data )
    DTS_sndToUart( com, data )

def DTS_rcvDataConfirm( qitem ):
    params = []
    params.append( {'msgId': 4} )
    params.append( {'msduHandle': 4} )
    params.append( {'timestamp': 4} )
    params.append( {'status': 4} )
    params.append( {'numOfBackoffs': 4} )
    params.append( {'DSN': 4} )
    params.append( {'ackPayload': ['IEList']} )

    msg = DTS_getParams( qitem, params )

    return msg

def DTS_rcvDataIndication( qitem ):
    params = []
    params.append( {'msgId': 4} )
    params.append( {'srcAddrMode': 4} )
    params.append( {'srcPANId': 4} )
    params.append( {'srcAddr': 8} )
    params.append( {'dstAddrMode': 4} )
    params.append( {'dstPANId': 4} )
    params.append( {'dstAddr': 8} )
    params.append( {'msduLength': 4} )
    params.append( {'msdu': ['msduLength', 'memcpy']} )
    params.append( {'mpduLinkQuality': 4} )
    params.append( {'DSN': 4} )
    params.append( {'timestamp': 4} )
    params.append( {'securityLevel': 4} )
    params.append( {'keyIdMode': 4} )
    params.append( {'keySource': [8, 'keySource']} )
    params.append( {'keyIndex': 4} )
    params.append( {'payloadIEList': ['IEList']} )

    msg = DTS_getParams( qitem, params )

    return msg


#############################
# RX ENABLE
#############################
def DTS_sndRxEnableRequest( com, msg ):
    data = []
    data.append( [msg['msgId'], 4] )
    data.append( [msg['deferPermit'], 4] )
    data.append( [msg['rxOnTime'], 4] )
    data.append( [msg['rxOnDuration'], 4] )

    data = DTS_setParams( data )
    DTS_sndToUart( com, data )

def DTS_rcvRxEnableConfirm( qitem ):
    params = []
    params.append( {'msgId': 4} )
    params.append( {'status': 4} )

    msg = DTS_getParams( qitem, params )

    return msg


#############################
# POLL
#############################
def DTS_sndPollRequest( com, msg ):
    data = []
    data.append( [msg['msgId'], 4] )
    data.append( [msg['coordAddrMode'], 4] )
    data.append( [msg['coordPANId'], 4] )
    data.append( [msg['coordAddr'], 8] )
    data.append( [msg['securityLevel'], 4] )
    data.append( [msg['keyIdMode'], 4] )
    data.append( [msg['keySource'], len( msg['keySource'] ), 'keySource'] )
    data.append( [msg['keyIndex'], 4] )

    data = DTS_setParams( data )
    DTS_sndToUart( com, data )

def DTS_rcvPollConfirm( qitem ):
    params = []
    params.append( {'msgId': 4} )
    params.append( {'status': 4} )

    msg = DTS_getParams( qitem, params )

    return msg


#############################
# PURGE
#############################
def DTS_sndPurgeRequest( com, msg ):
    data = []
    data.append( [msg['msgId'], 4] )
    data.append( [msg['msduHandle'], 4] )

    data = DTS_setParams( data )
    DTS_sndToUart( com, data )

def DTS_rcvPurgeConfirm( qitem ):
    params = []
    params.append( {'msgId': 4} )
    params.append( {'msduHandle': 4} )
    params.append( {'status': 4} )

    msg = DTS_getParams( qitem, params )

    return msg


#############################
# SCAN
#############################
def DTS_sndScanRequest( com, msg ):
    data = []
    data.append( [msg['msgId'], 4] )
    data.append( [msg['scanType'], 4] )
    data.append( [msg['scanChannels'], 4] )
    data.append( [msg['channelPage'], 4] )
    data.append( [msg['scanDuration'], 4] )
    data.append( [msg['securityLevel'], 4] )
    data.append( [msg['keyIdMode'], 4] )
    data.append( [msg['keySource'], len( msg['keySource'] ), 'keySource'] )
    data.append( [msg['keyIndex'], 4] )

    data = DTS_setParams( data )
    DTS_sndToUart( com, data )

def DTS_rcvScanConfirm( qitem ):
    pandes = []
    pandes.append( {'coordAddrMode': 4} )
    pandes.append( {'coordPANId': 4} )
    pandes.append( {'coordAddr': 8} )
    pandes.append( {'channelNumber': 4} )
    pandes.append( {'channelPage': 4} )
    pandes.append( {'superframeSpec': 4} )
    pandes.append( {'GTSPermit': 4} )
    pandes.append( {'linkQuality': 4} )
    pandes.append( {'timestamp': 4} )

    coorddes = []
    coorddes.append( {'coordPANId': 4} )
    coorddes.append( {'coordShortAddr': 4} )
    coorddes.append( {'channelNumber': 4} )
    coorddes.append( {'shortAddr': 4} )
    coorddes.append( {'channelPage': 4} )

    params = []
    params.append( {'msgId': 4} )
    params.append( {'status': 4} )
    params.append( {'scanType': 4} )
    params.append( {'channelPage': 4} )
    params.append( {'unscannedChannels': 4} )
    params.append( {'resultListSize': 4} )
    params.append( {'energyDetectList': ['resultListSize', 'memcpy']} )
    params.append( {'PANDescriptorList': ['resultListSize', pandes, 'list_dict']} )
    params.append( {'coordRealignDescriptor': [coorddes, 'dict']} )

    msg = DTS_getParams( qitem, params )

    return msg


#############################
# TSCH MODE
#############################
def DTS_sndTschModeRequest( com, msg ):
    data = []
    data.append( [msg['msgId'], 4] )
    data.append( [msg['tschMode'], 4] )
    data.append( [msg['timeslotStartTime'], 4] )

    data = DTS_setParams( data )
    DTS_sndToUart( com, data )

def DTS_rcvTschModeConfirm( qitem ):
    params = []
    params.append( {'msgId': 4} )
    params.append( {'tschMode': 4} )
    params.append( {'status': 4} )

    msg = DTS_getParams( qitem, params )

    return msg


#############################
# SLOTFRAME
#############################
def DTS_sndSetSlotframeRequest( com, msg ):
    data = []
    data.append( [msg['msgId'], 4] )
    data.append( [msg['handle'], 4] )
    data.append( [msg['operation'], 4] )
    data.append( [msg['size'], 4] )

    data = DTS_setParams( data )
    DTS_sndToUart( com, data )

def DTS_rcvSetSlotframeConfirm( qitem ):
    params = []
    params.append( {'msgId': 4} )
    params.append( {'handle': 4} )
    params.append( {'status': 4} )

    msg = DTS_getParams( qitem, params )

    return msg


#############################
# LINK
#############################
def DTS_sndSetLinkRequest( com, msg ):
    data = []
    data.append( [msg['msgId'], 4] )
    data.append( [msg['operation'], 4] )
    data.append( [msg['linkHandle'], 4] )
    data.append( [msg['slotframeHandle'], 4] )
    data.append( [msg['timeslot'], 4] )
    data.append( [msg['channelOffset'], 4] )
    data.append( [msg['linkOptions'], 4] )
    data.append( [msg['linkType'], 4] )
    data.append( [msg['nodeAddress'], 4] )

    data = DTS_setParams( data )
    DTS_sndToUart( com, data )

def DTS_rcvSetLinkConfirm( qitem ):
    params = []
    params.append( {'msgId': 4} )
    params.append( {'status': 4} )
    params.append( {'linkHandle': 4} )
    params.append( {'slotframeHandle': 4} )

    msg = DTS_getParams( qitem, params )

    return msg


#############################
# BEACON
#############################
def DTS_sndBeaconRequest( com, msg ):
    data = []
    data.append( [msg['msgId'], 4] )
    data.append( [msg['beaconType'], 4] )
    data.append( [msg['channel'], 4] )
    data.append( [msg['channelPage'], 4] )
    data.append( [msg['superframeOrder'], 4] )
    data.append( [msg['beaconSecurityLevel'], 4] )
    data.append( [msg['beaconKeyIdMode'], 4] )
    data.append( [msg['beaconKeySource'], len( msg['beaconKeySource'] ), 'keySource'] )
    data.append( [msg['beaconKeyIndex'], 4] )
    data.append( [msg['dstAddrMode'], 4] )
    data.append( [msg['dstAddr'], 8] )
    data.append( [msg['BSNSuppression'], 4] )

    data = DTS_setParams( data )
    DTS_sndToUart( com, data )

def DTS_rcvBeaconConfirm( qitem ):
    params = []
    params.append( {'msgId': 4} )
    params.append( {'status': 4} )

    msg = DTS_getParams( qitem, params )

    return msg

def DTS_rcvBeaconRequestIndication( qitem ):
    params = []
    params.append( {'msgId': 4} )
    params.append( {'beaconType': 4} )
    params.append( {'srcAddrMode': 4} )
    params.append( {'srcAddr': 8} )
    params.append( {'dstPANId': 4} )
    params.append( {'IEList': ['IEList']} )

    msg = DTS_getParams( qitem, params )

    return msg

def DTS_rcvBeaconNotifyIndication( qitem ):
    pandes = []
    pandes.append( {'coordAddrMode': 4} )
    pandes.append( {'coordPANId': 4} )
    pandes.append( {'coordAddr': 8} )
    pandes.append( {'channelNumber': 4} )
    pandes.append( {'channelPage': 4} )
    pandes.append( {'superframeSpec': 4} )
    pandes.append( {'GTSPermit': 4} )
    pandes.append( {'linkQuality': 4} )
    pandes.append( {'timestamp': 4} )

    params = []
    params.append( {'msgId': 4} )
    params.append( {'BSN': 4} )
    params.append( {'PANDescriptor': [1, pandes, 'list_dict']} )
    params.append( {'pendAddrSpec': 4} )
    params.append( {'addrList': ['pendAddrSpec', 'beacon_address_list']} )
    params.append( {'sduLength': 4} )
    params.append( {'sdu': ['sduLength', 'memcpy']} )
    params.append( {'EBSN': 4} )
    params.append( {'beaconType': 4} )
    params.append( {'IEList': ['IEList']} )
    params.append( {'timestamp': 4} )

    msg = DTS_getParams( qitem, params )

    return msg


#############################
# START
#############################
def DTS_sndStartRequest( com, msg ):
    data = []
    data.append( [msg['msgId'], 4] )
    data.append( [msg['PANId'], 4] )
    data.append( [msg['channelNumber'], 4] )
    data.append( [msg['channelPage'], 4] )
    data.append( [msg['startTime'], 4] )
    data.append( [msg['beaconOrder'], 4] )
    data.append( [msg['superframeOrder'], 4] )
    data.append( [msg['PANCoordinator'], 4] )
    data.append( [msg['batteryLifeExtension'], 4] )
    data.append( [msg['coordRealignment'], 4] )
    data.append( [msg['coordRealignSecurityLevel'], 4] )
    data.append( [msg['coordRealignKeyIdMode'], 4] )
    data.append( [msg['coordRealignKeySource'], len( msg['coordRealignKeySource'] ), 'keySource'] )
    data.append( [msg['coordRealignKeyIndex'], 4] )
    data.append( [msg['beaconSecurityLevel'], 4] )
    data.append( [msg['beaconKeyIdMode'], 4] )
    data.append( [msg['beaconKeySource'], len( msg['beaconKeySource'] ), 'keySource'] )
    data.append( [msg['beaconKeyIndex'], 4] )

    data = DTS_setParams( data )
    DTS_sndToUart( com, data )

def DTS_rcvStartConfirm( qitem ):
    params = []
    params.append( {'msgId': 4} )
    params.append( {'status': 4} )

    msg = DTS_getParams( qitem, params )

    return msg


#############################
# ASSOCIATE
#############################
def DTS_sndAssociateRequest( com, msg ):
    data = []
    data.append( [msg['msgId'], 4] )
    data.append( [msg['channelNumber'], 4] )
    data.append( [msg['channelPage'], 4] )
    data.append( [msg['coordAddrMode'], 4] )
    data.append( [msg['coordPANId'], 4] )
    data.append( [msg['coordAddr'], 8] )
    data.append( [msg['capabilityInformation'], 4] )
    data.append( [msg['securityLevel'], 4] )
    data.append( [msg['keyIdMode'], 4] )
    data.append( [msg['keySource'], len( msg['keySource'] ), 'keySource'] )
    data.append( [msg['keyIndex'], 4] )
    data.append( [msg['channelOffset'], 4] )
    data.append( [msg['hoppingSequenceId'], 4] )

    data = DTS_setParams( data )
    DTS_sndToUart( com, data )

def DTS_sndAssociateResponse( com, msg ):
    data = []
    data.append( [msg['msgId'], 4] )
    data.append( [msg['deviceAddress'], 8] )
    data.append( [msg['assocShortAddress'], 4] )
    data.append( [msg['status'], 4] )
    data.append( [msg['fastA'], 4] )
    data.append( [msg['securityLevel'], 4] )
    data.append( [msg['keyIdMode'], 4] )
    data.append( [msg['keySource'], len( msg['keySource'] ), 'keySource'] )
    data.append( [msg['keyIndex'], 4] )
    data.append( [msg['channelOffset'], 4] )
    data.append( [0, 4] ) # Hopping sequence length is fixed to 0

    data = DTS_setParams( data )
    DTS_sndToUart( com, data )

def DTS_rcvAssociateConfirm( qitem ):
    params = []
    params.append( {'msgId': 4} )
    params.append( {'assocShortAddress': 4} )
    params.append( {'status': 4} )
    params.append( {'securityLevel': 4} )
    params.append( {'keyIdMode': 4} )
    params.append( {'keySource': [8, 'keySource']} )
    params.append( {'keyIndex': 4} )
    params.append( {'channelOffset': 4} )
    params.append( {'hoppingSequenceLength': 4} )
    params.append( {'hoppingSequence': ['hoppingSequenceLength', 'memcpy']} )

    msg = DTS_getParams( qitem, params )

    return msg

def DTS_rcvAssociateIndication( qitem ):
    params = []
    params.append( {'msgId': 4} )
    params.append( {'deviceAddress': 8} )
    params.append( {'capabilityInformation': 4} )
    params.append( {'securityLevel': 4} )
    params.append( {'keyIdMode': 4} )
    params.append( {'keySource': [8, 'keySource']} )
    params.append( {'keyIndex': 4} )
    params.append( {'channelOffset': 4} )
    params.append( {'hoppingSequenceId': 4} )

    msg = DTS_getParams( qitem, params )

    return msg


#############################
# DISASSOCIATE
#############################
def DTS_sndDisassociateRequest( com, msg ):
    data = []
    data.append( [msg['msgId'], 4] )
    data.append( [msg['deviceAddrMode'], 4] )
    data.append( [msg['devicePANId'], 4] )
    data.append( [msg['deviceAddress'], 8] )
    data.append( [msg['disassociateReason'], 4] )
    data.append( [msg['txIndirect'], 4] )
    data.append( [msg['securityLevel'], 4] )
    data.append( [msg['keyIdMode'], 4] )
    data.append( [msg['keySource'], len( msg['keySource'] ), 'keySource'] )
    data.append( [msg['keyIndex'], 4] )

    data = DTS_setParams( data )
    DTS_sndToUart( com, data )

def DTS_rcvDisassociateConfirm( qitem ):
    params = []
    params.append( {'msgId': 4} )
    params.append( {'status': 4} )
    params.append( {'deviceAddrMode': 4} )
    params.append( {'devicePANId': 4} )
    params.append( {'deviceAddress': 8} )

    msg = DTS_getParams( qitem, params )

    return msg

def DTS_rcvDisassociateIndication( qitem ):
    params = []
    params.append( {'msgId': 4} )
    params.append( {'deviceAddress': 8} )
    params.append( {'disassociateReason': 4} )
    params.append( {'securityLevel': 4} )
    params.append( {'keyIdMode': 4} )
    params.append( {'keySource': [8, 'keySource']} )
    params.append( {'keyIndex': 4} )

    msg = DTS_getParams( qitem, params )

    return msg


#############################
# ORPHAN
#############################
def DTS_sndOrphanResponse( com, msg ):
    data = []
    data.append( [msg['msgId'], 4] )
    data.append( [msg['orphanAddress'], 8] )
    data.append( [msg['shortAddress'], 4] )
    data.append( [msg['associatedMember'], 4] )
    data.append( [msg['securityLevel'], 4] )
    data.append( [msg['keyIdMode'], 4] )
    data.append( [msg['keySource'], len( msg['keySource'] ), 'keySource'] )
    data.append( [msg['keyIndex'], 4] )

    data = DTS_setParams( data )
    DTS_sndToUart( com, data )

def DTS_rcvOrphanIndication( qitem ):
    params = []
    params.append( {'msgId': 4} )
    params.append( {'orphanAddress': 8} )
    params.append( {'securityLevel': 4} )
    params.append( {'keyIdMode': 4} )
    params.append( {'keySource': [8, 'keySource']} )
    params.append( {'keyIndex': 4} )

    msg = DTS_getParams( qitem, params )

    return msg


#############################
# KEEP ALIVE
#############################
def DTS_sndKeepAliveRequest( com, msg ):
    data = []
    data.append( [msg['msgId'], 4] )
    data.append( [msg['dstAddress'], 4] )
    data.append( [msg['keepAlivePeriod'], 4] )

    data = DTS_setParams( data )
    DTS_sndToUart( com, data )

def DTS_rcvKeepAliveConfirm( qitem ):
    params = []
    params.append( {'msgId': 4} )
    params.append( {'status': 4} )

    msg = DTS_getParams( qitem, params )

    return msg


#############################
# SYNC LOSS
#############################
def DTS_rcvSyncLossIndication( qitem ):
    params = []
    params.append( {'msgId': 4} )
    params.append( {'lossReason': 4} )
    params.append( {'PANId': 4} )
    params.append( {'channelNumber': 4} )
    params.append( {'channelPage': 4} )
    params.append( {'securityLevel': 4} )
    params.append( {'keyIdMode': 4} )
    params.append( {'keySource': [8, 'keySource']} )
    params.append( {'keyIndex': 4} )

    msg = DTS_getParams( qitem, params )

    return msg


#############################
# COMM STATUS
#############################
def DTS_rcvCommStatusIndication( qitem ):
    params = []
    params.append( {'msgId': 4} )
    params.append( {'PANId': 4} )
    params.append( {'srcAddrMode': 4} )
    params.append( {'srcAddr': 8} )
    params.append( {'dstAddrMode': 4} )
    params.append( {'dstAddr': 8} )
    params.append( {'status': 4} )
    params.append( {'securityLevel': 4} )
    params.append( {'keyIdMode': 4} )
    params.append( {'keySource': [8, 'keySource']} )
    params.append( {'keyIndex': 4} )

    msg = DTS_getParams( qitem, params )

    return msg


#############################
# TRANSPARENT
#############################
def DTS_enableTransparantMode( com, enable, options ):
    dtsLog.info( 'Calling FTDF_enableTransparantMode (COM port ID: %s)' % com )
    dtsLog.debug( 'enable=%s options=%s' % ( enable, options ) )

    data = []
    data.append( [ftdf.DTS_MSG_ID_ENA_TRANS, 4] )
    data.append( [enable, 4] )
    data.append( [options, 4] )

    data = DTS_setParams( data )
    DTS_sndToUart( com, data )

def DTS_sendFrameTransparant( com, length, frame, channel, csmaSuppress, handle=0, pti=0 ):
    # Handle has become obsolete, but is still present for legacy reasons
    dtsLog.info( 'Calling FTDF_sendFrameTransparant (COM port ID: %s)' % com )
    dtsLog.debug( 'length=%s channel=%s csmaSuppress=%s' % ( length, channel, csmaSuppress ) )
    dtsLog.debug( 'frame=%s', frame )

    data = []
    data.append( [ftdf.DTS_MSG_ID_SND_TRANS, 4] )
    data.append( [length, 4] )
    data.append( [frame, length, 'memcpy'] )
    data.append( [channel, 4] )
    data.append( [pti, 4] )
    data.append( [csmaSuppress, 4] )

    data = DTS_setParams( data )
    DTS_sndToUart( com, data )

def DTS_rcvSendFrameTransparantConfirm( qitem ):
    params = []
    params.append( {'msgId': 4} )
    params.append( {'status': 4} )

    msg = DTS_getParams( qitem, params )

    return msg

def DTS_rcvFrameTransparant( qitem ):
    params = []
    params.append( {'msgId': 4} )
    params.append( {'frameLength': 4} )
    params.append( {'frame': ['frameLength', 'memcpy']} )
    params.append( {'status': 4} )

    msg = DTS_getParams( qitem, params )

    return msg


#############################
# SLEEP
#############################
def DTS_sndSleepRequest( com, msg ):
    data = []
    data.append( [msg['msgId'], 4] )
    data.append( [msg['sleepTime'], 4] )

    data = DTS_setParams( data )
    DTS_sndToUart( com, data )

def DTS_rcvExplicitWakeUp( qitem ):
    params = []
    params.append( {'msgId': 4} )

    msg = DTS_getParams( qitem, params )

    return msg

def DTS_setSleepAttributes( com, lowPowerClockCycle, wakeupLatency ):
    dtsLog.info( 'Calling FTDF_setSleepAttributes (COM port ID: %s)' % com )
    dtsLog.debug( 'lowPowerClockCycle=%s wakeupLatency=%s' % ( lowPowerClockCycle, wakeupLatency ) )

    data = []
    data.append( [ftdf.DTS_MSG_ID_SET_LOW_POWER_CLK, 4] )
    data.append( [lowPowerClockCycle, 8] )
    data.append( [wakeupLatency, 4] )

    data = DTS_setParams( data )
    DTS_sndToUart( com, data )

def DTS_canSleep( com ):
    dtsLog.info( 'Calling FTDF_canSleep (COM port ID: %s)' % com )

    data = []
    data.append( [ftdf.DTS_MSG_ID_CAN_POWER_OFF, 4] )

    data = DTS_setParams( data )
    DTS_sndToUart( com, data )

def DTS_rcvCanSleep( qitem ):
    params = []
    params.append( {'msgId': 4} )
    params.append( {'usec': 4} )

    msg = DTS_getParams( qitem, params )

    return msg

def DTS_prepareForSleep( com, sleepTime ):
    dtsLog.info( 'Calling FTDF_prepareForSleep (COM port ID: %s)' % com )
    dtsLog.debug( 'sleepTime=%s' % sleepTime )

    data = []
    data.append( [ftdf.DTS_MSG_ID_PREP_POWER_OFF, 4] )
    data.append( [sleepTime, 4] )

    data = DTS_setParams( data )
    DTS_sndToUart( com, data )

def DTS_rcvPrepareForSleep( qitem ):
    params = []
    params.append( {'msgId': 4} )
    params.append( {'success': 4} )

    msg = DTS_getParams( qitem, params )

    return msg

def DTS_wakeUp( com ):
    dtsLog.info( 'Calling FTDF_wakeUp (COM port ID: %s)' % com )

    data = []
    data.append( [ftdf.DTS_MSG_ID_WAKE_UP, 4] )

    data = DTS_setParams( data )
    DTS_sndToUart( com, data )

def DTS_rcvWakeUpReady( qitem ):
    params = []
    params.append( {'msgId': 4} )

    msg = DTS_getParams( qitem, params )

    return msg


#############################
# RELEASE INFO
#############################
def DTS_getReleaseInfo( com ):
    dtsLog.info( 'Calling FTDF_getReleaseInfo( COM port ID: %s)' % com )

    data = []
    data.append( [ftdf.DTS_MSG_ID_REL_INFO, 4] )

    data = DTS_setParams( data )
    DTS_sndToUart( com, data )

def DTS_rcvReleaseInfo( qitem ):
    params = []
    params.append( {'msgId': 4} )
    params.append( {'lmacRelName': [16, 'strcpy']} )
    params.append( {'lmacBuildTime': [16, 'strcpy']} )
    params.append( {'umacRelName': [16, 'strcpy']} )
    params.append( {'umacBuildTime': [16, 'strcpy']} )

    msg = DTS_getParams( qitem, params )

    return msg

#############################
# REGISTER ACCESS
#############################
def DTS_setRegister( com, addr, size, val ):
    dtsLog.info( 'Calling FTDF_setRegister (COM port ID: %s)' % com )
    dtsLog.debug( 'addr=0x%x size=%s val=0x%x' % ( addr, size, val ) )

    data = []
    data.append( [ftdf.DTS_MSG_ID_SET_REG, 4] )
    data.append( [addr, 4] )
    data.append( [size, 4] )
    data.append( [val, 4] )

    data = DTS_setParams( data )
    DTS_sndToUart( com, data )

def DTS_getRegister( com, addr, size ):
    dtsLog.info( 'Calling FTDF_getRegister (COM port ID: %s)' % com )
    dtsLog.debug( 'addr=0x%x size=%s' % ( addr, size ) )

    data = []
    data.append( [ftdf.DTS_MSG_ID_GET_REG, 4] )
    data.append( [addr, 4] )
    data.append( [size, 4] )

    data = DTS_setParams( data )
    DTS_sndToUart( com, data )

def DTS_rcvGetRegister( qitem ):
    params = []
    params.append( {'msgId': 4} )
    params.append( {'val': 4} )

    msg = DTS_getParams( qitem, params )

    return msg

def DTS_rcvBLEEvt( qitem ):
    params = []
    params.append( {'msgId': 4} )
    params.append( {'evt_code': 4} )
    
    msg = DTS_getParams( qitem, params )
    
    if msg['evt_code'] == ftdf.DTS_BLE_EVT_CODE_GAP_ADV_REPORT:
        params.append( {'adv_type': 4})
        params.append( {'adv_addr_type': 4})
        params.append( {'adv_addr_0': 4})
        params.append( {'adv_addr_1': 4})
        params.append( {'adv_addr_2': 4})
        params.append( {'adv_addr_3': 4})
        params.append( {'adv_addr_4': 4})
        params.append( {'adv_addr_5': 4})
        params.append( {'rssi': 4})
        msg = DTS_getParams( qitem, params )
    
    if msg['evt_code'] == ftdf.DTS_BLE_EVT_CODE_GATTC_READ_COMPLETED:
        params.append( {'value': 4})
        msg = DTS_getParams( qitem, params )
    
    return msg

def DTS_rcvBLEStatus( qitem ):
    params = []
    params.append( {'msgId': 4} )
    params.append( {'ble_status': 4} )

    msg = DTS_getParams( qitem, params )

    return msg

def DTS_rcvBLEGeneric( qitem ):
    params = []
    params.append( {'msgId': 4} )

    msg = DTS_getParams( qitem, params )

    return msg

def DTS_rcvBLEMsgLog( qitem ):
    params = []
    params.append( {'msgId': 4} )
    params.append( {'msgIdx': 4} )
    params.append( {'overflow': 4} )
    params.append( {'is_enabled': 4} )
    params.append( {'msgId0': 4} )
    params.append( {'evtCode0': 4} )
    params.append( {'msgId1': 4} )
    params.append( {'evtCode1': 4} )
    params.append( {'msgId2': 4} )
    params.append( {'evtCode2': 4} )
    params.append( {'msgId3': 4} )
    params.append( {'evtCode3': 4} )

    msg = DTS_getParams( qitem, params )

    return msg

def DTS_rcvBLEStats( qitem ):
    params = []
    params.append( {'msgId': 4} )
    params.append( {'bleTotalDataPackets': 4} )
    params.append( {'bleDataPacketErrors': 4} )

    msg = DTS_getParams( qitem, params )

    return msg


def DTS_rcvCoexStats( qitem ):
    params = []
    params.append( {'msgId': 4} )
    params.append( {'decisionSw': 4} )
    params.append( {'txrxMonOverflow': 4} )
    params.append( {'txrxMonTxPassed1': 4} )
    params.append( {'txrxMonTxMasked1': 4} )
    params.append( {'txrxMonRxPassed1': 4} )
    params.append( {'txrxMonRxMasked1': 4} )
    params.append( {'txrxMonTxPassed2': 4} )
    params.append( {'txrxMonTxMasked2': 4} )
    params.append( {'txrxMonRxPassed2': 4} )
    params.append( {'txrxMonRxMasked2': 4} )
    params.append( {'txrxMonTxPassed3': 4} )
    params.append( {'txrxMonTxMasked3': 4} )
    params.append( {'txrxMonRxPassed3': 4} )
    params.append( {'txrxMonRxMasked3': 4} )
    params.append( {'txrxMonTxPassed4': 4} )
    params.append( {'txrxMonTxMasked4': 4} )
    params.append( {'txrxMonRxPassed4': 4} )
    params.append( {'txrxMonRxMasked4': 4} )
    params.append( {'txrxMonTxPassed5': 4} )
    params.append( {'txrxMonTxMasked5': 4} )
    params.append( {'txrxMonRxPassed5': 4} )
    params.append( {'txrxMonRxMasked5': 4} )
    params.append( {'txrxMonTxPassed6': 4} )
    params.append( {'txrxMonTxMasked6': 4} )
    params.append( {'txrxMonRxPassed6': 4} )
    params.append( {'txrxMonRxMasked6': 4} )
    params.append( {'txrxMonTxPassed7': 4} )
    params.append( {'txrxMonTxMasked7': 4} )
    params.append( {'txrxMonRxPassed7': 4} )
    params.append( {'txrxMonRxMasked7': 4} )
    params.append( {'txrxMonTxPassed8': 4} )
    params.append( {'txrxMonTxMasked8': 4} )
    params.append( {'txrxMonRxPassed8': 4} )
    params.append( {'txrxMonRxMasked8': 4} )
    params.append( {'txrxMonTxPassed9': 4} )
    params.append( {'txrxMonTxMasked9': 4} )
    params.append( {'txrxMonRxPassed9': 4} )
    params.append( {'txrxMonRxMasked9': 4} )
    params.append( {'txrxMonTxPassed10': 4} )
    params.append( {'txrxMonTxMasked10': 4} )
    params.append( {'txrxMonRxPassed10': 4} )
    params.append( {'txrxMonRxMasked10': 4} )
    params.append( {'txrxMonTxPassed11': 4} )
    params.append( {'txrxMonTxMasked11': 4} )
    params.append( {'txrxMonRxPassed11': 4} )
    params.append( {'txrxMonRxMasked11': 4} )
    params.append( {'txrxMonTxPassed12': 4} )
    params.append( {'txrxMonTxMasked12': 4} )
    params.append( {'txrxMonRxPassed12': 4} )
    params.append( {'txrxMonRxMasked12': 4} )
    params.append( {'txrxMonTxPassed13': 4} )
    params.append( {'txrxMonTxMasked13': 4} )
    params.append( {'txrxMonRxPassed13': 4} )
    params.append( {'txrxMonRxMasked13': 4} )
    params.append( {'txrxMonTxPassed14': 4} )
    params.append( {'txrxMonTxMasked14': 4} )
    params.append( {'txrxMonRxPassed14': 4} )
    params.append( {'txrxMonRxMasked14': 4} )
    params.append( {'txrxMonTxPassed15': 4} )
    params.append( {'txrxMonTxMasked15': 4} )
    params.append( {'txrxMonRxPassed15': 4} )
    params.append( {'txrxMonRxMasked15': 4} )
    msg = DTS_getParams( qitem, params )

    return msg

#############################
# DDPHY Access
#############################
def DTS_ddphySet( com, ccaNegEnable ):
    dtsLog.info( 'Calling DTS_ddphySet (COM port ID: %s)' % com )
    dtsLog.debug( 'ccaNegEnable=0x%x' % ( ccaNegEnable ) )
    if ccaNegEnable == 0:
        ccaReg = 0
    else:
        ccaReg = 1
    data = []
    data.append( [ftdf.DTS_MSG_ID_DDPHY_SET, 4] )
    data.append( [ccaReg, 4] )

    data = DTS_setParams( data )
    DTS_sndToUart( com, data )
    
##################################
# Queue, burst, repeat
##################################
def DTS_setQueueParameters( com, status, mode, repeat, interval ):
    dtsLog.info( 'Calling DTS_setQueueParameters (COM port ID: %s)' % com )
    dtsLog.debug( 'status=%s mode=%s repeat=%s interval=%s' % ( status, mode, repeat, interval ) )

    data = []
    data.append( [ftdf.DTS_MSG_ID_SET_QUEUE_PARAMS, 4] )
    data.append( [status, 4] )
    data.append( [mode, 4] )
    data.append( [repeat, 4] )
    data.append( [interval, 4] )

    data = DTS_setParams( data )
    DTS_sndToUart( com, data )

def DTS_setQueueEnable( com, enable ):
    dtsLog.info( 'Calling DTS_setQueueEnable (COM port ID: %s)' % com )
    dtsLog.debug( 'enable=%s' % enable )

    data = []
    data.append( [ftdf.DTS_MSG_ID_SET_QUEUE_ENABLE, 4] )
    data.append( [enable, 4] )

    data = DTS_setParams( data )
    DTS_sndToUart( com, data )

def DTS_rcvQueueSummary( qitem ):
    params = []
    params.append( {'msgId': 4} )
    params.append( {'msgTotal': 4} )
    params.append( {'msgSuccess': 4} )
    params.append( {'msgChannelAccessFailure': 4} )
    params.append( {'msgNoAck': 4} )
    params.append( {'msgMiscErrors': 4} )
    params.append( {'duration': 4} )

    msg = DTS_getParams( qitem, params )

    return msg


##################################
# Sleep when possible
##################################
def DTS_sleepWhenPossible( com, sleepWhenPossible ):
    dtsLog.info( 'Calling DTS_sleepWhenPossible (COM port ID: %s)' % com )
    dtsLog.debug( 'sleepWhenPossible=%s' % sleepWhenPossible )

    data = []
    data.append( [ftdf.DTS_MSG_ID_SLEEP_WHEN_POSSIBLE, 4] )
    data.append( [sleepWhenPossible, 4] )

    data = DTS_setParams( data )
    DTS_sndToUart( com, data )


##################################
# Simulate BLE stack
##################################
def DTS_simulateBLE( com, enable ):
    dtsLog.info( 'Calling DTS_simulateBLE (COM port ID: %s)' % com )
    dtsLog.debug( 'enable=%s' % ( enable ) )

    data = []
    data.append( [ftdf.DTS_MSG_ID_SIM_BLE, 4] )
    data.append( [enable, 4] )

    data = DTS_setParams( data )
    DTS_sndToUart( com, data )

##################################
# BLE commands
##################################
def DTS_BLEConnect( com, interval_min, interval_max, slave_latency, sup_timeout):
    dtsLog.info( 'Calling DTS_BLEConnect (COM port ID: %s)' % com )
    dtsLog.debug( 'interval_min = %s interval_max = %s, slave_latency = %s, sup_timeout = %s' % 
                  ( interval_min, interval_max, slave_latency, sup_timeout ))
    data = []
    data.append( [ftdf.DTS_MSG_ID_BLE_CMD, 4] )
    data.append( [ftdf.DTS_BLE_CMD_CONNECT, 4] )
    data.append( [interval_min, 4] )
    data.append( [interval_max, 4] )
    data.append( [slave_latency, 4] )
    data.append( [sup_timeout, 4] )
    data = DTS_setParams( data )
    DTS_sndToUart(com, data)

def DTS_BLEScan(com, scan_type, interval, window):
    dtsLog.info( 'Calling DTS_BLEScan (COM port ID: %s)' % com )
    dtsLog.debug( 'scan_type = %s interval = %s window = %s' % (scan_type, interval, window))
    data = []
    data.append( [ftdf.DTS_MSG_ID_BLE_CMD, 4] )
    data.append( [ftdf.DTS_BLE_CMD_SCAN, 4] )
    data.append( [scan_type, 4] )
    data.append( [interval, 4] )
    data.append( [window, 4] )
    data = DTS_setParams( data )
    DTS_sndToUart(com, data)

def DTS_BLERead(com ):
    dtsLog.info( 'Calling DTS_BLERead (COM port ID: %s)' % com )
    data = []
    data.append( [ftdf.DTS_MSG_ID_BLE_CMD, 4] )
    data.append( [ftdf.DTS_BLE_CMD_READ, 4] )
    data = DTS_setParams( data )
    DTS_sndToUart(com, data)

def DTS_BLEWrite(com, value ):
    dtsLog.info( 'Calling DTS_BLEWrite (COM port ID: %s)' % com )
    dtsLog.debug( 'value = %s ' % value )
    data = []
    data.append( [ftdf.DTS_MSG_ID_BLE_CMD, 4] )
    data.append( [ftdf.DTS_BLE_CMD_WRITE, 4] )
    data.append( [value, 4] )
    data = DTS_setParams( data )
    DTS_sndToUart(com, data)

def DTS_BLEAdvertise(com, conn_mode, interval_min, interval_max):
    dtsLog.info( 'Calling DTS_BLEAdvertise (COM port ID: %s)' % com )
    dtsLog.debug( 'conn_mode = %s interval_min = %s interval_max = %s' % (conn_mode, interval_min, interval_max))
    data = []
    data.append( [ftdf.DTS_MSG_ID_BLE_CMD, 4] )
    data.append( [ftdf.DTS_BLE_CMD_ADVERTISE, 4] )
    data.append( [conn_mode, 4] )
    data.append( [interval_min, 4] )
    data.append( [interval_max, 4] )
    data = DTS_setParams( data )
    DTS_sndToUart(com, data)
    
def DTS_BLEStop(com):
    dtsLog.info( 'Calling DTS_BLEStop (COM port ID: %s)' % com )
    data = []
    data.append( [ftdf.DTS_MSG_ID_BLE_CMD, 4] )
    data.append( [ftdf.DTS_BLE_CMD_STOP, 4] )
    data = DTS_setParams( data )
    DTS_sndToUart(com, data)

def DTS_BLEReset(com):
    dtsLog.info( 'Calling DTS_BLEReset (COM port ID: %s)' % com )
    data = []
    data.append( [ftdf.DTS_MSG_ID_BLE_CMD, 4] )
    data.append( [ftdf.DTS_BLE_CMD_RESET, 4] )
    data = DTS_setParams( data )
    DTS_sndToUart(com, data)
  
def DTS_BLESetSleepMode(com, sleepMode):
    dtsLog.info( 'Calling DTS_BLESetSleepMode (COM port ID: %s)' % com )
    dtsLog.debug( 'sleepMode=%s' % ( sleepMode ) )
    data = []
    data.append( [ftdf.DTS_MSG_ID_BLE_CMD, 4] )
    data.append( [ftdf.DTS_BLE_CMD_SET_SLEEP_MODE, 4] )
    data.append( [sleepMode, 4] )
    data = DTS_setParams( data )
    DTS_sndToUart(com, data)

def DTS_BLEConnectionOpen( peripheral, central, responseTimeout, interval_min, interval_max, slave_latency, sup_timeout):
    dtsLog.info( 'Calling DTS_BLEConnectionOpen (Peripheral COM port ID: %s, Central COM port ID: %s)' % (peripheral, central) )
    dtsLog.debug( 'responseTimeout = %s interval_min = %s interval_max = %s, slave_latency = %s, sup_timeout = %s' % 
                  ( responseTimeout, interval_min, interval_max, slave_latency, sup_timeout ))
    status = ftdf.DTS_BLE_FUNC_STATUS_OK
    reason = {}
    # Start peripheral
    DTS_BLEAdvertise( peripheral, ftdf.DTS_BLE_GAP_CONN_MODE_UNDIRECTED, 1100, 1100 )
    # Expect OK
    res, ret = DTS_getMsg( peripheral, responseTimeout)
    if ( res == False ):
        reason['expected'] = ftdf.DTS_MSG_ID_BLE_OK
        return ftdf.DTS_BLE_FUNC_STATUS_NO_RSP, reason 
    elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
        reason['expected'] = ftdf.DTS_MSG_ID_BLE_OK
        reason['received'] = ret['msgId']
        return ftdf.DTS_BLE_FUNC_STATUS_MSG_ID, reason
    
    # Start central
    DTS_BLEConnect( central, interval_min, interval_max, slave_latency, sup_timeout)
    # Expect OK
    res, ret = DTS_getMsg( central, responseTimeout)
    if ( res == False ):
        reason['expected'] = ftdf.DTS_MSG_ID_BLE_OK
        return ftdf.DTS_BLE_FUNC_STATUS_NO_RSP, reason 
    elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
        reason['expected'] = ftdf.DTS_MSG_ID_BLE_OK
        reason['received'] = ret['msgId']
        return ftdf.DTS_BLE_FUNC_STATUS_MSG_ID, reason
      
    # Expect GAP connect on both devices.
    res, ret = DTS_getMsg( peripheral, responseTimeout)
    if ( res == False ):
        reason['expected'] = ftdf.DTS_MSG_ID_BLE_EVT
        return ftdf.DTS_BLE_FUNC_STATUS_NO_RSP, reason 
    elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_EVT:
        reason['expected'] = ftdf.DTS_MSG_ID_BLE_EVT
        reason['received'] = ret['msgId']
        return ftdf.DTS_BLE_FUNC_STATUS_MSG_ID, reason
    elif ret['evt_code'] != ftdf.DTS_BLE_EVT_CODE_GAP_CONNECTED:
        reason['expected'] = ftdf.DTS_BLE_EVT_CODE_GAP_CONNECTED
        reason['received'] = ret['evt_code']
        return ftdf.DTS_BLE_FUNC_STATUS_BLE_EVT, reason
      
    res, ret = DTS_getMsg( central, responseTimeout)
    if ( res == False ):
        reason['expected'] = ftdf.DTS_MSG_ID_BLE_EVT
        return ftdf.DTS_BLE_FUNC_STATUS_NO_RSP, reason 
    elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_EVT:
        reason['expected'] = ftdf.DTS_MSG_ID_BLE_EVT
        reason['received'] = ret['msgId']
        return ftdf.DTS_BLE_FUNC_STATUS_MSG_ID, reason
    elif ret['evt_code'] != ftdf.DTS_BLE_EVT_CODE_GAP_CONNECTED:
        reason['expected'] = ftdf.DTS_BLE_EVT_CODE_GAP_CONNECTED
        reason['received'] = ret['evt_code']
        return ftdf.DTS_BLE_FUNC_STATUS_BLE_EVT, reason
    
    # Expect advertisement completed in peripheral
    res, ret = DTS_getMsg( peripheral, responseTimeout)
    if ( res == False ):
        reason['expected'] = ftdf.DTS_MSG_ID_BLE_EVT
        return ftdf.DTS_BLE_FUNC_STATUS_NO_RSP, reason 
    elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_EVT:
        reason['expected'] = ftdf.DTS_MSG_ID_BLE_EVT
        reason['received'] = ret['msgId']
        return ftdf.DTS_BLE_FUNC_STATUS_MSG_ID, reason
    elif ret['evt_code'] != ftdf.DTS_BLE_EVT_CODE_GAP_ADV_COMPLETED:
        reason['expected'] = ftdf.DTS_BLE_EVT_CODE_GAP_ADV_COMPLETED
        reason['received'] = ret['evt_code']
        return ftdf.DTS_BLE_FUNC_STATUS_BLE_EVT, reason

    # Expect connection completed in central
    res, ret = DTS_getMsg( central, responseTimeout)
    if ( res == False ):
        reason['expected'] = ftdf.DTS_MSG_ID_BLE_EVT
        return ftdf.DTS_BLE_FUNC_STATUS_NO_RSP, reason 
    elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_EVT:
        reason['expected'] = ftdf.DTS_MSG_ID_BLE_EVT
        reason['received'] = ret['msgId']
        return ftdf.DTS_BLE_FUNC_STATUS_MSG_ID, reason
    elif ret['evt_code'] != ftdf.DTS_BLE_EVT_CODE_GAP_CONNECTION_COMPLETED:
        reason['expected'] = ftdf.DTS_BLE_EVT_CODE_GAP_CONNECTION_COMPLETED
        reason['received'] = ret['evt_code']
        return ftdf.DTS_BLE_FUNC_STATUS_BLE_EVT, reason
    
    # Expect service discover on central
    res, ret = DTS_getMsg( central, responseTimeout)
    if ( res == False ):
        reason['expected'] = ftdf.DTS_MSG_ID_BLE_EVT
        return ftdf.DTS_BLE_FUNC_STATUS_NO_RSP, reason 
    elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_EVT:
        reason['expected'] = ftdf.DTS_MSG_ID_BLE_EVT
        reason['received'] = ret['msgId']
        return ftdf.DTS_BLE_FUNC_STATUS_MSG_ID, reason
    elif ret['evt_code'] != ftdf.DTS_BLE_EVT_CODE_GATTC_DISCOVER_SVC:
        reason['expected'] = ftdf.DTS_BLE_EVT_CODE_GATTC_DISCOVER_SVC
        reason['received'] = ret['evt_code']
        return ftdf.DTS_BLE_FUNC_STATUS_BLE_EVT, reason
    
    # Expect discover complete on central
    res, ret = DTS_getMsg( central, responseTimeout)
    if ( res == False ):
        reason['expected'] = ftdf.DTS_MSG_ID_BLE_EVT
        return ftdf.DTS_BLE_FUNC_STATUS_NO_RSP, reason 
    elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_EVT:
        reason['expected'] = ftdf.DTS_MSG_ID_BLE_EVT
        reason['received'] = ret['msgId']
        return ftdf.DTS_BLE_FUNC_STATUS_MSG_ID, reason
    elif ret['evt_code'] != ftdf.DTS_BLE_EVT_CODE_GATTC_DISCOVER_COMPLETED:
        reason['expected'] = ftdf.DTS_BLE_EVT_CODE_GATTC_DISCOVER_COMPLETED
        reason['received'] = ret['evt_code']
        return ftdf.DTS_BLE_FUNC_STATUS_BLE_EVT, reason
    
    # Expect attribute discover on central
    res, ret = DTS_getMsg( central, responseTimeout)
    if ( res == False ):
        reason['expected'] = ftdf.DTS_MSG_ID_BLE_EVT
        return ftdf.DTS_BLE_FUNC_STATUS_NO_RSP, reason 
    elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_EVT:
        reason['expected'] = ftdf.DTS_MSG_ID_BLE_EVT
        reason['received'] = ret['msgId']
        return ftdf.DTS_BLE_FUNC_STATUS_MSG_ID, reason
    elif ret['evt_code'] != ftdf.DTS_BLE_EVT_CODE_GATTC_DISCOVER_CHAR:
        reason['expected'] = ftdf.DTS_BLE_EVT_CODE_GATTC_DISCOVER_CHAR
        reason['received'] = ret['evt_code']
        return ftdf.DTS_BLE_FUNC_STATUS_BLE_EVT, reason
    
    # Expect discover complete on central
    res, ret = DTS_getMsg( central, responseTimeout)
    if ( res == False ):
        reason['expected'] = ftdf.DTS_MSG_ID_BLE_EVT
        return ftdf.DTS_BLE_FUNC_STATUS_NO_RSP, reason 
    elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_EVT:
        reason['expected'] = ftdf.DTS_MSG_ID_BLE_EVT
        reason['received'] = ret['msgId']
        return ftdf.DTS_BLE_FUNC_STATUS_MSG_ID, reason
    elif ret['evt_code'] != ftdf.DTS_BLE_EVT_CODE_GATTC_DISCOVER_COMPLETED:
        reason['expected'] = ftdf.DTS_BLE_EVT_CODE_GATTC_DISCOVER_COMPLETED
        reason['received'] = ret['evt_code']
        return ftdf.DTS_BLE_FUNC_STATUS_BLE_EVT, reason
        
    return ftdf.DTS_BLE_FUNC_STATUS_OK, 0

def DTS_BLEConnectionClose( peripheral, central, responseTimeout ):
    dtsLog.info( 'Calling DTS_BLEConnectionClose (Peripheral COM port ID: %s, Central COM port ID: %s)' % (peripheral, central) )
    dtsLog.debug( 'responseTimeout = %s' % ( responseTimeout ))
    status = ftdf.DTS_BLE_FUNC_STATUS_OK
    reason = {}
    # Stop central
    DTS_BLEStop(central)
    # Expect OK
    res, ret = DTS_getMsg( central, responseTimeout)
    if ( res == False ):
        reason['expected'] = ftdf.DTS_MSG_ID_BLE_OK
        return ftdf.DTS_BLE_FUNC_STATUS_NO_RSP, reason 
    elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
        reason['expected'] = ftdf.DTS_MSG_ID_BLE_OK
        reason['received'] = ret['msgId']
        return ftdf.DTS_BLE_FUNC_STATUS_MSG_ID, reason
    
    # Expect GAP disconnect on both devices.
    res, ret = DTS_getMsg( peripheral, responseTimeout)
    if ( res == False ):
        reason['expected'] = ftdf.DTS_MSG_ID_BLE_EVT
        return ftdf.DTS_BLE_FUNC_STATUS_NO_RSP, reason 
    elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_EVT:
        reason['expected'] = ftdf.DTS_MSG_ID_BLE_EVT
        reason['received'] = ret['msgId']
        return ftdf.DTS_BLE_FUNC_STATUS_MSG_ID, reason
    elif ret['evt_code'] != ftdf.DTS_BLE_EVT_CODE_GAP_DISCONNECTED:
        reason['expected'] = ftdf.DTS_BLE_EVT_CODE_GAP_DISCONNECTED
        reason['received'] = ret['evt_code']
        return ftdf.DTS_BLE_FUNC_STATUS_BLE_EVT, reason
      
    res, ret = DTS_getMsg( central, responseTimeout)
    if ( res == False ):
        reason['expected'] = ftdf.DTS_MSG_ID_BLE_EVT
        return ftdf.DTS_BLE_FUNC_STATUS_NO_RSP, reason 
    elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_EVT:
        reason['expected'] = ftdf.DTS_MSG_ID_BLE_EVT
        reason['received'] = ret['msgId']
        return ftdf.DTS_BLE_FUNC_STATUS_MSG_ID, reason
    elif ret['evt_code'] != ftdf.DTS_BLE_EVT_CODE_GAP_DISCONNECTED:
        reason['expected'] = ftdf.DTS_BLE_EVT_CODE_GAP_DISCONNECTED
        reason['received'] = ret['evt_code']
        return ftdf.DTS_BLE_FUNC_STATUS_BLE_EVT, reason
    return ftdf.DTS_BLE_FUNC_STATUS_OK, 0

#     # Stop peripheral
#     DTS_BLEStartCentral( peripheral, ftdf.DTS_BLE_CMD_STOP, 
#                 0, 0, 0, 0, 0)
#     # Expect OK
#     res, ret = DTS_getMsg( peripheral, responseTimeout)
#     if ( res == False ):
#         reason['expected'] = ftdf.DTS_MSG_ID_BLE_OK
#         return DTS_BLE_FUNC_STATUS_NO_RSP, reason 
#     elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
#         reason['expected'] = ftdf.DTS_MSG_ID_BLE_OK
#         reason['received'] = ret['msgId']
#         return ftdf.DTS_BLE_FUNC_STATUS_MSG_ID, reason

def DTS_BLEEnableSleep( com, responseTimeout ):
    status = ftdf.DTS_BLE_FUNC_STATUS_OK
    reason = {}
    # Set sleep mode
    DTS_BLESetSleepMode(com, ftdf.DTS_BLE_SLEEP_MODE_EXT_SLEEP)
    # Expect OK
    res, ret = DTS_getMsg( com, responseTimeout)
    if ( res == False ):
        reason['expected'] = ftdf.DTS_MSG_ID_BLE_OK
        return ftdf.DTS_BLE_FUNC_STATUS_NO_RSP, reason 
    elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
        reason['expected'] = ftdf.DTS_MSG_ID_BLE_OK
        reason['received'] = ret['msgId']
        return ftdf.DTS_BLE_FUNC_STATUS_MSG_ID, reason
    return status, reason

def DTS_BLEDisableSleep( com, responseTimeout ):
    status = ftdf.DTS_BLE_FUNC_STATUS_OK
    reason = {}
    # Set sleep mode
    DTS_BLESetSleepMode(com, ftdf.DTS_BLE_SLEEP_MODE_ACTIVE)
    # Expect OK
    res, ret = DTS_getMsg( com, responseTimeout)
    if ( res == False ):
        reason['expected'] = ftdf.DTS_MSG_ID_BLE_OK
        return ftdf.DTS_BLE_FUNC_STATUS_NO_RSP, reason 
    elif ret['msgId'] != ftdf.DTS_MSG_ID_BLE_OK:
        reason['expected'] = ftdf.DTS_MSG_ID_BLE_OK
        reason['received'] = ret['msgId']
        return ftdf.DTS_BLE_FUNC_STATUS_MSG_ID, reason
    return status, reason

def DTS_FTDFPERTest(sender, receiver, msgDATA, numFrames, interval, responseTimeout, 
                    msgRxEnable_On, msgRxEnable_Off):
    txPkt = 0
    rxPkt = 0
    duration = 0
    reason = {}
    
    # Turn Rx on on devId2
    DTS_sndMsg(receiver, msgRxEnable_On)
    
    # Expect confirm
    res, ret = DTS_getMsg(receiver, responseTimeout )
    if( res == False ):
        reason['expected'] = ftdf.FTDF_RX_ENABLE_CONFIRM
        return ftdf.DTS_BLE_FUNC_STATUS_NO_RSP, reason, txPkt, rxPkt, duration
    elif ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM:
        reason['expected'] = ftdf.FTDF_RX_ENABLE_CONFIRM
        reason['received'] = ret['msgId']
        return ftdf.DTS_BLE_FUNC_STATUS_MSG_ID, reason, txPkt, rxPkt, duration
    
    DTS_setQueueParameters( sender,
                       ftdf.DTS_QUEUE_SND,
                       ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                       numFrames - 1 , interval)

    DTS_setQueueParameters( receiver,
                           ftdf.DTS_QUEUE_RCV,
                           ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                           0 , 0)
    
    DTS_sndMsg( sender, msgDATA )
    
    # start sending of frames
    DTS_setQueueEnable( sender, True )
    
    res, ret = DTS_getMsg( sender, numFrames )
    
    if res == False:
        reason['expected'] = ftdf.DTS_MSG_ID_SND_QUEUE_SUMMARY
        return ftdf.DTS_BLE_FUNC_STATUS_NO_RSP, reason, txPkt, rxPkt, duration
    elif ret['msgId'] != ftdf.DTS_MSG_ID_SND_QUEUE_SUMMARY:
        reason['expected'] = ftdf.DTS_MSG_ID_SND_QUEUE_SUMMARY
        reason['received'] = ret['msgId']
        return ftdf.DTS_BLE_FUNC_STATUS_MSG_ID, reason, txPkt, rxPkt, duration
    
    txPkt = ret['msgSuccess']
    duration = ret['duration']
    time.sleep(2)
    
    DTS_setQueueParameters( sender,
                           ftdf.DTS_QUEUE_DIS,
                           ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                           0 , 0)
    
    DTS_setQueueParameters( receiver,
                           ftdf.DTS_QUEUE_DIS,
                           ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                           0 , 0)
    
    res, ret = DTS_getMsg( receiver, numFrames )
        
    if res == False:
        reason['expected'] = ftdf.DTS_MSG_ID_SND_QUEUE_SUMMARY
        return ftdf.DTS_BLE_FUNC_STATUS_NO_RSP, reason, txPkt, rxPkt, duration
    elif ret['msgId'] != ftdf.DTS_MSG_ID_SND_QUEUE_SUMMARY:
        reason['expected'] = ftdf.DTS_MSG_ID_SND_QUEUE_SUMMARY
        reason['received'] = ret['msgId']
        return ftdf.DTS_BLE_FUNC_STATUS_MSG_ID, reason, txPkt, rxPkt, duration
    
    rxPkt = ret['msgSuccess']
    
    # Turn Rx off on receiver
    DTS_sndMsg(receiver, msgRxEnable_Off)
    
    # Expect confirm
    res, ret = DTS_getMsg( receiver, responseTimeout )
    if( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    elif ret['msgId'] != ftdf.FTDF_RX_ENABLE_CONFIRM:
        logstr = ( 'SCRIPT: ERROR: Expected ', ftdf.FTDF_RX_ENABLE_CONFIRM, 
                   ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
        raise StopScript( ''.join( map( str, logstr ) ) )
    
    return ftdf.DTS_BLE_FUNC_STATUS_OK, reason, txPkt, rxPkt, duration

def DTS_BLEMsgLogEnable( com ):
    dtsLog.info( 'Calling DTS_BLEMsgLogEnable (COM port ID: %s)' % com )
    data = []
    data.append( [ftdf.DTS_MSG_ID_BLE_MSG_LOG_CMD, 4] )
    data.append( [ftdf.DTS_BLE_MSG_LOG_CMD_TYPE_ENABLE, 4] )
    data = DTS_setParams( data )
    DTS_sndToUart(com, data)

def DTS_BLEMsgLogDisable( com ):
    dtsLog.info( 'Calling DTS_BLEMsgLogDisable (COM port ID: %s)' % com )
    data = []
    data.append( [ftdf.DTS_MSG_ID_BLE_MSG_LOG_CMD, 4] )
    data.append( [ftdf.DTS_BLE_MSG_LOG_CMD_TYPE_DISABLE, 4] )
    data = DTS_setParams( data )
    DTS_sndToUart(com, data)
    
##################################
# Arbiter configuration
##################################
def DTS_ArbiterSetConfig( com,
                          ctrl, 
                          ble_manual_pti, ftdf_manual_pti, 
                          mac1, pti1,
                          mac2, pti2,
                          mac3, pti3,
                          mac4, pti4,
                          mac5, pti5,
                          mac6, pti6,
                          mac7, pti7,
                          mac8, pti8,
                          mac9, pti9,
                          mac10, pti10,
                          mac11, pti11,
                          mac12, pti12,
                          mac13, pti13,
                          mac14, pti14,
                          mac15, pti15,
                          mac16, pti16,
                          mac17, pti17):
    dtsLog.info( 'Calling DTS_ArbiterConfig (COM port ID: %s)' % com )
    dtsLog.debug( 'ctrl = %04x' % ( ctrl ) )
    dtsLog.debug( 'ble_manual_pti = %s ftdf_manual_pti = %s' % ( ble_manual_pti, ftdf_manual_pti ) )
    dtsLog.debug( 'mac1 = %s pti1 = %s' % ( mac1, pti1 ) )
    dtsLog.debug( 'mac2 = %s pti2 = %s' % ( mac2, pti2 ) )
    dtsLog.debug( 'mac3 = %s pti3 = %s' % ( mac3, pti3 ) )
    dtsLog.debug( 'mac4 = %s pti4 = %s' % ( mac4, pti4 ) )
    dtsLog.debug( 'mac5 = %s pti5 = %s' % ( mac5, pti5 ) )
    dtsLog.debug( 'mac6 = %s pti6 = %s' % ( mac6, pti6 ) )
    dtsLog.debug( 'mac7 = %s pti7 = %s' % ( mac7, pti7 ) )
    dtsLog.debug( 'mac8 = %s pti8 = %s' % ( mac8, pti8 ) )
    dtsLog.debug( 'mac9 = %s pti9 = %s' % ( mac9, pti9 ) )
    dtsLog.debug( 'mac10 = %s pti10 = %s' % ( mac10, pti10 ) )
    dtsLog.debug( 'mac11 = %s pti11 = %s' % ( mac11, pti11 ) )
    dtsLog.debug( 'mac12 = %s pti12 = %s' % ( mac12, pti12 ) )
    dtsLog.debug( 'mac13 = %s pti13 = %s' % ( mac13, pti13 ) )
    dtsLog.debug( 'mac14 = %s pti14 = %s' % ( mac14, pti14 ) )
    dtsLog.debug( 'mac15 = %s pti15 = %s' % ( mac15, pti15 ) )
    dtsLog.debug( 'mac16 = %s pti16 = %s' % ( mac16, pti16 ) )
    dtsLog.debug( 'mac17 = %s pti17 = %s' % ( mac17, pti17 ) )
    data = []
    data.append( [ftdf.DTS_MSG_ID_COEX_SET_CONFIG, 4] )
    data.append( [ctrl, 4] )
    data.append( [ble_manual_pti, 4] )
    data.append( [ftdf_manual_pti, 4] )
    data.append( [mac1, 4] )
    data.append( [pti1, 4] )
    data.append( [mac2, 4] )
    data.append( [pti2, 4] )
    data.append( [mac3, 4] )
    data.append( [pti3, 4] )
    data.append( [mac4, 4] )
    data.append( [pti4, 4] )
    data.append( [mac5, 4] )
    data.append( [pti5, 4] )
    data.append( [mac6, 4] )
    data.append( [pti6, 4] )
    data.append( [mac7, 4] )
    data.append( [pti7, 4] )
    data.append( [mac8, 4] )
    data.append( [pti8, 4] )
    data.append( [mac9, 4] )
    data.append( [pti9, 4] )
    data.append( [mac10, 4] )
    data.append( [pti10, 4] )
    data.append( [mac11, 4] )
    data.append( [pti11, 4] )
    data.append( [mac12, 4] )
    data.append( [pti12, 4] )
    data.append( [mac13, 4] )
    data.append( [pti13, 4] )
    data.append( [mac14, 4] )
    data.append( [pti14, 4] )
    data.append( [mac15, 4] )
    data.append( [pti15, 4] )
    data.append( [mac16, 4] )
    data.append( [pti16, 4] )
    data.append( [mac17, 4] )
    data.append( [pti17, 4] )
    data = DTS_setParams( data )
    DTS_sndToUart(com, data)  

def DTS_ArbiterReset ( com ):
    dtsLog.info( 'Calling DTS_ArbiterReset (COM port ID: %s)' % com )
    data = []
    data.append( [ftdf.DTS_MSG_ID_COEX_RESET, 4] )
    data = DTS_setParams( data )
    DTS_sndToUart(com, data)

def DTS_ArbiterSetExtStatus( com, is_active):
    dtsLog.info( 'Calling DTS_ArbiterSetExtStatus (COM port ID: %s)' % com )
    dtsLog.debug( 'is_active = %s' % ( is_active ) )
    data = []
    data.append( [ftdf.DTS_MSG_ID_COEX_SET_EXT_STATUS, 4] )
    data.append( [is_active, 4] )
    data = DTS_setParams( data )
    DTS_sndToUart(com, data)

def DTS_BleStatsReq( com ):
    dtsLog.info( 'Calling DTS_BleStatsReq (COM port ID: %s)' % com )
    data = []
    data.append( [ftdf.DTS_MSG_ID_BLE_STATS_REQ, 4] )
    data = DTS_setParams( data )
    DTS_sndToUart(com, data)

def DTS_CoexStatsReq( com ):
    dtsLog.info( 'Calling DTS_CoexStatsReq (COM port ID: %s)' % com )
    data = []
    data.append( [ftdf.DTS_MSG_ID_COEX_STATS, 4] )
    data = DTS_setParams( data )
    DTS_sndToUart(com, data)
    
##################################
# Debug mode
##################################    
def DTS_setDbgMode( com, msg ):
    dtsLog.info( 'Calling DTS_setDbgMode (COM port ID: %s)' % com )
    dtsLog.debug( 'dbgMode=%s' % ( msg['dbgMode'] ) )

    data = []
    data.append( [msg['msgId'], 4] )
    data.append( [msg['dbgMode'], 4] )

    data = DTS_setParams( data )
    DTS_sndToUart( com, data )  

##################################
# FPPR 
##################################
def DTS_setFpprMode( com, msg ):
    dtsLog.info( 'Calling DTS_setFpprMode (COM port ID: %s)' % com )
    dtsLog.debug( 'match_fp_value=%s fp_override=%s fp_force_value=%s' % ( msg['match_fp_value'], msg['fp_override'], msg['fp_force_value'] ) )

    data = []
    data.append( [msg['msgId'], 4] )
    data.append( [msg['match_fp_value'], 4] )
    data.append( [msg['fp_override'], 4] )
    data.append( [msg['fp_force_value'], 4] )

    data = DTS_setParams( data )
    DTS_sndToUart( com, data )

def DTS_isFPPRTableEmpty(com):
    initAddress = 0x40092008
    interval = 0x10
    for i in range (0, 24):
        address = initAddress + i * interval
        DTS_getRegister( com, address, 4 )
        res, ret = DTS_getMsg( com, 10 )
        if ((ret['val'] == 0x01) or (ret['val'] & 0x1f) != 0):
            return False
    return True

##################################    
# Main functions
##################################
def DTS_quit():
    DTS_closeAllPorts()
    quit()

class DTS_scriptThread( threading.Thread ):
    def __init__(self, scripts, abortOnFail):
        threading.Thread.__init__(self)
        self.scripts     = scripts
        self.abortOnFail = abortOnFail
        self.stopflag    = threading.Event()
    def stop(self):
        self.stopflag.set( )
    def run(self):
        results = []
        for script in self.scripts:
            DTS_stopped = 0
            DTS_consoleQueue.put( '\nExecuting script: ' + script )
            dtsLog.info( 'Executing script: %s' % script )
            try:
                exec(compile(open(script).read(), script, 'exec'), globals(), locals())
            except PerformanceResults as msg:
                DTS_consoleQueue.put( msg.msg )
                dtsLog.info( '%s' % (msg.msg) )
            except StopScript as msg:
                dtsLog.error( '%s' % (msg.msg) )
                DTS_stopped = 1
            except:
                dtsLog.error( 'Fatal error in script' )
                dtsLog.error( traceback.format_exc() )
                DTS_stopped = 1

            results.append( DTS_stopped )

            if DTS_stopped == 0:
                dtsLog.info( 'SCRIPT: PASSED' )
                DTS_consoleQueue.put( 'SCRIPT: PASSED' )
            else:
                dtsLog.error( 'SCRIPT: FAILED' )

            # Flush UART queue
            for y in DTS_serQueue.keys( ):
                while(True):
                    res, ret = DTS_getMsg(y,0.5)
                    if (res == False):
                        break

            # stop tests if script failed and abortOnFail
            if ( DTS_stopped != 0 and self.abortOnFail ):
                break

            # stop tests also if stopflag is set
            if self.stopflag.is_set( ):
                DTS_consoleQueue.put( 'Test aborted' )
                break

        # put results in queue and disable thread
        DTS_consoleQueue.put( results )

def DTS_startScripts( scripts ):
    DTS_closeAllPorts( )
    dtsParam.reInit( )

    if dtsParam.atFail == dtsparam.STOP:
        abortOnFail = True
    else:
        abortOnFail = False

    # Open COM ports with parameters from GUI config file
    for dut in (dtsParam.dut):
        if dut['id'] == '' or dut['port'] == '' or dut['address'] == '':
            continue

        DTS_openPort( int(dut['id']), dut['port'], int(dut['address'], 16) )

    thr = DTS_scriptThread( scripts, abortOnFail )
    thr.start( )
    return thr

def DTS_abortScripts( thr ):
    thr.stop( )


def DTS_disableLogger( ):
    global dtsLog

    # clean up the log handlers
    for loghandler in reversed(dtsLog.handlers):
        loghandler.close()
        dtsLog.removeHandler( loghandler )

def DTS_enableLogger( ):
    global dtsLog

    # re-init the dtsParam class, in case the configfile has been overwritten
    # the parameters and scripts are not applicable here.
    dtsParam.reInit()

    dtsLog = dtsparam.initLogger(dtsParam, DTS_StreamHandler(), True)

uart_dbg         = False
DTS_consoleQueue = Queue()

class DTS_StreamHandler(logging.StreamHandler):
    def __init__(self):
        logging.StreamHandler.__init__(self)

    def emit(self, record):
        msg = self.format(record)

        # put log msg in queue
        DTS_consoleQueue.put( {'level': record.levelname, 'msg': msg} )

if __name__ == '__main__':
    # Command line processing
    options     = {}
    parameters  = []
    scripts     = []
    argc        = len(sys.argv)
    i           = 1
    noscript    = False
    scriptparams= []

    while i < argc:
        a = sys.argv[i]
        i += 1
        if a[0] == '-':
            # Option
            multi     = False
            addToOpts = False

            if len(a) == 1:
                print('Expected option after -')
                quit()

            if a[1] == '?':
                options['h'] = ['USAGE']
                break
            elif a[1] == 'c':
                multi     = True
                addToOpts = True
            elif a[1] == 'd':
                options['d'] = 1
            elif a[1] == 'h':
                multi     = True
                addToOpts = True
            elif a[1] == 'o':
                noscript = True
            elif a[1] == 'u':
                uart_dbg = True
            else:
                print("Invalid option:", a)
                quit()

            if (len(a) > 2 ) and not multi:
                print("Unexpected characters after option:", a)
                quit()

            if addToOpts:
                if len(a) > 2:
                    opt = [a[2:]]
                else:
                    if i == argc:
                        if a[1] not in ['h']:
                            print("Expected parameter after:", a)
                        quit()
                        opt = []
                    else:
                        opt = [sys.argv[i]]
                        i += 1
                if a[1] in options:
                    options[a[1]] += opt
                else:
                    options[a[1]] = opt
        elif a.find('=') != -1:
            # Parameter
            parameters += [ a ]
        elif noscript:
            scriptparams += [ a ]
        else:
            # Script
            scripts += [ a ]

    if 'h' in options:
        subject = options['h']
        if subject:
            subject = subject[0].upper()
        else:
            subject = ''

        helpList = []
        helpList += dtsparam.help(subject)
        if (subject):
            print("Help about\033[1m", subject, "\033[0mnot found, use 'dts -h' or 'dts -h <subject>', where subject is one of:")
            print(str(helpList).strip("[]"))
        quit()


    if 'c' in options:
        cfgFile = options['c']
    else:
        cfgFile = ['config/dts.xml']

    # Init the DTS_Param class
    dtsParam = dtsparam.DTS_Param(cfgFile, parameters, scripts)

    if 'd' in options:
        for i in sorted(dtsParam.__dict__):
            print("%-16s: %s" % (i, dtsParam.__dict__[i]))
        quit()

    # Init the logger
    dtsLog = dtsparam.initLogger(dtsParam, DTS_StreamHandler(), True)

    if dtsParam.script:
        DTS_startScripts(dtsParam.script)

        finished = False

        while finished == False:
            qitem = 0
            try:
                qitem = DTS_consoleQueue.get( block=False )
            except:
                time.sleep(0.01)
                continue

            if type( qitem ) == dict:
                # this is queue item from log stream
                print(qitem['msg'])
            elif type( qitem ) == list:
                # this is test results
                print('\n*******************************************************')
                print('* TEST RESULTS')
                print('*******************************************************')

                for index, result in enumerate( qitem ):
                    logResult = ''

                    if result == 0:
                        logResult = 'PASSED'
                    else:
                        logResult = 'FAILED'

                    print('SCRIPT: ' + str(dtsParam.script[index]) + ' = ' + logResult)
                finished = True
            elif type( qitem ) == str:
                # this is script info
                print(qitem)

            DTS_consoleQueue.task_done( )

    DTS_quit()
else:
    # Init the DTS_Param class
    dtsParam = dtsparam.DTS_Param(['config/dts.xml'], [], [])

    dtsLog = dtsparam.initLogger(dtsParam, DTS_StreamHandler(), False)
