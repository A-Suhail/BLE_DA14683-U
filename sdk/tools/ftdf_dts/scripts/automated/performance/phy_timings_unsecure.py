import sys, datetime, time, math
from scriptIncludes import *
from pipes import stepkinds
from gi.overrides.keysyms import lowleftcorner

msgSET_TxPower = { 'msgId': ftdf.FTDF_SET_REQUEST,
                 'PIBAttribute': ftdf.FTDF_PIB_TX_POWER,
                 'PIBAttributeValue': 0 }

nrOfFrames = 10000

# Original FPGA values
# FTDF_PHYTXSTARTUP_HIGH = 99
# FTDF_PHYTXLATENCY_HIGH = 40
# FTDF_PHYTXFINISH_HIGH  = 19
# FTDF_PHYTRXWAIT_HIGH   = 16
# FTDF_PHYRXSTARTUP_HIGH = 50
# FTDF_PHYRXLATENCY_HIGH = 200
# FTDF_PHYENABLE_HIGH    = 0

# New Recommended values  
FTDF_PHYTXSTARTUP_HIGH = 76
FTDF_PHYTXLATENCY_HIGH = 1
FTDF_PHYTXFINISH_HIGH  = 0
FTDF_PHYTRXWAIT_HIGH   = 15
FTDF_PHYRXSTARTUP_HIGH = 0
FTDF_PHYRXLATENCY_HIGH = 0
FTDF_PHYENABLE_HIGH    = 0

FTDF_PHYTXSTARTUP_LOW = FTDF_PHYTXSTARTUP_HIGH
FTDF_PHYTXLATENCY_LOW = FTDF_PHYTXLATENCY_HIGH
FTDF_PHYTXFINISH_LOW  = FTDF_PHYTXFINISH_HIGH
FTDF_PHYTRXWAIT_LOW   = FTDF_PHYTRXWAIT_HIGH
FTDF_PHYRXSTARTUP_LOW = FTDF_PHYRXSTARTUP_HIGH
FTDF_PHYRXLATENCY_LOW = FTDF_PHYRXLATENCY_HIGH
FTDF_PHYENABLE_LOW    = FTDF_PHYENABLE_HIGH

# FTDF_PHYTXSTARTUP_LOW = 0
# FTDF_PHYTXLATENCY_LOW = 0
# FTDF_PHYTXFINISH_LOW  = 0
# FTDF_PHYTRXWAIT_LOW   = 0
# FTDF_PHYRXSTARTUP_LOW = 0
# FTDF_PHYRXLATENCY_LOW = 0
# FTDF_PHYENABLE_LOW    = 0

FTDF_PHYTXSTARTUP_STEP = 16
FTDF_PHYTXLATENCY_STEP = 16
FTDF_PHYTXFINISH_STEP  = 16
FTDF_PHYTRXWAIT_STEP   = 16
FTDF_PHYRXSTARTUP_STEP = 16
FTDF_PHYRXLATENCY_STEP = 16
FTDF_PHYENABLE_STEP    = 16

FTDF_PHYENABLE    = FTDF_PHYENABLE_HIGH
while (1):
    FTDF_PHYRXLATENCY = FTDF_PHYRXLATENCY_HIGH
    while(1):
        FTDF_PHYRXSTARTUP = FTDF_PHYRXSTARTUP_HIGH
        while(1):
            FTDF_PHYTRXWAIT   = FTDF_PHYTRXWAIT_HIGH
            while(1):
                FTDF_PHYTXFINISH  = FTDF_PHYTXFINISH_HIGH
                while(1):
                    FTDF_PHYTXLATENCY = FTDF_PHYTXLATENCY_HIGH
                    while(1):
                        FTDF_PHYTXSTARTUP = FTDF_PHYTXSTARTUP_HIGH
                        while(1): 
                            msgSET_rxOnWhenIdle = { 'msgId': ftdf.FTDF_SET_REQUEST,
                                                    'PIBAttribute': ftdf.FTDF_PIB_RX_ON_WHEN_IDLE,
                                                    'PIBAttributeValue': True }
                            # Message order
                            msgFlow = ( devId1, msgRESET, ftdf.FTDF_RESET_CONFIRM,
                                        devId2, msgRESET, ftdf.FTDF_RESET_CONFIRM,
                            
                                        devId1, msgSET_TxPower, ftdf.FTDF_SET_CONFIRM,
                                        devId2, msgSET_TxPower, ftdf.FTDF_SET_CONFIRM,
                                        
                                        devId1, msgSET_Dev1_ShortAddress, ftdf.FTDF_SET_CONFIRM,
                                        devId2, msgSET_Dev2_ShortAddress, ftdf.FTDF_SET_CONFIRM,
                            
                                        devId1, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
                                        devId2, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
                            
                                        devId2, msgSET_rxOnWhenIdle, ftdf.FTDF_SET_CONFIRM )
                            
                            idx = 0
                            while( idx < len( msgFlow ) ):
                              # Send message
                              DTS_sndMsg( msgFlow[idx], msgFlow[idx+1] )
                            
                              # Get message confirm
                              res, ret = DTS_getMsg( msgFlow[idx],responseTimeout )
                            
                              # Check received expected confirm
                              if( res == False ):
                                raise StopScript( 'SCRIPT: ERROR: No response received from device' )
                              elif ret['msgId'] != msgFlow[idx+2]:
                                logstr = ( 'SCRIPT: ERROR: Expected ', msgFlow[idx+2], ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
                                raise StopScript( ''.join( map( str, logstr ) ) )
                            
                              idx += 3
                            
                            phy_parameters_reg_2 = 0x40090188
                            phy_parameters_reg_3 = 0x4009018c
                            
                            phy_parameters_reg_2_val = ( FTDF_PHYTXSTARTUP | ( FTDF_PHYTXLATENCY << 8 ) | 
                                    ( FTDF_PHYTXFINISH << 16 ) | ( FTDF_PHYTRXWAIT << 24 ) )
                            
                            phy_parameters_reg_3_val = ( FTDF_PHYRXSTARTUP | ( FTDF_PHYRXLATENCY << 8 ) | 
                                    ( FTDF_PHYENABLE << 16 ) )
                            
                            DTS_setRegister(devId1, phy_parameters_reg_2, 4, phy_parameters_reg_2_val)
                            DTS_setRegister(devId1, phy_parameters_reg_3, 4, phy_parameters_reg_3_val)
                            
                            DTS_setRegister(devId2, phy_parameters_reg_2, 4, phy_parameters_reg_2_val)
                            DTS_setRegister(devId2, phy_parameters_reg_3, 4, phy_parameters_reg_3_val)                            
                            logmsg = ''
                            
                            testout = ( str(FTDF_PHYTXSTARTUP) + '\t' +
                                                str(FTDF_PHYTXLATENCY) + '\t' +
                                                str(FTDF_PHYTXFINISH) + '\t' +
                                                str(FTDF_PHYTRXWAIT) + '\t' +
                                                str(FTDF_PHYRXSTARTUP) + '\t' +
                                                str(FTDF_PHYRXLATENCY) + '\t' +
                                                str(FTDF_PHYENABLE) + '\t' )
                            # logmsg = 'Normal unsecure performance (acknowledged):\n'
                            # ####################################
                            # # 11 + 16
                            # ####################################
                            # logmsg = logmsg + 'Frame size 11 + 16 : \n'
                            #   
                            # msdu = []
                            # for i in range( 16 ):
                            #     msdu.append( i )
                            #   
                            # msgDATA = {
                            #     'msgId': ftdf.FTDF_DATA_REQUEST,
                            #     'srcAddrMode': ftdf.FTDF_SHORT_ADDRESS,
                            #     'dstAddrMode': ftdf.FTDF_SHORT_ADDRESS,
                            #     'dstPANId': 0x0001,
                            #     'dstAddr': 0x0020,
                            #     'msduLength': len( msdu ),
                            #     'msdu': msdu,
                            #     'msduHandle': 1,
                            #     'ackTX': True,
                            #     'GTSTX': False,
                            #     'indirectTX': False,
                            #     'securityLevel': 0,
                            #     'keyIdMode': 0,
                            #     'keySource': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
                            #     'keyIndex': 0,
                            #     'frameControlOptions': 0,
                            #     'headerIEList': 0,
                            #     'payloadIEList': 0,
                            #     'sendMultiPurpose': False
                            # }
                            #   
                            # DTS_setQueueParameters( devId1,
                            #                        ftdf.DTS_QUEUE_SND,
                            #                        ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                            #                        nrOfFrames - 1 )
                            #   
                            # DTS_setQueueParameters( devId2,
                            #                        ftdf.DTS_QUEUE_RCV,
                            #                        ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                            #                        0 )
                            #   
                            # DTS_sndMsg( devId1, msgDATA )
                            #   
                            # # Get current time
                            # t1 = datetime.datetime.now( )
                            #   
                            # # start sending of frames
                            # DTS_setQueueEnable( devId1, True )
                            #   
                            # res, ret = DTS_getMsg( devId1, 100 )
                            #   
                            # if res == False:
                            #     raise StopScript( 'No response from device' )
                            # elif ret['msgTotal'] != nrOfFrames:
                            #     raise StopScript( 'Expected ' + str(nrOfFrames) + ' sent messages' )
                            # elif ret['msgSuccess'] != nrOfFrames:
                            #     raise StopScript( 'Expected ' + str(nrOfFrames) + ' successful messages' )
                            #   
                            #   
                            # # get time after end of test
                            # t2 = datetime.datetime.now( )
                            # deltat = t2 - t1
                            # fps = nrOfFrames / deltat.total_seconds()
                            #   
                            # #logmsg = logmsg + str(nrOfFrames) + ' frames in ' + str( deltat.total_seconds() ) +\
                            # #         ' seconds (' + str(int(fps)) + ' frames per second)\n'
                            # logmsg = logmsg + 'Tx: ' + str(ret['msgTotal']) + ' total ' + str(ret['msgSuccess']) +\
                            #         ' succeeded in ' + str( deltat.total_seconds() ) +\
                            #         ' seconds (' + str(int(fps)) + ' frames per second)\n'
                            #  
                            # testout = testout + str(ret['msgTotal']) + '\t' + str(ret['msgSuccess']) 
                            # time.sleep(2)
                            #   
                            # DTS_setQueueParameters( devId2,
                            #                        ftdf.DTS_QUEUE_DIS,
                            #                        ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                            #                        0 )
                            #   
                            # res, ret = DTS_getMsg( devId2, responseTimeout )
                            #   
                            # if res == False:
                            #     raise StopScript( 'No response from device' )
                            # elif ret['msgTotal'] != nrOfFrames:
                            #     dtsLog.warning( 'Expected ' + str(nrOfFrames) + ' rcvd messages' )
                            # elif ret['msgSuccess'] != nrOfFrames:
                            #     dtsLog.warning( 'Expected ' + str(nrOfFrames) + ' successful messages' )
                            #   
                            # logmsg = logmsg + 'Rx: ' + str(ret['msgTotal']) + ' total ' + str(ret['msgSuccess']) +\
                            #         ' succeeded in ' + str( deltat.total_seconds() ) +\
                            #         ' seconds (' + str(int(fps)) + ' frames per second)\n'
                            # testout = testout + '\t' + str(ret['msgTotal']) + '\t' + str(ret['msgSuccess']) + '\t' +\
                            #         str( deltat.total_seconds() ) + '\t'
                            #   
                            # ####################################
                            # # 11 + 64
                            # ####################################
                            # logmsg = logmsg + 'Frame size 11 + 64 : \n'
                            #   
                            # msdu = []
                            # for i in range( 64 ):
                            #     msdu.append( i )
                            #   
                            # msgDATA = {
                            #     'msgId': ftdf.FTDF_DATA_REQUEST,
                            #     'srcAddrMode': ftdf.FTDF_SHORT_ADDRESS,
                            #     'dstAddrMode': ftdf.FTDF_SHORT_ADDRESS,
                            #     'dstPANId': 0x0001,
                            #     'dstAddr': 0x0020,
                            #     'msduLength': len( msdu ),
                            #     'msdu': msdu,
                            #     'msduHandle': 1,
                            #     'ackTX': True,
                            #     'GTSTX': False,
                            #     'indirectTX': False,
                            #     'securityLevel': 0,
                            #     'keyIdMode': 0,
                            #     'keySource': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
                            #     'keyIndex': 0,
                            #     'frameControlOptions': 0,
                            #     'headerIEList': 0,
                            #     'payloadIEList': 0,
                            #     'sendMultiPurpose': False
                            # }
                            #   
                            # DTS_setQueueParameters( devId1,
                            #                        ftdf.DTS_QUEUE_SND,
                            #                        ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                            #                        nrOfFrames - 1 )
                            #   
                            # DTS_setQueueParameters( devId2,
                            #                        ftdf.DTS_QUEUE_RCV,
                            #                        ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                            #                        0 )
                            #   
                            # DTS_sndMsg( devId1, msgDATA )
                            #   
                            # # Get current time
                            # t1 = datetime.datetime.now( )
                            #   
                            # # start sending of 1000 frames
                            # DTS_setQueueEnable( devId1, True )
                            #   
                            # res, ret = DTS_getMsg( devId1, 100 )
                            #   
                            # if res == False:
                            #     raise StopScript( 'No response from device' )
                            # elif ret['msgTotal'] != nrOfFrames:
                            #     raise StopScript( 'Expected ' + str(nrOfFrames) + ' sent messages' )
                            # elif ret['msgSuccess'] != nrOfFrames:
                            #     raise StopScript( 'Expected ' + str(nrOfFrames) + ' successful messages' )
                            #   
                            #   
                            # # get time after end of test
                            # t2 = datetime.datetime.now( )
                            # deltat = t2 - t1
                            # fps = nrOfFrames / deltat.total_seconds()
                            #   
                            # logmsg = logmsg + 'Tx: ' + str(ret['msgTotal']) + ' total ' + str(ret['msgSuccess']) +\
                            #         ' succeeded in ' + str( deltat.total_seconds() ) +\
                            #         ' seconds (' + str(int(fps)) + ' frames per second)\n'
                            # testout = testout + str(ret['msgTotal']) + '\t' + str(ret['msgSuccess']) 
                            # time.sleep(2)
                            #   
                            # DTS_setQueueParameters( devId2,
                            #                        ftdf.DTS_QUEUE_DIS,
                            #                        ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                            #                        0 )
                            #   
                            # res, ret = DTS_getMsg( devId2, responseTimeout )
                            #   
                            # if res == False:
                            #     raise StopScript( 'No response from device' )
                            # elif ret['msgTotal'] != nrOfFrames:
                            #     dtsLog.warning( 'Expected ' + str(nrOfFrames) + ' rcvd messages' )
                            # elif ret['msgSuccess'] != nrOfFrames:
                            #     dtsLog.warning( 'Expected ' + str(nrOfFrames) + ' successful messages' )
                            #   
                            # logmsg = logmsg + 'Rx: ' + str(ret['msgTotal']) + ' total ' + str(ret['msgSuccess']) +\
                            #         ' succeeded in ' + str( deltat.total_seconds() ) +\
                            #         ' seconds (' + str(int(fps)) + ' frames per second)\n'
                            # testout = testout + '\t' + str(ret['msgTotal']) + '\t' + str(ret['msgSuccess']) + '\t' +\
                            #         str( deltat.total_seconds() ) + '\t'
                            # ####################################
                            # # 11 + 116
                            # ####################################
                            # logmsg = logmsg + 'Frame size 11 + 116: \n'
                            #   
                            # msdu = []
                            # for i in range( 116 ):
                            #     msdu.append( i )
                            #   
                            # msgDATA = {
                            #     'msgId': ftdf.FTDF_DATA_REQUEST,
                            #     'srcAddrMode': ftdf.FTDF_SHORT_ADDRESS,
                            #     'dstAddrMode': ftdf.FTDF_SHORT_ADDRESS,
                            #     'dstPANId': 0x0001,
                            #     'dstAddr': 0x0020,
                            #     'msduLength': len( msdu ),
                            #     'msdu': msdu,
                            #     'msduHandle': 1,
                            #     'ackTX': True,
                            #     'GTSTX': False,
                            #     'indirectTX': False,
                            #     'securityLevel': 0,
                            #     'keyIdMode': 0,
                            #     'keySource': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
                            #     'keyIndex': 0,
                            #     'frameControlOptions': 0,
                            #     'headerIEList': 0,
                            #     'payloadIEList': 0,
                            #     'sendMultiPurpose': False
                            # }
                            #   
                            # DTS_setQueueParameters( devId1,
                            #                        ftdf.DTS_QUEUE_SND,
                            #                        ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                            #                        nrOfFrames - 1 )
                            #   
                            # DTS_setQueueParameters( devId2,
                            #                        ftdf.DTS_QUEUE_RCV,
                            #                        ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                            #                        0 )
                            #   
                            # DTS_sndMsg( devId1, msgDATA )
                            #   
                            # # Get current time
                            # t1 = datetime.datetime.now( )
                            #   
                            # # start sending of 1000 frames
                            # DTS_setQueueEnable( devId1, True )
                            #   
                            # res, ret = DTS_getMsg( devId1, 100 )
                            #   
                            # if res == False:
                            #     raise StopScript( 'No response from device' )
                            # elif ret['msgTotal'] != nrOfFrames:
                            #     raise StopScript( 'Expected ' + str(nrOfFrames) + ' sent messages' )
                            # elif ret['msgSuccess'] != nrOfFrames:
                            #     raise StopScript( 'Expected ' + str(nrOfFrames) + ' successful messages' )
                            #   
                            #   
                            # # get time after end of test
                            # t2 = datetime.datetime.now( )
                            # deltat = t2 - t1
                            # fps = nrOfFrames / deltat.total_seconds()
                            #   
                            # logmsg = logmsg + 'Tx: ' + str(ret['msgTotal']) + ' total ' + str(ret['msgSuccess']) +\
                            #         ' succeeded in ' + str( deltat.total_seconds() ) +\
                            #         ' seconds (' + str(int(fps)) + ' frames per second)\n'
                            #  
                            # testout = testout + str(ret['msgTotal']) + '\t' + str(ret['msgSuccess']) 
                            # time.sleep(2)
                            #   
                            # DTS_setQueueParameters( devId2,
                            #                        ftdf.DTS_QUEUE_DIS,
                            #                        ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                            #                        0 )
                            #   
                            # res, ret = DTS_getMsg( devId2, responseTimeout )
                            #   
                            # if res == False:
                            #     raise StopScript( 'No response from device' )
                            # elif ret['msgTotal'] != nrOfFrames:
                            #     dtsLog.warning( 'Expected ' + str(nrOfFrames) + ' rcvd messages' )
                            # elif ret['msgSuccess'] != nrOfFrames:
                            #     dtsLog.warning( 'Expected ' + str(nrOfFrames) + ' successful messages' )
                            #   
                            # logmsg = logmsg + 'Rx: ' + str(ret['msgTotal']) + ' total ' + str(ret['msgSuccess']) +\
                            #         ' succeeded in ' + str( deltat.total_seconds() ) +\
                            #         ' seconds (' + str(int(fps)) + ' frames per second)\n'
                            #  
                            # testout = testout + '\t' + str(ret['msgTotal']) + '\t' + str(ret['msgSuccess']) + '\t' +\
                            #         str( deltat.total_seconds() ) + '\t'
                            logmsg = logmsg + '\nNormal unsecure performance (unacknowledged):\n'
                            ####################################
                            # 11 + 16
                            ####################################
                            logmsg = logmsg + 'Frame size 11 + 16 : \n'
                             
                            msdu = []
                            for i in range( 16 ):
                                msdu.append( i )
                             
                            msgDATA = {
                                'msgId': ftdf.FTDF_DATA_REQUEST,
                                'srcAddrMode': ftdf.FTDF_SHORT_ADDRESS,
                                'dstAddrMode': ftdf.FTDF_SHORT_ADDRESS,
                                'dstPANId': 0x0001,
                                'dstAddr': 0x0020,
                                'msduLength': len( msdu ),
                                'msdu': msdu,
                                'msduHandle': 1,
                                'ackTX': False,
                                'GTSTX': False,
                                'indirectTX': False,
                                'securityLevel': 0,
                                'keyIdMode': 0,
                                'keySource': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
                                'keyIndex': 0,
                                'frameControlOptions': 0,
                                'headerIEList': 0,
                                'payloadIEList': 0,
                                'sendMultiPurpose': False
                            }
                             
                            DTS_setQueueParameters( devId1,
                                                   ftdf.DTS_QUEUE_SND,
                                                   ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                                                   nrOfFrames - 1, 0 )
                             
                            DTS_setQueueParameters( devId2,
                                                   ftdf.DTS_QUEUE_RCV,
                                                   ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                                                   0, 0 )
                             
                            DTS_sndMsg( devId1, msgDATA )
                             
                            # Get current time
                            t1 = datetime.datetime.now( )
                             
                            # start sending of frames
                            DTS_setQueueEnable( devId1, True )
                             
                            res, ret = DTS_getMsg( devId1, 100 )
                             
                            if res == False:
                                raise StopScript( 'No response from device' )
                        #     elif ret['msgTotal'] != nrOfFrames:
                        #         raise StopScript( 'Expected ' + str(nrOfFrames) + ' sent messages' )
                        #     elif ret['msgSuccess'] != nrOfFrames:
                        #         raise StopScript( 'Expected ' + str(nrOfFrames) + ' successful messages' )
                             
                             
                            # get time after end of test
                            t2 = datetime.datetime.now( )
                            deltat = t2 - t1
                            fps = nrOfFrames / deltat.total_seconds()
                             
                            logmsg = logmsg + 'Tx: ' + str(ret['msgTotal']) + ' total ' + str(ret['msgSuccess']) +\
                                    ' succeeded in ' + str( deltat.total_seconds() ) +\
                                    ' seconds (' + str(int(fps)) + ' frames per second)\n'
                             
                        #     testout = testout + str(ret['msgTotal']) + '\t' + str(ret['msgSuccess'])
                            tx_total_27 = ret['msgTotal']
                            tx_success_27 = ret['msgSuccess']
                            time.sleep(2)
                             
                            DTS_setQueueParameters( devId2,
                                                   ftdf.DTS_QUEUE_DIS,
                                                   ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                                                   0, 0 )
                             
                            res, ret = DTS_getMsg( devId2, responseTimeout )
                             
                            if res == False:
                                raise StopScript( 'No response from device' )
                            elif ret['msgTotal'] != nrOfFrames:
                                dtsLog.warning( 'Expected ' + str(nrOfFrames) + ' rcvd messages' )
                            elif ret['msgSuccess'] != nrOfFrames:
                                dtsLog.warning( 'Expected ' + str(nrOfFrames) + ' successful messages' )
                             
                            logmsg = logmsg + 'Rx: ' + str(ret['msgTotal']) + ' total ' + str(ret['msgSuccess']) +\
                                    ' succeeded in ' + str( deltat.total_seconds() ) +\
                                    ' seconds (' + str(int(fps)) + ' frames per second)\n'
                        #     testout = testout + '\t' + str(ret['msgTotal']) + '\t' + str(ret['msgSuccess']) + '\t' +\
                        #             str( deltat.total_seconds() ) + '\t'
                            rx_total_27 = ret['msgTotal']
                            rx_success_27 = ret['msgSuccess']
                            time_27 = deltat.total_seconds()
                            ####################################
                            # 11 + 64
                            ####################################
                            logmsg = logmsg + 'Frame size 11 + 64 : \n'
                             
                            msdu = []
                            for i in range( 64 ):
                                msdu.append( i )
                             
                            msgDATA = {
                                'msgId': ftdf.FTDF_DATA_REQUEST,
                                'srcAddrMode': ftdf.FTDF_SHORT_ADDRESS,
                                'dstAddrMode': ftdf.FTDF_SHORT_ADDRESS,
                                'dstPANId': 0x0001,
                                'dstAddr': 0x0020,
                                'msduLength': len( msdu ),
                                'msdu': msdu,
                                'msduHandle': 1,
                                'ackTX': False,
                                'GTSTX': False,
                                'indirectTX': False,
                                'securityLevel': 0,
                                'keyIdMode': 0,
                                'keySource': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
                                'keyIndex': 0,
                                'frameControlOptions': 0,
                                'headerIEList': 0,
                                'payloadIEList': 0,
                                'sendMultiPurpose': False
                            }
                             
                            DTS_setQueueParameters( devId1,
                                                   ftdf.DTS_QUEUE_SND,
                                                   ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                                                   nrOfFrames - 1, 0 )
                             
                            DTS_setQueueParameters( devId2,
                                                   ftdf.DTS_QUEUE_RCV,
                                                   ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                                                   0, 0 )
                             
                            DTS_sndMsg( devId1, msgDATA )
                             
                            # Get current time
                            t1 = datetime.datetime.now( )
                             
                            # start sending of 1000 frames
                            DTS_setQueueEnable( devId1, True )
                             
                            res, ret = DTS_getMsg( devId1, 100 )
                             
                            if res == False:
                                raise StopScript( 'No response from device' )
                        #     elif ret['msgTotal'] != nrOfFrames:
                        #         raise StopScript( 'Expected ' + str(nrOfFrames) + ' sent messages' )
                        #     elif ret['msgSuccess'] != nrOfFrames:
                        #         raise StopScript( 'Expected ' + str(nrOfFrames) + ' successful messages' )
                             
                             
                            # get time after end of test
                            t2 = datetime.datetime.now( )
                            deltat = t2 - t1
                            fps = nrOfFrames / deltat.total_seconds()
                             
                            logmsg = logmsg + 'Tx: ' + str(ret['msgTotal']) + ' total ' + str(ret['msgSuccess']) +\
                                    ' succeeded in ' + str( deltat.total_seconds() ) +\
                                    ' seconds (' + str(int(fps)) + ' frames per second)\n'
                        #     testout = testout + str(ret['msgTotal']) + '\t' + str(ret['msgSuccess']) 
                            tx_total_75 = ret['msgTotal']
                            tx_success_75 = ret['msgSuccess']
                            time.sleep(2)
                             
                            DTS_setQueueParameters( devId2,
                                                   ftdf.DTS_QUEUE_DIS,
                                                   ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                                                   0, 0 )
                             
                            res, ret = DTS_getMsg( devId2, responseTimeout )
                             
                            if res == False:
                                raise StopScript( 'No response from device' )
                            elif ret['msgTotal'] != nrOfFrames:
                                dtsLog.warning( 'Expected ' + str(nrOfFrames) + ' rcvd messages' )
                            elif ret['msgSuccess'] != nrOfFrames:
                                dtsLog.warning( 'Expected ' + str(nrOfFrames) + ' successful messages' )
                             
                            logmsg = logmsg + 'Rx: ' + str(ret['msgTotal']) + ' total ' + str(ret['msgSuccess']) +\
                                    ' succeeded in ' + str( deltat.total_seconds() ) +\
                                    ' seconds (' + str(int(fps)) + ' frames per second)\n'
                        #     testout = testout + '\t' + str(ret['msgTotal']) + '\t' + str(ret['msgSuccess']) + '\t' +\
                        #             str( deltat.total_seconds() ) + '\t'
                            rx_total_75 = ret['msgTotal']
                            rx_success_75 = ret['msgSuccess']
                            time_75 = deltat.total_seconds()
                            ####################################
                            # 11 + 116
                            ####################################
                            logmsg = logmsg + 'Frame size 11 + 116: \n'
                             
                            msdu = []
                            for i in range( 116 ):
                                msdu.append( i )
                             
                            msgDATA = {
                                'msgId': ftdf.FTDF_DATA_REQUEST,
                                'srcAddrMode': ftdf.FTDF_SHORT_ADDRESS,
                                'dstAddrMode': ftdf.FTDF_SHORT_ADDRESS,
                                'dstPANId': 0x0001,
                                'dstAddr': 0x0020,
                                'msduLength': len( msdu ),
                                'msdu': msdu,
                                'msduHandle': 1,
                                'ackTX': False,
                                'GTSTX': False,
                                'indirectTX': False,
                                'securityLevel': 0,
                                'keyIdMode': 0,
                                'keySource': [0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0],
                                'keyIndex': 0,
                                'frameControlOptions': 0,
                                'headerIEList': 0,
                                'payloadIEList': 0,
                                'sendMultiPurpose': False
                            }
                             
                            DTS_setQueueParameters( devId1,
                                                   ftdf.DTS_QUEUE_SND,
                                                   ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                                                   nrOfFrames - 1, 0 )
                             
                            DTS_setQueueParameters( devId2,
                                                   ftdf.DTS_QUEUE_RCV,
                                                   ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                                                   0, 0 )
                             
                            DTS_sndMsg( devId1, msgDATA )
                             
                            # Get current time
                            t1 = datetime.datetime.now( )
                             
                            # start sending of 1000 frames
                            DTS_setQueueEnable( devId1, True )
                             
                            res, ret = DTS_getMsg( devId1, 100 )
                             
                            if res == False:
                                raise StopScript( 'No response from device' )
                        #     elif ret['msgTotal'] != nrOfFrames:
                        #         raise StopScript( 'Expected ' + str(nrOfFrames) + ' sent messages' )
                        #     elif ret['msgSuccess'] != nrOfFrames:
                        #         raise StopScript( 'Expected ' + str(nrOfFrames) + ' successful messages' )
                             
                             
                            # get time after end of test
                            t2 = datetime.datetime.now( )
                            deltat = t2 - t1
                            fps = nrOfFrames / deltat.total_seconds()
                             
                            logmsg = logmsg + 'Tx: ' + str(ret['msgTotal']) + ' total ' + str(ret['msgSuccess']) +\
                                    ' succeeded in ' + str( deltat.total_seconds() ) +\
                                    ' seconds (' + str(int(fps)) + ' frames per second)\n'
                        #    testout = testout + str(ret['msgTotal']) + '\t' + str(ret['msgSuccess'])
                            tx_total_127 = ret['msgTotal']
                            tx_success_127 = ret['msgSuccess'] 
                            time.sleep(2)
                             
                            DTS_setQueueParameters( devId2,
                                                   ftdf.DTS_QUEUE_DIS,
                                                   ftdf.DTS_QUEUE_MODE_NO_OVERFLOW,
                                                   0, 0 )
                             
                            res, ret = DTS_getMsg( devId2, responseTimeout )
                             
                            if res == False:
                                raise StopScript( 'No response from device' )
                            elif ret['msgTotal'] != nrOfFrames:
                                dtsLog.warning( 'Expected ' + str(nrOfFrames) + ' rcvd messages' )
                            elif ret['msgSuccess'] != nrOfFrames:
                                dtsLog.warning( 'Expected ' + str(nrOfFrames) + ' successful messages' )
                             
                            logmsg = logmsg + 'Rx: ' + str(ret['msgTotal']) + ' total ' + str(ret['msgSuccess']) +\
                                    ' succeeded in ' + str( deltat.total_seconds() ) +\
                                    ' seconds (' + str(int(fps)) + ' frames per second)\n'
                        #     testout = testout + '\t' + str(ret['msgTotal']) + '\t' + str(ret['msgSuccess']) + '\t' +\
                        #             str( deltat.total_seconds() ) + '\t'
                            rx_total_127 = ret['msgTotal']
                            rx_success_127 = ret['msgSuccess']
                            time_127 = deltat.total_seconds()
                            
                            fps_27 = tx_total_27 / time_27
                            fps_75 = tx_total_75 / time_75
                            fps_127 = tx_total_127 / time_127
                            per_total = ( 1 - (rx_success_27 + rx_success_75 + rx_success_127) / 
                                          (tx_total_27 + tx_total_75 + tx_total_127) )
                            testout = ( testout + 
                                        str(tx_total_27) + '\t' + str(tx_success_27) + '\t' + 
                                        str(rx_total_27) + '\t' + str(rx_success_27) + '\t' + str(time_27) + '\t' + 
                                        str(tx_total_75) + '\t' + str(tx_success_75) + '\t' + 
                                        str(rx_total_75) + '\t' + str(rx_success_75) + '\t' + str(time_75) + '\t' +
                                        str(tx_total_127) + '\t' + str(tx_success_127) + '\t' + 
                                        str(rx_total_127) + '\t' + str(rx_success_127) + '\t' + str(time_127) + '\t' +
                                        str(fps_27) + '\t' + str(fps_75) + '\t' + str(fps_127) + '\t' + str(per_total) + 
                                        '\n'
                                        )
                            text_file = open("log/phy_timings.csv", "a")
                            text_file.write("%s" % testout)
                            text_file.close()
                            logmsg = logmsg # + testout
                            
                            ################################################################################################
                            # Add repetition logic here
                            ################################################################################################
#                             FTDF_PHYTXSTARTUP = FTDF_PHYTXSTARTUP_HIGH
#                             FTDF_PHYTXLATENCY = FTDF_PHYTXLATENCY_HIGH
#                             FTDF_PHYTXFINISH  = FTDF_PHYTXFINISH_HIGH
#                             FTDF_PHYTRXWAIT   = FTDF_PHYTRXWAIT_HIGH
#                             FTDF_PHYRXSTARTUP = FTDF_PHYRXSTARTUP_HIGH
#                             FTDF_PHYRXLATENCY = FTDF_PHYRXLATENCY_HIGH
#                             FTDF_PHYENABLE    = FTDF_PHYENABLE_HIGH  
                            if (FTDF_PHYTXSTARTUP == FTDF_PHYTXSTARTUP_LOW):
                                break
                            FTDF_PHYTXSTARTUP = FTDF_PHYTXSTARTUP - FTDF_PHYTXSTARTUP_STEP
                            if (FTDF_PHYTXSTARTUP < FTDF_PHYTXSTARTUP_LOW):
                                FTDF_PHYTXSTARTUP = FTDF_PHYTXSTARTUP_LOW
                            
                        if (FTDF_PHYTXLATENCY == FTDF_PHYTXLATENCY_LOW):
                            break
                        FTDF_PHYTXLATENCY = FTDF_PHYTXLATENCY - FTDF_PHYTXLATENCY_STEP
                        if (FTDF_PHYTXLATENCY < FTDF_PHYTXLATENCY_LOW):
                            FTDF_PHYTXLATENCY = FTDF_PHYTXLATENCY_LOW
                        
                    if (FTDF_PHYTXFINISH == FTDF_PHYTXFINISH_LOW):
                        break
                    FTDF_PHYTXFINISH = FTDF_PHYTXFINISH - FTDF_PHYTXFINISH_STEP
                    if (FTDF_PHYTXFINISH < FTDF_PHYTXFINISH_LOW):
                        FTDF_PHYTXFINISH = FTDF_PHYTXFINISH_LOW

                if (FTDF_PHYTRXWAIT == FTDF_PHYTRXWAIT_LOW):
                    break
                FTDF_PHYTRXWAIT = FTDF_PHYTRXWAIT - FTDF_PHYTRXWAIT_STEP
                if (FTDF_PHYTRXWAIT < FTDF_PHYTRXWAIT_LOW):
                    FTDF_PHYTRXWAIT = FTDF_PHYTRXWAIT_LOW
                    
            if (FTDF_PHYRXSTARTUP == FTDF_PHYRXSTARTUP_LOW):
                break
            FTDF_PHYRXSTARTUP = FTDF_PHYRXSTARTUP - FTDF_PHYRXSTARTUP_STEP
            if (FTDF_PHYRXSTARTUP < FTDF_PHYRXSTARTUP_LOW):
                FTDF_PHYRXSTARTUP = FTDF_PHYRXSTARTUP_LOW 

        if (FTDF_PHYRXLATENCY == FTDF_PHYRXLATENCY_LOW):
            break
        FTDF_PHYRXLATENCY = FTDF_PHYRXLATENCY - FTDF_PHYRXLATENCY_STEP
        if (FTDF_PHYRXLATENCY < FTDF_PHYRXLATENCY_LOW):
            FTDF_PHYRXLATENCY = FTDF_PHYRXLATENCY_LOW

    if (FTDF_PHYENABLE == FTDF_PHYENABLE_LOW):
        break
    FTDF_PHYENABLE = FTDF_PHYENABLE - FTDF_PHYENABLE_STEP
    if (FTDF_PHYENABLE < FTDF_PHYENABLE_LOW):
        FTDF_PHYENABLE = FTDF_PHYENABLE_LOW
# Return performance results via exception
raise PerformanceResults( logmsg )
