import os
import subprocess
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *

        
        
#
# Takes in WSPR messages
# Converts to decoded structures
#
class WSPRDecoder:
    def __init__(self):
        pass
        
    def IsEligibleForUpload(self, name__value):
        retVal = False
        
        call = self.GetDecodedCallsign(name__value)
        if call == "KD2KDD":
            retVal = True
        
        return retVal
        
    def DecodeList(self, nvList):
        retVal = []
        
        for name__value in nvList:
            retVal.append(self.Decode(name__value))
        
        return retVal
        
        
    # The callsign buffer will be used for:
    #
    # Position    Values      Usage (number of values)
    # Callsign 1  Q,0         Telemetry Channel (2)
    # Callsign 2  0-9,A-Z     Speed (9)
    #                         Altitude 1,000ft increment (2)
    #                         Altitude 5000ft increment (2)
    # Callsign 3  0-9         Telemetry Channel (10)
    # Callsign 4  A-Z         Grid Square 5th char (A-X) (24)
    # Callsign 5  A-Z         Grid Square 6th char (A-X) (24)
    # Callsign 6  A-Z, space  Temperature(8)
    #                         Voltage(3)
    def Decode(self, name__valueInput):
        # first, assume all decoded fields are the same as input
        name__value = dict(name__valueInput)
        
        # now, go through rules to determine what fields to add/modify
        name__value["CALLSIGN_DECODED"] = self.GetDecodedCallsign(name__valueInput)
        name__value["SPEED_MPH"]        = self.GetDecodedSpeedMph(name__valueInput)
        name__value["ALTITUDE_FT"]      = self.GetDecodedAltitudeFt(name__valueInput)
        name__value["GRID_DECODED"]     = self.GetDecodedGrid(name__valueInput)
        name__value["TEMPERATURE_C"]    = self.GetDecodedTemperatureC(name__value)
        name__value["VOLTAGE"]          = self.GetDecodedVoltage(name__value)
        
        return name__value
        
    def GetDecodedCallsign(self, name__value):
        retVal = name__value["CALLSIGN"]
        
        id = str(name__value["CALLSIGN"][0]) + str(name__value["CALLSIGN"][2])
        
        #if id == "00":
        #    retVal = "KD2KDD"
            
        if id == "Q2":
            retVal = "KD2KDD"
        
        return retVal
    
    def GetDecodedSpeedMph(self, name__value):
        speedKnotsIncr, ftIncr1000Val, ftIncr500Val = self.DecodeCallsign2(name__value)
        
        speedKnots = speedKnotsIncr * 16
        speedMph   = round(speedKnots * 1.151)
        
        return speedMph
        
    def GetDecodedAltitudeFt(self, name__value):
        retVal = 0
        
        speedKnotsIncr, ftIncr1000Val, ftIncr500Val = self.DecodeCallsign2(name__value)
        ftIncr2000Val                         = self.DecodePower(name__value)
        
        retVal = (2000 * ftIncr2000Val) + (1000 * ftIncr1000Val) + (500 * ftIncr500Val)
        
        return retVal
        
    def GetDecodedGrid(self, name__value):
        grid0to4 = name__value["GRID"]
        grid5to6 = name__value["CALLSIGN"][3:5]
        
        grid0to6 = grid0to4 + grid5to6
        
        return grid0to6
        
    def GetDecodedTemperatureC(self, name__value):
        temperatureC, milliVolt = self.DecodeCallsign6(name__value)
        
        temperatureC = -50 + (temperatureC * 10)
        
        return temperatureC
    
    def GetDecodedVoltage(self, name__value):
        temperatureC, milliVolt = self.DecodeCallsign6(name__value)
        
        milliVolt = 1500 + (milliVolt * 1500)
        
        return milliVolt

    def DecodePower(self, name__value):
        dbm = name__value["DBM"][1:]    ;# strip the +
        
        powerList = [ 0, 3, 7, 10, 13, 17, 20, 23, 27, 30, 33, 37, 40, 43, 47, 50, 53, 57, 60 ]
        
        idxMatch = 0
        
        idx = 0
        for power in powerList:
            if dbm == str(power):
                idxMatch = idx
        
            idx += 1
        
        retVal = idxMatch
        
        return retVal
        
    def DecodeCallsign2(self, name__value):
        c2Val = self.UnMapFromAlphaNum(name__value["CALLSIGN"][1])
        
        ftIncr500Val,   c2Val = self.UnPack(c2Val, 2)
        ftIncr1000Val,  c2Val = self.UnPack(c2Val, 2)
        speedKnotsIncr, c2Val = self.UnPack(c2Val, 9)
        
        return speedKnotsIncr, ftIncr1000Val, ftIncr500Val

    def DecodeCallsign6(self, name__value):
        c6Val = self.UnMapFromAlphaSpace(name__value["CALLSIGN"][5])
        
        milliVolt,    c6Val = self.UnPack(c6Val, 3)
        temperatureC, c6Val = self.UnPack(c6Val, 8)
        
        return temperatureC, milliVolt
        
        
    def UnMapFromAlphaNum(self, val):
        retVal = 0
        
        if val.isalpha():
            retVal = 10 + (ord(val) - ord('A'))
        else:
            retVal = ord(val) - ord('0')
    
        return retVal
    
    def UnMapFromAlphaSpace(self, val):
        retVal = 0
        
        if val == " ":
            retVal = 26
        else:
            retVal = ord(val) - ord('A')
        
        return retVal
        
        
    def UnPack(self, unpackSource, valueCount):
        unpackVal            = unpackSource  % valueCount
        unpackSourceAdjusted = unpackSource // valueCount
    
        return unpackVal, unpackSourceAdjusted
        
        
        
        
        
        
        
        
        
        
        
