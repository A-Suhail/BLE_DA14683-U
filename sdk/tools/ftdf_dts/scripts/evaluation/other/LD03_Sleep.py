import sys  #cli arguments
import time  #sleep

from scriptIncludes import *

lowPowerClockCycle = 30517578 # 32.768kHz
wakeupLatency      = 100      # 3ms

def error( logstr ):
    raise StopScript( logstr )

############
# RESET
############
DTS_sndMsg(devId1, msgRESET)

res, ret = DTS_getMsg(devId1, responseTimeout)
if res == False:
    error("No response")
elif ret['msgId'] != ftdf.FTDF_RESET_CONFIRM or ret['status'] != ftdf.FTDF_SUCCESS:
    error("Incorrect result")


############
# Sleep for 5 seconds
############

msg = {'msgId': ftdf.FTDF_SLEEP_REQUEST,
       'sleepTime': 5000000}

DTS_sndMsg( devId1, msg )

############
# Check device wakes up after 5 seconds
############

res, ret = DTS_getMsg( devId1, 7 )

if res == False:
    error( "Device did not wake up" )
elif ret['msgId'] != ftdf.FTDF_EXPLICIT_WAKE_UP:
    error( "Expected explicit wake up msg" )

