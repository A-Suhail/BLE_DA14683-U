import sys    #cli arguments
import time    #sleep

from scriptIncludes import *


result = True

# Reset devices
if(result):
    DTS_sndMsg( devId1, msgRESET )
    res, ret = DTS_getMsg( devId1, responseTimeout )
    if( res == False ):
        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: No response received from device' )
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False
    elif( ret['msgId'] != ftdf.FTDF_RESET_CONFIRM ):
        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: Expected RESET_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False
    elif( ret['status'] != ftdf.FTDF_SUCCESS ):
        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: result:', resultStr[ ret['status'] ] )
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False


#------------------------------ # TEST: Slotframe
# TEST: Slotframe: add slotframe, slotframeHandle already in use, delete slotframe
if(result):
    msg_Slotframe_Add = {
        'msgId': ftdf.FTDF_SET_SLOTFRAME_REQUEST,
        'handle': 0,
        'operation': ftdf.FTDF_ADD,
        'size': 20
    }

    DTS_sndMsg( devId1, msg_Slotframe_Add )
    res, ret = DTS_getMsg( devId1, responseTimeout )
    if( res == False ):
        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: No response received from device' )
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False
    elif( ret['msgId'] != ftdf.FTDF_SET_SLOTFRAME_CONFIRM ):
        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: Expected SLOTFRAME_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False
    elif( ret['status'] != ftdf.FTDF_SUCCESS ):
        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: result:', resultStr[ ret['status'] ] )
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False
    else:
        # Check set values
        msgGet['PIBAttribute'] = ftdf.FTDF_PIB_SLOTFRAME_TABLE

        DTS_sndMsg( devId1, msgGet )
        res, ret = DTS_getMsg( devId1, responseTimeout )
        if( res == False ):
            logstr = ( 'SCRIPT (',lineNr(),'): ERROR: No response received from device' )
            raise StopScript( ''.join( map( str, logstr ) ) )
            result = False
        elif( ret['msgId'] != ftdf.FTDF_GET_CONFIRM ):
            logstr = ( 'SCRIPT (',lineNr(),'): ERROR: Expected GET_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
            raise StopScript( ''.join( map( str, logstr ) ) )
            result = False
        elif( ret['status'] != ftdf.FTDF_SUCCESS ):
            logstr = ( 'SCRIPT (',lineNr(),'): ERROR: result:', resultStr[ ret['status'] ] )
            raise StopScript( ''.join( map( str, logstr ) ) )
            result = False
        else:
            if( ret['PIBAttributeValue']['slotframeEntries'][0]['slotframeHandle'] != 0 ):
                logstr = ( 'SCRIPT (',lineNr(),'): ERROR: slotframe: slotframeHandle' )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
            if( ret['PIBAttributeValue']['slotframeEntries'][0]['slotframeSize'] != 20 ):
                logstr = ( 'SCRIPT (',lineNr(),'): ERROR: slotframe: slotframeSize' )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False

            # Set the same slotframe should result in error
            DTS_sndMsg( devId1, msg_Slotframe_Add )
            res, ret = DTS_getMsg( devId1, responseTimeout )
            if( res == False ):
                logstr = ( 'SCRIPT (',lineNr(),'): ERROR: No response received from device' )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
            elif( ret['msgId'] != ftdf.FTDF_SET_SLOTFRAME_CONFIRM ):
                logstr = ( 'SCRIPT (',lineNr(),'): ERROR: Expected GET_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
            elif( ret['status'] != ftdf.FTDF_INVALID_PARAMETER ):
                logstr = ( 'SCRIPT (',lineNr(),'): ERROR: Epexted result:FTDF_INVALID_PARAMETER received result:', resultStr[ ret['status'] ] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False

        # Delete created slotframe
        msg_Slotframe_Delete = {
            'msgId': ftdf.FTDF_SET_SLOTFRAME_REQUEST,
            'handle': 0,
            'operation': ftdf.FTDF_DELETE,
            'size': 20
        }

        DTS_sndMsg( devId1, msg_Slotframe_Delete )
        res, ret = DTS_getMsg( devId1, responseTimeout )
        if( res == False ):
            logstr = ( 'SCRIPT (',lineNr(),'): ERROR: No response received from device' )
            raise StopScript( ''.join( map( str, logstr ) ) )
            result = False
        elif( ret['msgId'] != ftdf.FTDF_SET_SLOTFRAME_CONFIRM ):
            logstr = ( 'SCRIPT (',lineNr(),'): ERROR: Expected SLOTFRAME_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
            raise StopScript( ''.join( map( str, logstr ) ) )
            result = False
        elif( ret['status'] != ftdf.FTDF_SUCCESS ):
            logstr = ( 'SCRIPT (',lineNr(),'): ERROR: result:', resultStr[ ret['status'] ] )
            raise StopScript( ''.join( map( str, logstr ) ) )
            result = False
        else:
            # Check slotframe deleted
            msgGet['PIBAttribute'] = ftdf.FTDF_PIB_SLOTFRAME_TABLE

            DTS_sndMsg( devId1, msgGet )
            res, ret = DTS_getMsg( devId1, responseTimeout )
            if( res == False ):
                logstr = ( 'SCRIPT (',lineNr(),'): ERROR: No response received from device' )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
            elif( ret['msgId'] != ftdf.FTDF_GET_CONFIRM ):
                logstr = ( 'SCRIPT (',lineNr(),'): ERROR: Expected GET_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
            elif( ret['status'] != ftdf.FTDF_SUCCESS ):
                logstr = ( 'SCRIPT (',lineNr(),'): ERROR: result:', resultStr[ ret['status'] ] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
            else:
                if( ret['PIBAttributeValue']['nrOfSlotframes'] != 0 ):
                    logstr = ( 'SCRIPT (',lineNr(),'): ERROR: slotframe: nrOfSlotframes should be 0' )
                    raise StopScript( ''.join( map( str, logstr ) ) )
                    result = False


# TEST: Slotframe: delete non existing slotframes
if(result):
    msg_Slotframe_Delete = {
        'msgId': ftdf.FTDF_SET_SLOTFRAME_REQUEST,
        'handle': 0,
        'operation': ftdf.FTDF_DELETE,
        'size': 20
    }

    DTS_sndMsg( devId1, msg_Slotframe_Delete )
    res, ret = DTS_getMsg( devId1, responseTimeout )
    if( res == False ):
        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: No response received from device' )
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False
    elif( ret['msgId'] != ftdf.FTDF_SET_SLOTFRAME_CONFIRM ):
        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: Expected SLOTFRAME_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False
    elif( ret['status'] != ftdf.FTDF_SLOTFRAME_NOT_FOUND ):
        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: expected result:SLOTFRAME_NOT_FOUND instead received', resultStr[ ret['status'] ] )
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False


# TEST: Slotframe: Max slotframes
if(result):
    idx = 0
    while( idx < ftdf.FTDF_MAX_SLOTFRAMES+1 ):
        msg_Slotframe_Add = {
            'msgId': ftdf.FTDF_SET_SLOTFRAME_REQUEST,
            'handle': 0+idx,
            'operation': ftdf.FTDF_ADD,
            'size': 20
        }

        DTS_sndMsg( devId1, msg_Slotframe_Add )
        res, ret = DTS_getMsg( devId1, responseTimeout )
        if( res == False ):
            logstr = ( 'SCRIPT (',lineNr(),'): ERROR: No response received from device' )
            raise StopScript( ''.join( map( str, logstr ) ) )
            result = False
            break
        elif( ret['msgId'] != ftdf.FTDF_SET_SLOTFRAME_CONFIRM ):
            logstr = ( 'SCRIPT (',lineNr(),'): ERROR: Expected SLOTFRAME_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
            raise StopScript( ''.join( map( str, logstr ) ) )
            result = False
            break
        else:
            if( idx != ftdf.FTDF_MAX_SLOTFRAMES and
                ret['status'] != ftdf.FTDF_SUCCESS ):
                logstr = ( 'SCRIPT (',lineNr(),'): ERROR: result:', resultStr[ ret['status'] ] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break

            if( idx == ftdf.FTDF_MAX_SLOTFRAMES and
                ret['status'] == ftdf.FTDF_SUCCESS ):
                logstr = ( 'SCRIPT (',lineNr(),'): ERROR: more slotframes then MAX_SLOTFRAMES could be created' )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break

        idx += 1


# TEST: Slotframe: modify slotframe
if(result):
    msg_Slotframe_Modify = {
        'msgId': ftdf.FTDF_SET_SLOTFRAME_REQUEST,
        'handle': 0,
        'operation': ftdf.FTDF_MODIFY,
        'size': 21
    }

    DTS_sndMsg( devId1, msg_Slotframe_Modify )
    res, ret = DTS_getMsg( devId1, responseTimeout )
    if( res == False ):
        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: No response received from device' )
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False
    elif( ret['msgId'] != ftdf.FTDF_SET_SLOTFRAME_CONFIRM ):
        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: Expected SLOTFRAME_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False
    elif( ret['status'] != ftdf.FTDF_SUCCESS ):
        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: result:', resultStr[ ret['status'] ] )
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False
    else:
        # Check slotframe deleted
        msgGet['PIBAttribute'] = ftdf.FTDF_PIB_SLOTFRAME_TABLE

        DTS_sndMsg( devId1, msgGet )
        res, ret = DTS_getMsg( devId1, responseTimeout )
        if( res == False ):
            logstr = ( 'SCRIPT (',lineNr(),'): ERROR: No response received from device' )
            raise StopScript( ''.join( map( str, logstr ) ) )
            result = False
        elif( ret['msgId'] != ftdf.FTDF_GET_CONFIRM ):
            logstr = ( 'SCRIPT (',lineNr(),'): ERROR: Expected GET_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
            raise StopScript( ''.join( map( str, logstr ) ) )
            result = False
        elif( ret['status'] != ftdf.FTDF_SUCCESS ):
            logstr = ( 'SCRIPT (',lineNr(),'): ERROR: result:', resultStr[ ret['status'] ] )
            raise StopScript( ''.join( map( str, logstr ) ) )
            result = False
        else:
            if( ret['PIBAttributeValue']['slotframeEntries'][0]['slotframeSize'] != 21 ):
                logstr = ( 'SCRIPT (',lineNr(),'): ERROR: slotframe: slotframeSize' )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False


# TEST: Slotframe: modify non existing slotframe
if(result):
    msg_Slotframe_Modify = {
        'msgId': ftdf.FTDF_SET_SLOTFRAME_REQUEST,
        'handle': 10,
        'operation': ftdf.FTDF_MODIFY,
        'size': 12
    }

    DTS_sndMsg( devId1, msg_Slotframe_Modify )
    res, ret = DTS_getMsg( devId1, responseTimeout )
    if( res == False ):
        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: No response received from device' )
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False
    elif( ret['msgId'] != ftdf.FTDF_SET_SLOTFRAME_CONFIRM ):
        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: Expected SLOTFRAME_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False
    elif( ret['status'] != ftdf.FTDF_SLOTFRAME_NOT_FOUND ):
        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: expected result:SLOTFRAME_NOT_FOUND instead received', resultStr[ ret['status'] ] )
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False


#------------------------------ # TEST: Link
# TEST: Link: add link, linkHandle already in use, delete link
if(result):
    linkOptions_Transmit = 0x01
    linkOptions_Receive = 0x02
    linkOptions_Shared = 0x04
    linkOptions_Timekeeping = 0x08
    msg_Link_Add = {
        'msgId': ftdf.FTDF_SET_LINK_REQUEST,
        'operation': ftdf.FTDF_ADD,
        'linkHandle': 1,
        'slotframeHandle': 2,
        'timeslot': 3,
        'channelOffset': 4,
        'linkOptions': linkOptions_Transmit,
        'linkType': 1,
        'nodeAddress': 0x0020
    }

    DTS_sndMsg( devId1, msg_Link_Add )
    res, ret = DTS_getMsg( devId1, responseTimeout )
    if( res == False ):
        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: No response received from device' )
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False
    elif( ret['msgId'] != ftdf.FTDF_SET_LINK_CONFIRM ):
        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: Expected SET_LINK_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False
    elif( ret['status'] != ftdf.FTDF_SUCCESS ):
        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: result:', resultStr[ ret['status'] ] )
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False
    else:
        # Check set values
        msgGet['PIBAttribute'] = ftdf.FTDF_PIB_LINK_TABLE

        DTS_sndMsg( devId1, msgGet )
        res, ret = DTS_getMsg( devId1, responseTimeout )
        if( res == False ):
            logstr = ( 'SCRIPT (',lineNr(),'): ERROR: No response received from device' )
            raise StopScript( ''.join( map( str, logstr ) ) )
            result = False
        elif( ret['msgId'] != ftdf.FTDF_GET_CONFIRM ):
            logstr = ( 'SCRIPT (',lineNr(),'): ERROR: Expected GET_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
            raise StopScript( ''.join( map( str, logstr ) ) )
            result = False
        elif( ret['status'] != ftdf.FTDF_SUCCESS ):
            logstr = ( 'SCRIPT (',lineNr(),'): ERROR: result:', resultStr[ ret['status'] ] )
            raise StopScript( ''.join( map( str, logstr ) ) )
            result = False
        else:
            if( ret['PIBAttributeValue']['linkEntries'][0]['linkHandle'] != 1 ):
                logstr = ( 'SCRIPT (',lineNr(),'): ERROR: link: linkHandle' )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
            if( ret['PIBAttributeValue']['linkEntries'][0]['slotframeHandle'] != 2 ):
                logstr = ( 'SCRIPT (',lineNr(),'): ERROR: link: slotframeHandle' )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
            if( ret['PIBAttributeValue']['linkEntries'][0]['timeslot'] != 3 ):
                logstr = ( 'SCRIPT (',lineNr(),'): ERROR: link: timeslot' )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
            if( ret['PIBAttributeValue']['linkEntries'][0]['channelOffset'] != 4 ):
                logstr = ( 'SCRIPT (',lineNr(),'): ERROR: link: channelOffset' )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
            if( ret['PIBAttributeValue']['linkEntries'][0]['linkOptions'] != linkOptions_Transmit ):
                logstr = ( 'SCRIPT (',lineNr(),'): ERROR: link: linkOptions' )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
            if( ret['PIBAttributeValue']['linkEntries'][0]['linkType'] != 1 ):
                logstr = ( 'SCRIPT (',lineNr(),'): ERROR: link: linkType' )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
            if( ret['PIBAttributeValue']['linkEntries'][0]['nodeAddress'] != 0x0020 ):
                logstr = ( 'SCRIPT (',lineNr(),'): ERROR: link: nodeAddress' )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False

        # Delete created like
        linkOptions_Transmit = 0x01
        linkOptions_Receive = 0x02
        linkOptions_Shared = 0x04
        linkOptions_Timekeeping = 0x08
        msg_Link_Delete = {
            'msgId': ftdf.FTDF_SET_LINK_REQUEST,
            'operation': ftdf.FTDF_DELETE,
            'linkHandle': 1,
            'slotframeHandle': 2,
            'timeslot': 3,
            'channelOffset': 4,
            'linkOptions': linkOptions_Transmit,
            'linkType': 1,
            'nodeAddress': 0x0020
        }

        DTS_sndMsg( devId1, msg_Link_Delete )
        res, ret = DTS_getMsg( devId1, responseTimeout )
        if( res == False ):
            logstr = ( 'SCRIPT (',lineNr(),'): ERROR: No response received from device' )
            raise StopScript( ''.join( map( str, logstr ) ) )
            result = False
        elif( ret['msgId'] != ftdf.FTDF_SET_LINK_CONFIRM ):
            logstr = ( 'SCRIPT (',lineNr(),'): ERROR: Expected SET_LINK_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
            raise StopScript( ''.join( map( str, logstr ) ) )
            result = False
        elif( ret['status'] != ftdf.FTDF_SUCCESS ):
            logstr = ( 'SCRIPT (',lineNr(),'): ERROR: result:', resultStr[ ret['status'] ] )
            raise StopScript( ''.join( map( str, logstr ) ) )
            result = False
        else:
            # Check slotframe deleted
            msgGet['PIBAttribute'] = ftdf.FTDF_PIB_LINK_TABLE

            DTS_sndMsg( devId1, msgGet )
            res, ret = DTS_getMsg( devId1, responseTimeout )
            if( res == False ):
                logstr = ( 'SCRIPT (',lineNr(),'): ERROR: No response received from device' )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
            elif( ret['msgId'] != ftdf.FTDF_GET_CONFIRM ):
                logstr = ( 'SCRIPT (',lineNr(),'): ERROR: Expected GET_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
            elif( ret['status'] != ftdf.FTDF_SUCCESS ):
                logstr = ( 'SCRIPT (',lineNr(),'): ERROR: result:', resultStr[ ret['status'] ] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
            else:
                if( ret['PIBAttributeValue']['nrOfLinks'] != 0 ):
                    logstr = ( 'SCRIPT (',lineNr(),'): ERROR: slotframe: nrOfLinks should be 0' )
                    raise StopScript( ''.join( map( str, logstr ) ) )
                    result = False


# TEST: Link: delete non existing links
if(result):
    linkOptions_Transmit = 0x01
    linkOptions_Receive = 0x02
    linkOptions_Shared = 0x04
    linkOptions_Timekeeping = 0x08
    msg_Link_Delete = {
        'msgId': ftdf.FTDF_SET_LINK_REQUEST,
        'operation': ftdf.FTDF_DELETE,
        'linkHandle': 1,
        'slotframeHandle': 2,
        'timeslot': 3,
        'channelOffset': 4,
        'linkOptions': linkOptions_Transmit,
        'linkType': 1,
        'nodeAddress': 0x0020
    }

    DTS_sndMsg( devId1, msg_Link_Delete )
    res, ret = DTS_getMsg( devId1, responseTimeout )
    if( res == False ):
        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: No response received from device' )
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False
    elif( ret['msgId'] != ftdf.FTDF_SET_LINK_CONFIRM ):
        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: Expected SET_LINK_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False
    elif( ret['status'] != ftdf.FTDF_UNKNOWN_LINK ):
        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: expected result:UNKNOWN_LINK, instead received', resultStr[ ret['status'] ] )
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False


# TEST: Link: Max links
if(result):
    idx = 0
    while( idx < ftdf.FTDF_MAX_LINKS+1 ):
        linkOptions_Transmit = 0x01
        linkOptions_Receive = 0x02
        linkOptions_Shared = 0x04
        linkOptions_Timekeeping = 0x08
        msg_Link_Add = {
            'msgId': ftdf.FTDF_SET_LINK_REQUEST,
            'operation': ftdf.FTDF_ADD,
            'linkHandle': idx,
            'slotframeHandle': 1,
            'timeslot': idx,
            'channelOffset': 1,
            'linkOptions': linkOptions_Transmit,
            'linkType': 1,
            'nodeAddress': 0x0020
        }

        DTS_sndMsg( devId1, msg_Link_Add )
        res, ret = DTS_getMsg( devId1, responseTimeout )
        if( res == False ):
            logstr = ( 'SCRIPT (',lineNr(),'): ERROR: No response received from device' )
            raise StopScript( ''.join( map( str, logstr ) ) )
            result = False
            break
        elif( ret['msgId'] != ftdf.FTDF_SET_LINK_CONFIRM ):
            logstr = ( 'SCRIPT (',lineNr(),'): ERROR: Expected LINK_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
            raise StopScript( ''.join( map( str, logstr ) ) )
            result = False
            break
        else:
            if( idx != ftdf.FTDF_MAX_LINKS and
                ret['status'] != ftdf.FTDF_SUCCESS ):
                logstr = ( 'SCRIPT (',lineNr(),'): ERROR: result:', resultStr[ ret['status'] ] )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break

            if( idx == ftdf.FTDF_MAX_LINKS and
                ret['status'] == ftdf.FTDF_SUCCESS ):
                logstr = ( 'SCRIPT (',lineNr(),'): ERROR: more slotframes then MAX_LINKS could be created' )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False
                break

        idx += 1


# TEST: Link: modify link
if(result):
    linkOptions_Transmit = 0x01
    linkOptions_Receive = 0x02
    linkOptions_Shared = 0x04
    linkOptions_Timekeeping = 0x08
    msg_Link_Modify = {
        'msgId': ftdf.FTDF_SET_LINK_REQUEST,
        'operation': ftdf.FTDF_MODIFY,
        'linkHandle': 0,
        'slotframeHandle': 1,
        'timeslot': 0,
        'channelOffset': 1,
        'linkOptions': linkOptions_Receive,
        'linkType': 0,
        'nodeAddress': 0x0040
    }

    DTS_sndMsg( devId1, msg_Link_Modify )
    res, ret = DTS_getMsg( devId1, responseTimeout )
    if( res == False ):
        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: No response received from device' )
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False
    elif( ret['msgId'] != ftdf.FTDF_SET_LINK_CONFIRM ):
        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: Expected SET_LINK_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False
    elif( ret['status'] != ftdf.FTDF_SUCCESS ):
        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: result:', resultStr[ ret['status'] ] )
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False
    else:
        # Check link deleted
        msgGet['PIBAttribute'] = ftdf.FTDF_PIB_LINK_TABLE

        DTS_sndMsg( devId1, msgGet )
        res, ret = DTS_getMsg( devId1, responseTimeout )
        if( res == False ):
            logstr = ( 'SCRIPT (',lineNr(),'): ERROR: No response received from device' )
            raise StopScript( ''.join( map( str, logstr ) ) )
            result = False
        elif( ret['msgId'] != ftdf.FTDF_GET_CONFIRM ):
            logstr = ( 'SCRIPT (',lineNr(),'): ERROR: Expected GET_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
            raise StopScript( ''.join( map( str, logstr ) ) )
            result = False
        elif( ret['status'] != ftdf.FTDF_SUCCESS ):
            logstr = ( 'SCRIPT (',lineNr(),'): ERROR: result:', resultStr[ ret['status'] ] )
            raise StopScript( ''.join( map( str, logstr ) ) )
            result = False
        else:
            foundLink = False
            idx = 0
            while( idx < ftdf.FTDF_MAX_LINKS or
                   idx < ret['PIBAttributeValue']['nrOfLinks'] ):

                if( ret['PIBAttributeValue']['linkEntries'][idx]['linkHandle'] == 0 ):
                    if( ret['PIBAttributeValue']['linkEntries'][idx]['slotframeHandle'] != 1 ):
                        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: link: slotframeHandle' )
                        raise StopScript( ''.join( map( str, logstr ) ) )
                        result = False
                    if( ret['PIBAttributeValue']['linkEntries'][idx]['timeslot'] != 0 ):
                        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: link: timeslot' )
                        raise StopScript( ''.join( map( str, logstr ) ) )
                        result = False
                    if( ret['PIBAttributeValue']['linkEntries'][idx]['channelOffset'] != 1 ):
                        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: link: channelOffset' )
                        raise StopScript( ''.join( map( str, logstr ) ) )
                        result = False
                    if( ret['PIBAttributeValue']['linkEntries'][idx]['linkOptions'] != linkOptions_Receive ):
                        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: link: linkOptions' )
                        raise StopScript( ''.join( map( str, logstr ) ) )
                        result = False
                    if( ret['PIBAttributeValue']['linkEntries'][idx]['linkType'] != 0 ):
                        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: link: linkType' )
                        raise StopScript( ''.join( map( str, logstr ) ) )
                        result = False
                    if( ret['PIBAttributeValue']['linkEntries'][idx]['nodeAddress'] != 0x0040 ):
                        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: link: nodeAddress' )
                        raise StopScript( ''.join( map( str, logstr ) ) )
                        result = False

                    foundLink = True
                    break

                idx += 1 

            if( foundLink == False ):
                logstr = ( 'SCRIPT (',lineNr(),'): ERROR: modified link not found' )
                raise StopScript( ''.join( map( str, logstr ) ) )
                result = False


# TEST: Link: modify non existing link
if(result):
    linkOptions_Transmit = 0x01
    linkOptions_Receive = 0x02
    linkOptions_Shared = 0x04
    linkOptions_Timekeeping = 0x08
    msg_Link_Modify = {
        'msgId': ftdf.FTDF_SET_LINK_REQUEST,
        'operation': ftdf.FTDF_MODIFY,
        'linkHandle': 16,
        'slotframeHandle': 1,
        'timeslot': 0,
        'channelOffset': 1,
        'linkOptions': linkOptions_Transmit,
        'linkType': 1,
        'nodeAddress': 0x0020
    }

    DTS_sndMsg( devId1, msg_Link_Modify )
    res, ret = DTS_getMsg( devId1, responseTimeout )
    if( res == False ):
        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: No response received from device' )
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False
    elif( ret['msgId'] != ftdf.FTDF_SET_LINK_CONFIRM ):
        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: Expected SET_LINK_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False
    elif( ret['status'] != ftdf.FTDF_UNKNOWN_LINK ):
        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: expected result:UNKNOWN_LINK instead received', resultStr[ ret['status'] ] )
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False


# TEST: Link: delete all links
if(result):
    linkOptions_Transmit = 0x01
    linkOptions_Receive = 0x02
    linkOptions_Shared = 0x04
    linkOptions_Timekeeping = 0x08

    idx = 0
    while( idx < ftdf.FTDF_MAX_LINKS ):
        msg_Link_Delete = {
            'msgId': ftdf.FTDF_SET_LINK_REQUEST,
            'operation': ftdf.FTDF_DELETE,
            'linkHandle': idx,
            'slotframeHandle': 2,
            'timeslot': idx,
            'channelOffset': 4,
            'linkOptions': linkOptions_Transmit,
            'linkType': 1,
            'nodeAddress': 0x0020
        }

        DTS_sndMsg( devId1, msg_Link_Delete )
        res, ret = DTS_getMsg( devId1, responseTimeout )
        if( res == False ):
            logstr = ( 'SCRIPT (',lineNr(),'): ERROR: No response received from device' )
            raise StopScript( ''.join( map( str, logstr ) ) )
            result = False
        elif( ret['msgId'] != ftdf.FTDF_SET_LINK_CONFIRM ):
            logstr = ( 'SCRIPT (',lineNr(),'): ERROR: Expected SET_LINK_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
            raise StopScript( ''.join( map( str, logstr ) ) )
            result = False
        elif( ret['status'] != ftdf.FTDF_SUCCESS ):
            logstr = ( 'SCRIPT (',lineNr(),'): ERROR: could not delete link with linkHandle:', idx, 'result was:', resultStr[ ret['status'] ] )
            raise StopScript( ''.join( map( str, logstr ) ) )
            result = False

        idx += 1


# TEST: Link: add link to non existing slotframe should fail
if(result):
    linkOptions_Transmit = 0x01
    linkOptions_Receive = 0x02
    linkOptions_Shared = 0x04
    linkOptions_Timekeeping = 0x08
    msg_Link_Add = {
        'msgId': ftdf.FTDF_SET_LINK_REQUEST,
        'operation': ftdf.FTDF_ADD,
        'linkHandle': 0,
        'slotframeHandle': 20,
        'timeslot': 0,
        'channelOffset': 4,
        'linkOptions': linkOptions_Transmit,
        'linkType': 1,
        'nodeAddress': 0x0020
    }

    DTS_sndMsg( devId1, msg_Link_Add )
    res, ret = DTS_getMsg( devId1, responseTimeout )
    if( res == False ):
        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: No response received from device' )
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False
    elif( ret['msgId'] != ftdf.FTDF_SET_LINK_CONFIRM ):
        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: Expected SET_LINK_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False
    elif( ret['status'] != ftdf.FTDF_INVALID_PARAMETER):
        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: expected result:INVALID_PARAMETER instead received', resultStr[ ret['status'] ] )
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False


# TEST: Link: add link to non existing timeslot should fail
if(result):
    linkOptions_Transmit = 0x01
    linkOptions_Receive = 0x02
    linkOptions_Shared = 0x04
    linkOptions_Timekeeping = 0x08
    msg_Link_Add = {
        'msgId': ftdf.FTDF_SET_LINK_REQUEST,
        'operation': ftdf.FTDF_ADD,
        'linkHandle': 0,
        'slotframeHandle': 1,
        'timeslot': 30,
        'channelOffset': 4,
        'linkOptions': linkOptions_Transmit,
        'linkType': 1,
        'nodeAddress': 0x0020
    }

    DTS_sndMsg( devId1, msg_Link_Add )
    res, ret = DTS_getMsg( devId1, responseTimeout )
    if( res == False ):
        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: No response received from device' )
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False
    elif( ret['msgId'] != ftdf.FTDF_SET_LINK_CONFIRM ):
        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: Expected SET_LINK_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False
    elif( ret['status'] != ftdf.FTDF_INVALID_PARAMETER):
        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: expected result:INVALID_PARAMETER instead received', resultStr[ ret['status'] ] )
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False


# TEST: Link: add link to non slotframe timeslot that already has link should fail
if(result):
    linkOptions_Transmit = 0x01
    linkOptions_Receive = 0x02
    linkOptions_Shared = 0x04
    linkOptions_Timekeeping = 0x08
    msg_Link_Add = {
        'msgId': ftdf.FTDF_SET_LINK_REQUEST,
        'operation': ftdf.FTDF_ADD,
        'linkHandle': 0,
        'slotframeHandle': 0,
        'timeslot': 0,
        'channelOffset': 1,
        'linkOptions': linkOptions_Transmit,
        'linkType': 1,
        'nodeAddress': 0x0020
    }

    DTS_sndMsg( devId1, msg_Link_Add )
    res, ret = DTS_getMsg( devId1, responseTimeout )
    if( res == False ):
        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: No response received from device' )
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False
    elif( ret['msgId'] != ftdf.FTDF_SET_LINK_CONFIRM ):
        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: Expected SET_LINK_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False
    elif( ret['status'] != ftdf.FTDF_SUCCESS ):
        logstr = ( 'SCRIPT (',lineNr(),'): ERROR: result:', resultStr[ ret['status'] ] )
        raise StopScript( ''.join( map( str, logstr ) ) )
        result = False
    else:
        msg_Link_Add = {
            'msgId': ftdf.FTDF_SET_LINK_REQUEST,
            'operation': ftdf.FTDF_ADD,
            'linkHandle': 1,
            'slotframeHandle': 0,
            'timeslot': 0,
            'channelOffset': 1,
            'linkOptions': linkOptions_Transmit,
            'linkType': 1,
            'nodeAddress': 0x0020
        }

        DTS_sndMsg( devId1, msg_Link_Add )
        res, ret = DTS_getMsg( devId1, responseTimeout )
        if( res == False ):
            logstr = ( 'SCRIPT (',lineNr(),'): ERROR: No response received from device' )
            raise StopScript( ''.join( map( str, logstr ) ) )
            result = False
        elif( ret['msgId'] != ftdf.FTDF_SET_LINK_CONFIRM ):
            logstr = ( 'SCRIPT (',lineNr(),'): ERROR: Expected SET_LINK_CONFIRM confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
            raise StopScript( ''.join( map( str, logstr ) ) )
            result = False
        elif( ret['status'] != ftdf.FTDF_INVALID_PARAMETER ):
            logstr = ( 'SCRIPT (',lineNr(),'): ERROR: expected result:INVALID_PARAMETER instead received', resultStr[ ret['status'] ] )
            raise StopScript( ''.join( map( str, logstr ) ) )
            result = False


if( not result ):
    raise StopScript('SCRIPT: FAILED')
