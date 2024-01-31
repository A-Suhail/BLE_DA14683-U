# Load-drop 2 Test: TSCH
#

import sys    #cli arguments
import time    #sleep

from scriptIncludes import *


# Slotframes
msg_Slotframe_Add_0 = {
    'msgId': ftdf.FTDF_SET_SLOTFRAME_REQUEST,
    'handle': 0,
    'operation': ftdf.FTDF_ADD,
    'size': 10
}

# Links
linkOptions_Transmit = 0x01
linkOptions_Receive = 0x02
linkOptions_Shared = 0x04
linkOptions_Timekeeping = 0x08
msg_Link_Add_Dev1_Slot5 = {
    'msgId': ftdf.FTDF_SET_LINK_REQUEST,
    'operation': ftdf.FTDF_ADD,
    'linkHandle': 0,
    'slotframeHandle': 0,
    'timeslot': 5,
    'channelOffset': 0,
    'linkOptions': linkOptions_Transmit,
    'linkType': 1,
    'nodeAddress': 0x0020,
}
msg_Link_Add_Dev1_Slot6 = {
    'msgId': ftdf.FTDF_SET_LINK_REQUEST,
    'operation': ftdf.FTDF_ADD,
    'linkHandle': 1,
    'slotframeHandle': 0,
    'timeslot': 6,
    'channelOffset': 0,
    'linkOptions': linkOptions_Receive,
    'linkType': 0,
    'nodeAddress': 0x0020,
}
msg_Link_Add_Dev2_Slot5 = {
    'msgId': ftdf.FTDF_SET_LINK_REQUEST,
    'operation': ftdf.FTDF_ADD,
    'linkHandle': 0,
    'slotframeHandle': 0,
    'timeslot': 5,
    'channelOffset': 0,
    'linkOptions': linkOptions_Receive,
    'linkType': 1,
    'nodeAddress': 0x0010,
}
msg_Link_Add_Dev2_Slot6 = {
    'msgId': ftdf.FTDF_SET_LINK_REQUEST,
    'operation': ftdf.FTDF_ADD,
    'linkHandle': 1,
    'slotframeHandle': 0,
    'timeslot': 6,
    'channelOffset': 0,
    'linkOptions': linkOptions_Transmit,
    'linkType': 0,
    'nodeAddress': 0x0010,
}

ieType_SlotframeAndLink            = 0x1b
ieType_Timeslot                    = 0x1c
ieType_ChannelHoppingSequence     = 0x09
slotframeAndLink                = [0xAB,0xAB,0xAB,0xAB,0xAB,0xAB]
timeslot                        = [0xED,0xED,0xED,0xED,0xED,0xED,0xED,0xED]
channelHoppingSequence            = [0x89,0x89,0x89,0x89,0x89,0x89,0x89,0x89,0x89,0x89,0x89,0x89]
ie2Content                        = [11, 22, 33, 44, 55, 66, 77, 88]
beaconIEList = {
    'nrOfIEs': 2,
    'IEs':
    [
        {
            'ID': 1,
            'length': 0,
            'content':
            {
                'nrOfSubIEs': 3,
                'subIEs':
                [
                    {
                        'type': 0,
                        'subID': ieType_SlotframeAndLink,
                        'length': len( slotframeAndLink ),
                        'subContent': slotframeAndLink
                    },
                    {
                        'type': 0,
                        'subID': ieType_Timeslot,
                        'length': len( timeslot ),
                        'subContent': timeslot
                    },
                    {
                        'type': 1,
                        'subID': ieType_ChannelHoppingSequence,
                        'length': len( channelHoppingSequence ),
                        'subContent': channelHoppingSequence
                    }
                ]
            }
        },
        {
            'ID': 2,
            'length': 8,
            'content': ie2Content
        }
    ]
}
msgSET_BeaconIEList = {
    'msgId': ftdf.FTDF_SET_REQUEST,
    'PIBAttribute': ftdf.FTDF_PIB_EB_IE_LIST,
    'PIBAttributeValue': beaconIEList
}

# Other
msgSET_Auto = {
    'msgId': ftdf.FTDF_SET_REQUEST,
    'PIBAttribute': ftdf.FTDF_PIB_AUTO_REQUEST,
    'PIBAttributeValue': False
}
msgSET_BeaconRespond = {
    'msgId': ftdf.FTDF_SET_REQUEST,
    'PIBAttribute': ftdf.FTDF_PIB_BEACON_AUTO_RESPOND,
    'PIBAttributeValue': True
}
EBSN=0x43
msgSET_EBSN= {
    'msgId': ftdf.FTDF_SET_REQUEST,
    'PIBAttribute': ftdf.FTDF_PIB_EBSN,
    'PIBAttributeValue': EBSN
}

msgSET_ASN = {
    'msgId': ftdf.FTDF_SET_REQUEST,
    'PIBAttribute': ftdf.FTDF_PIB_ASN,
    'PIBAttributeValue': 0
}

msgSTART = {
    'msgId': ftdf.FTDF_START_REQUEST,
    'PANId': 0x0001,
    'channelNumber': 11,
    'channelPage': 0,
    'startTime': 0x000000,
    'beaconOrder': 15,
    'superframeOrder': 0,
    'PANCoordinator': True,
    'batteryLifeExtension':False,
    'coordRealignment': False,
    'coordRealignSecurityLevel': 0,
    'coordRealignKeyIdMode': 0,
    'coordRealignKeySource':[0,0,0,0,0,0,0,0],
    'coordRealignKeyIndex': 0,
    'beaconSecurityLevel': 0,
    'beaconKeyIdMode': 0,
    'beaconKeySource': [0,0,0,0,0,0,0,0],
    'beaconKeyIndex': 0
}

msg_Tsch_Mode_On = {
    'msgId': ftdf.FTDF_TSCH_MODE_REQUEST,
    'tschMode': ftdf.FTDF_TSCH_ON,
    'timeslotStartTime': 0
}

msg_Tsch_Mode_Off = {
    'msgId': ftdf.FTDF_TSCH_MODE_REQUEST,
    'tschMode': ftdf.FTDF_TSCH_OFF,
    'timeslotStartTime': 0
}

scanChannels_00 = 0x00000001
scanChannels_01 = 0x00000002
scanChannels_02 = 0x00000004
scanChannels_03 = 0x00000008
scanChannels_04 = 0x00000010
scanChannels_05 = 0x00000020
scanChannels_06 = 0x00000040
scanChannels_07 = 0x00000080
scanChannels_08 = 0x00000100
scanChannels_09 = 0x00000200
scanChannels_10 = 0x00000400
scanChannels_11 = 0x00000800
scanChannels_12 = 0x00001000
scanChannels_13 = 0x00002000
scanChannels_14 = 0x00004000
scanChannels_15 = 0x00008000
scanChannels_16 = 0x00010000
scanChannels_17 = 0x00020000
scanChannels_18 = 0x00040000
scanChannels_19 = 0x00080000
scanChannels_20 = 0x00100000
scanChannels_21 = 0x00200000
scanChannels_22 = 0x00400000
scanChannels_23 = 0x00800000
scanChannels_24 = 0x01000000
scanChannels_25 = 0x02000000
scanChannels_26 = 0x04000000
scanChannels_27 = 0x08000000
scanChannels_28 = 0x10000000
scanChannels_29 = 0x20000000
scanChannels_30 = 0x40000000
scanChannels_31 = 0x80000000
scanChannels = (
#    scanChannels_00 |
#    scanChannels_01 |
#    scanChannels_02 |
#    scanChannels_03 |
#    scanChannels_04 |
#    scanChannels_05 |
#    scanChannels_06 |
#    scanChannels_07 |
#    scanChannels_08 |
#    scanChannels_09 |
#    scanChannels_10 |
    scanChannels_11 |
    scanChannels_12 |
    scanChannels_13 |
    scanChannels_14 |
    scanChannels_15 |
    scanChannels_16 |
    scanChannels_17 |
    scanChannels_18 |
    scanChannels_19 |
    scanChannels_20 |
    scanChannels_21 |
    scanChannels_22 |
    scanChannels_23 |
    scanChannels_24 |
    scanChannels_25 |
    scanChannels_26
#    scanChannels_27 |
#    scanChannels_28 |
#    scanChannels_29 |
#    scanChannels_30 |
#    scanChannels_31
)
msgScanPassive = {
    'msgId': ftdf.FTDF_SCAN_REQUEST,
    'scanType': ftdf.FTDF_PASSIVE_SCAN,
    'scanChannels': scanChannels,
    'channelPage': 0,
    'scanDuration': 4,
    'securityLevel': 0,
    'keyIdMode': 0,
    'keySource': [0,0,0,0,0,0,0,0],
    'keyIndex': 0
}

msgEnhancedBeacon = {
    'msgId': ftdf.FTDF_BEACON_REQUEST,
    'beaconType': ftdf.FTDF_ENHANCED_BEACON,
    'channel': 11,
    'channelPage': 0,
    'superframeOrder': 0,
    'beaconSecurityLevel': 0,
    'beaconKeyIdMode': 0,
    'beaconKeySource': [0,0,0,0,0,0,0,0],
    'beaconKeyIndex': 0,
    'dstAddrMode': ftdf.FTDF_SHORT_ADDRESS,
    'dstAddr': 0x0020,
    'BSNSuppression': False
}


# Message order
msgFlow = (
    devId1, msgRESET, ftdf.FTDF_RESET_CONFIRM,
    devId2, msgRESET, ftdf.FTDF_RESET_CONFIRM,

    devId1, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
    devId2, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,

    devId1, msgSET_Dev1_ShortAddress, ftdf.FTDF_SET_CONFIRM,
    devId2, msgSET_Dev2_ShortAddress, ftdf.FTDF_SET_CONFIRM,

    devId1, msg_Slotframe_Add_0, ftdf.FTDF_SET_SLOTFRAME_CONFIRM,
    devId2, msg_Slotframe_Add_0, ftdf.FTDF_SET_SLOTFRAME_CONFIRM,

    devId1, msg_Link_Add_Dev1_Slot5, ftdf.FTDF_SET_LINK_CONFIRM,
    devId2, msg_Link_Add_Dev2_Slot5, ftdf.FTDF_SET_LINK_CONFIRM,
    devId1, msg_Link_Add_Dev1_Slot6, ftdf.FTDF_SET_LINK_CONFIRM,
    devId2, msg_Link_Add_Dev2_Slot6, ftdf.FTDF_SET_LINK_CONFIRM,
    
    devId2, msgSET_Auto, ftdf.FTDF_SET_CONFIRM, # To pass received beacon directly to network layer

    devId1, msgSTART, ftdf.FTDF_START_CONFIRM,

    devId1, msg_Tsch_Mode_On, ftdf.FTDF_TSCH_MODE_CONFIRM,

    devId2, msgScanPassive, ftdf.FTDF_SCAN_CONFIRM,
    
    devId1, msgSET_BeaconIEList, ftdf.FTDF_SET_CONFIRM,

    devId1, msgSET_EBSN, ftdf.FTDF_SET_CONFIRM,
    devId1, msgEnhancedBeacon, ftdf.FTDF_BEACON_CONFIRM
)


idx = 0
result = True
while( idx < len( msgFlow ) ):
    # Send message
    DTS_sndMsg( msgFlow[idx], msgFlow[idx+1] )

    if( msgFlow[idx+2] == ftdf.FTDF_SCAN_CONFIRM ):
        idx += 3
        continue

    # Get message confirm
    res, ret = DTS_getMsg( msgFlow[idx], responseTimeout )

    # Check received expected confirm
    if( res == False ):
        raise StopScript( 'SCRIPT: ERROR: No response received from device' )
        result = False
        break
    elif( ret['msgId'] != msgFlow[idx+2] ):
        logstr = ( 'SCRIPT: ERROR: Expected ', msgFlow[idx+2], ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False
        break
    else:
        if( ret['msgId'] == ftdf.FTDF_BEACON_CONFIRM ):
            # Catch beacon on receiving DUT and configure it accordingly
            slotStartTime = 0

            res, ret = DTS_getMsg( devId2, responseTimeout )
            if( res == False ):
                raise StopScript( 'SCRIPT: ERROR: No response received from device' )
                result = False
                break
            elif( ret['msgId'] != ftdf.FTDF_BEACON_NOTIFY_INDICATION ):
                logstr = ( 'SCRIPT: ERROR: Expected BEACON_NOTIFY_INDICATION, instead received ', msgNameStr[ ret['msgId'] -1 ] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break

            # Check received Enh Beacon
            if( ret['beaconType'] != ftdf.FTDF_ENHANCED_BEACON ):
                logstr = ( 'SCRIPT: ERROR: expected beaconType = ENHANCED_BEACON received:', ret['beaconType'] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break
            if( ret['sduLength'] != 0 ):
                logstr = ( 'SCRIPT: ERROR: expected sduLength =0 received:', ret['sduLength'] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break
            if( ret['EBSN'] != EBSN ):
                logstr = ( 'SCRIPT: ERROR: expected EBSN =', EBSN,' received:', ret['EBSN'] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break

            if( ret['IEList']['nrOfIEs'] != 2 ):
                logstr = ( 'SCRIPT: ERROR: expected nrOfIEs = 2 received:', ret['IEList']['nrOfIEs'] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break
            if( ret['IEList']['IEs'][0]['content']['nrOfSubIEs'] != 4 ):
                logstr = ( 'SCRIPT: ERROR: expected nrOfSubIEs = 4 received:', ret['IEList']['IEs'][0]['content']['nrOfSubIEs'] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break

            # IE 2
            if( ret['IEList']['IEs'][1]['content'] != ie2Content ):
                logstr = ( 'SCRIPT: ERROR: expected IE2 content =', ie2Content, ' received:', ret['IEList']['IEs'][1]['content'] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break

            # IE 1 with sub IE's
            if( ret['IEList']['IEs'][0]['content']['subIEs'][1]['subID'] != ieType_SlotframeAndLink ):
                logstr = ( 'SCRIPT: ERROR: expected SubIE 1 subID=', ieType_SlotframeAndLink, 'received:', ret['IEList']['IEs'][0]['content']['subIEs'][1]['subID'] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break
            if( ret['IEList']['IEs'][0]['content']['subIEs'][1]['content'] != slotframeAndLink ):
                logstr = ( 'SCRIPT: ERROR: expected SubIE 1 content=', slotframeAndLink, 'received:', ret['IEList']['IEs'][0]['content']['subIEs'][1]['content'] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break
            if( ret['IEList']['IEs'][0]['content']['subIEs'][1]['type'] != 0 ):
                logstr = ( 'SCRIPT: ERROR: expected type 1 content=', 0, 'received:', ret['IEList']['IEs'][0]['content']['subIEs'][1]['type'] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break

            if( ret['IEList']['IEs'][0]['content']['subIEs'][2]['subID'] != ieType_Timeslot ):
                logstr = ( 'SCRIPT: ERROR: expected SubIE 1 subID=', ieType_Timeslot, 'received:', ret['IEList']['IEs'][0]['content']['subIEs'][2]['subID'] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break
            if( ret['IEList']['IEs'][0]['content']['subIEs'][2]['content'] != timeslot ):
                logstr = ( 'SCRIPT: ERROR: expected SubIE 1 content=', timeslot, 'received:', ret['IEList']['IEs'][0]['content']['subIEs'][2]['content'] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break
            if( ret['IEList']['IEs'][0]['content']['subIEs'][2]['type'] != 0 ):
                logstr = ( 'SCRIPT: ERROR: expected type 1 content=', 0, 'received:', ret['IEList']['IEs'][0]['content']['subIEs'][2]['type'] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break

            if( ret['IEList']['IEs'][0]['content']['subIEs'][3]['subID'] != ieType_ChannelHoppingSequence ):
                logstr = ( 'SCRIPT: ERROR: expected SubIE 1 subID=', ieType_ChannelHoppingSequence, 'received:', ret['IEList']['IEs'][0]['content']['subIEs'][3]['subID'] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break
            if( ret['IEList']['IEs'][0]['content']['subIEs'][3]['content'] != channelHoppingSequence ):
                logstr = ( 'SCRIPT: ERROR: expected SubIE 1 content=', channelHoppingSequence, 'received:', ret['IEList']['IEs'][0]['content']['subIEs'][3]['content'] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break
            if( ret['IEList']['IEs'][0]['content']['subIEs'][3]['type'] != 1 ):
                logstr = ( 'SCRIPT: ERROR: expected type 1 content=', 1, 'received:', ret['IEList']['IEs'][0]['content']['subIEs'][3]['type'] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break

            # Get ASN from beacon
            slotStartTime = ret['timestamp'] - 80
            shift = 0
            ASN = 0
            for n in range(5):
                ASN = ASN + (ret['IEList']['IEs'][0]['content']['subIEs'][0]['content'][n] << shift)
                shift = shift + 8

            # Get scan result
            res, ret = DTS_getMsg( devId2, responseTimeout )
            if( res == False ):
                raise StopScript( 'SCRIPT: ERROR: No response received from device' )
                result = False
                break
            elif( ret['msgId'] != ftdf.FTDF_SCAN_CONFIRM ):
                logstr = ( 'SCRIPT: ERROR: Expected SCAN_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break
            elif( ret['status'] != ftdf.FTDF_SUCCESS ):
                logstr = ( 'SCRIPT: ERROR: Scan result:', resultStr[ ret['status'] ] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break

            # Set ASN on receiving DUT
            msgSET_ASN['PIBAttributeValue'] = ASN
            DTS_sndMsg( devId2, msgSET_ASN )
            res, ret = DTS_getMsg( devId2, responseTimeout )
            if( res == False ):
                raise StopScript( 'SCRIPT: ERROR: No response received from device' )
                result = False
                break
            elif( ret['msgId'] != ftdf.FTDF_SET_CONFIRM  ):
                logstr = ( 'SCRIPT: ERROR: Expected SET_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break
            elif( ret['status'] != ftdf.FTDF_SUCCESS ):
                logstr = ( 'SCRIPT: ERROR: Scan result:', resultStr[ ret['status'] ] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break

            # Enable TCSH on receiving DUT
            msg_Tsch_Mode_On['timeslotStartTime'] = slotStartTime
            DTS_sndMsg( devId2, msg_Tsch_Mode_On )
            res, ret = DTS_getMsg( devId2, responseTimeout )
            if( res == False ):
                raise StopScript( 'SCRIPT: ERROR: No response received from device' )
                result = False
                break
            elif( ret['msgId'] != ftdf.FTDF_TSCH_MODE_CONFIRM  ):
                logstr = ( 'SCRIPT: ERROR: Expected TSCH_MODE_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break
            elif( ret['status'] != ftdf.FTDF_SUCCESS ):
                logstr = ( 'SCRIPT: ERROR: Scan result:', resultStr[ ret['status'] ] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break

        elif( ret['msgId'] == ftdf.FTDF_DATA_CONFIRM ):
            res, ret = DTS_getMsg( devId2, responseTimeout )
            if( res == False ):
                raise StopScript( 'SCRIPT: ERROR: No response received from device' )
                result = False
                break
            elif( ret['msgId'] != ftdf.FTDF_DATA_INDICATION ):
                logstr = ( 'SCRIPT: ERROR: Expected DATA_INDICATION confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break

        elif( ret['msgId'] == ftdf.FTDF_SET_CONFIRM ):
            if( ret['status'] != ftdf.FTDF_SUCCESS ):
                logstr = ( 'SCRIPT: ERROR: devId:', msgFlow[idx], ' request:', msgNameStr[ msgFlow[idx+1]['msgId'] -1 ], 'attribute:', pibAttributeStr[ msgFlow[idx+1]['PIBAttribute'] -1 ], ' result:', resultStr[ ret['status'] ] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break

            # Check set request with get request
            msgGet['PIBAttribute'] = msgFlow[idx+1]['PIBAttribute']

            DTS_sndMsg( msgFlow[idx], msgGet )

            res2, ret2 = DTS_getMsg( msgFlow[idx], responseTimeout )
            if( res2 == False ):
                raise StopScript( 'SCRIPT: ERROR: No response received from device' )
                result = False
                break
            elif ret2['msgId'] != ftdf.FTDF_GET_CONFIRM:
                logstr = ( 'SCRIPT: ERROR: Expected GET_CONFIRM, instead received ', ret2['msgId'] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break
            elif( ret2['status'] != ftdf.FTDF_SUCCESS ):
                logstr = ( 'SCRIPT: devId:', msgFlow[idx], ' request: GET_REQUEST', 'attribute:', pibAttributeStr[ msgFlow[idx+1]['PIBAttribute'] -1 ], ' result:', resultStr[ ret2['status'] ] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break
            elif ret2['PIBAttributeValue'] != msgFlow[idx+1]['PIBAttributeValue']:
                logstr = ( 'SCRIPT: ERROR: Incorrect set PIBAttribute: ', msgGet['PIBAttribute'] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break

        else:
            if( ret['status'] != ftdf.FTDF_SUCCESS ):
                logstr = ( 'SCRIPT: devId:', msgFlow[idx], ' request:', msgNameStr[ msgFlow[idx+1]['msgId'] -1 ], ' result:', resultStr[ ret['status'] ] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break

    idx += 3


if( not result ):
    raise StopScript('SCRIPT: FAILED')
