#TODO: energie list chack for value's whem bugs are fixxed

import sys  #cli arguments
import time  #sleep

from scriptIncludes import *

DTS_getReleaseInfo(devId1)
DTS_getReleaseInfo(devId2)
#time.sleep( responseTimeout )
res, ret = DTS_getMsg( devId1,responseTimeout )
res, ret = DTS_getMsg( devId2,responseTimeout )

# Data frame
msdu = [0x1, 0x2, 0x3, 0x4, 0x5]
keySource = [0x0, 0x0, 0x0, 0x0,
       0x0, 0x0, 0x0, 0x0]
msgDATA = { 'msgId': ftdf.FTDF_DATA_REQUEST,
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
      'keySource': keySource,
      'keyIndex': 0,
      'frameControlOptions': 0,
      'headerIEList': 0,
      'payloadIEList': 0,
      'sendMultiPurpose': False }
      
msgSCAN_inval_channelPage = { 'msgId':        ftdf.FTDF_SCAN_REQUEST,
                               'scanType':     ftdf.FTDF_ED_SCAN,
                               'scanChannels': 0x3ff800,
                               'channelPage':  10,
                               'scanDuration': 0,
                               'securityLevel': 0,
                               'keyIdMode': 0,
                               'keySource': keySource,
                               'keyIndex': 0}
                               
msgSCAN_inval_scanChannels1 = { 'msgId':        ftdf.FTDF_SCAN_REQUEST,
                               'scanType':     ftdf.FTDF_ED_SCAN,
                               'scanChannels': 0x2,
                               'channelPage':  0,
                               'scanDuration': 0,
                               'securityLevel': 0,
                               'keyIdMode': 0,
                               'keySource': keySource,
                               'keyIndex': 0} 

msgSCAN_inval_scanChannels2 = { 'msgId':        ftdf.FTDF_SCAN_REQUEST,
                               'scanType':     ftdf.FTDF_ED_SCAN,
                               'scanChannels': 0x3fffff,
                               'channelPage':  0,
                               'scanDuration': 0,
                               'securityLevel': 0,
                               'keyIdMode': 0,
                               'keySource': keySource,
                               'keyIndex': 0}                                
      
msgSCAN_short = { 'msgId':        ftdf.FTDF_SCAN_REQUEST,
                  'scanType':     ftdf.FTDF_ED_SCAN,
                  'scanChannels': 0x7fff800,
                  'channelPage':  0,
                  'scanDuration': 1,
                  'securityLevel': 0,
                  'keyIdMode': 0,
                  'keySource': keySource,
                  'keyIndex': 0}
                  
msgSCAN_long = { 'msgId':        ftdf.FTDF_SCAN_REQUEST,
                 'scanType':     ftdf.FTDF_ED_SCAN,
                 'scanChannels': 0x7fff800,
                 'channelPage':  0,
                 'scanDuration': 5,
                 'securityLevel': 0,
                 'keyIdMode': 0,
                 'keySource': keySource,
                 'keyIndex': 0,}                  

msgSET_PtiConfig = { 'msgId': ftdf.FTDF_SET_REQUEST,
           'PIBAttribute': ftdf.FTDF_PIB_PTI_CONFIG,
           'PIBAttributeValue': [2, 1, 3, 4, 5, 6, 7, 8] }                   


msgSET_keepPhyEnable = { 'msgId': ftdf.FTDF_SET_REQUEST,
           'PIBAttribute': ftdf.FTDF_PIB_KEEP_PHY_ENABLED,
           'PIBAttributeValue': 1 }    


msgDbgModeSetRequest = {
    'msgId': ftdf.FTDF_DBG_MODE_SET_REQUEST,
    'dbgMode': 0x3b,
}

# Message order
msgFlow = ( devId1, msgRESET, ftdf.FTDF_RESET_CONFIRM,
            devId2, msgRESET, ftdf.FTDF_RESET_CONFIRM,
      
            devId1, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_PANId, ftdf.FTDF_SET_CONFIRM,
      
            devId1, msgSET_Dev1_ShortAddress, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_Dev2_ShortAddress, ftdf.FTDF_SET_CONFIRM,
      
            devId1, msgSET_PtiConfig, ftdf.FTDF_SET_CONFIRM,
            devId2, msgSET_PtiConfig, ftdf.FTDF_SET_CONFIRM, 
            )

idx = 0
res = True
error = 0

while( idx < len( msgFlow ) ):
  # Send message
  DTS_sndMsg( msgFlow[idx], msgFlow[idx+1] )

  # Get message confirm
  res, ret = DTS_getMsg( msgFlow[idx],responseTimeout )

  # Check received expected confirm
  if( res == False ):
    raise StopScript( 'SCRIPT: ERROR: No response received from device' )
    break
  elif ret['msgId'] != msgFlow[idx+2]:
    logstr = ( 'SCRIPT: ERROR: Expected ', msgFlow[idx+2], ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
    raise StopScript( ''.join( map( str, logstr ) ) )
    break
    
  idx += 3

# Reset arbiter
DTS_ArbiterReset(devId1)
DTS_ArbiterReset(devId2)

DTS_sndMsg(devId1, msgDbgModeSetRequest);
DTS_sndMsg(devId2, msgDbgModeSetRequest);

DTS_ArbiterSetConfig(devId1, 0x07f0, 0, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_EXT, 0,
                     ftdf.DTS_COEX_MAC_TYPE_FTDF, 2,
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
 
DTS_ArbiterSetConfig(devId2, 0x07f0, 0, 0, 
                     ftdf.DTS_COEX_MAC_TYPE_EXT, 0,
                     ftdf.DTS_COEX_MAC_TYPE_FTDF, 2,
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
 

##################  
## test ED scan ##
################## 
DTS_setRegister(devId1,0x50002F80, 2, 30)
DTS_setRegister(devId2,0x50002F80, 2, 30)  
DTS_sndMsg( devId1, msgSCAN_short )
res, ret = DTS_getMsg( devId1,responseTimeout )
if( res == False ):
  raise StopScript( 'SCRIPT: ERROR: No response received from device' )
  error += 1
elif ret['msgId'] != ftdf.FTDF_SCAN_CONFIRM:
  logstr = ( 'SCRIPT: ERROR: Expected ', msgFlow[idx+2], ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
elif ret['status'] != ftdf.FTDF_SUCCESS: 
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_SUCCESS , instead received ', resultStr[ ret['status'] ] )
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1

################################
## test FTDF_SCAN_IN_PROGRESS ##
################################
DTS_sndMsg( devId1, msgSCAN_long )
DTS_sndMsg( devId1, msgSCAN_short )
res, ret = DTS_getMsg( devId1,responseTimeout )
if( res == False ):
  raise StopScript( 'SCRIPT: ERROR: No response received from device' )
  error += 1
elif ret['msgId'] != ftdf.FTDF_SCAN_CONFIRM:
  logstr = ( 'SCRIPT: ERROR: Expected ', msgFlow[idx+2], ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1
elif ret['status'] != ftdf.FTDF_SCAN_IN_PROGRESS: 
  logstr = ( 'SCRIPT: ERROR: Expected FTDF_SCAN_IN_PROGRESS , instead received ', resultStr[ ret['status'] ] )
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1

res, ret = DTS_getMsg( devId1, 60 )
if( res == False ):
  raise StopScript( 'SCRIPT: ERROR: No response received from device' )
  error += 1
elif ret['msgId'] != ftdf.FTDF_SCAN_CONFIRM:
  logstr = ( 'SCRIPT: ERROR: Expected ', msgFlow[idx+2], ' confirm, instead received ', msgNameStr[ ret['msgId'] -1 ])
  raise StopScript( ''.join( map( str, logstr ) ) )
  error += 1

##########################################
## END OF TEST, let examine the results ##
##########################################   
if error != 0:
  logstr = ('SCRIPT: test FAILED with ' , error , ' ERRORS')
  raise StopScript( ''.join( map( str, logstr ) ) )

