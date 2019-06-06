import os
import subprocess
import sys

from libCore import *
from libGeolocation import *


class APRSMessageMaker:
    def __init__(self):
        self.geo = Geolocation()
    
    def GetRefStr(self):
        return "KN4IUD-11>WSPR,TCPIP*:/225418h2646.53N/08259.54WO294/010/A=008810 MM17  ) !',$   #"
    
    def GetRefStrNoSSID(self):
        return "KN4IUD>WSPR,TCPIP*:/225418h2646.53N/08259.54WO294/010/A=008810 MM17  ) !',$   #"
    
    def MakeLocationReportMessage(self, call, ssid, wsprDate, grid, speedMph, altitudeFt, extraData = ""):
        # Basic APRS message
        callsign           = call
        ssid               = str(ssid)
        receivedBy         = "WSPR"
        timeOfReceptionUtc = self.GetTimeUtc(wsprDate)
        latitudeStr        = self.geo.ConvertGridToLatitudeDegMinHundredths(grid)
        symbolTableId      = "/"    ;# table 1
        longitudeStr       = self.geo.ConvertGridToLongitudeDegMinHundredths(grid)
        symbolCode         = "O"    ;# balloon
        courseDegs         = self.GetCourseDegs(0)
        speedKnots         = self.GetSpeedKnotsFromSpeedMph(speedMph)
        altitudeFt         = self.ConvertAltitudeFtToAPRSFeet(altitudeFt)
        
        # Encoded data fun to slot in
        # ...

        # Construct message
        msg  = ""
        msg += callsign + "-" + ssid
        msg += ">"
        msg += receivedBy
        msg += ",TCPIP*"
        msg += ":"
        msg += "/"
        msg += timeOfReceptionUtc
        msg += latitudeStr
        msg += symbolTableId
        msg += longitudeStr
        msg += symbolCode
        msg += courseDegs
        msg += speedKnots
        msg += altitudeFt
        
        # There are now 43 bytes remaining for comment
        # Testing shows you can add as much arbitrary data as you want.
        # There are no rules on TCPIP uploads it seems, just do whatever.
        msg += extraData[0:43]
        
        return msg
        
        

    #################################################
    ##
    ## Time
    ##
    #################################################

    def GetTimeUtc(self, wsprDate):
        partList = wsprDate.split(" ")[1].split(":")  ;# 2019-05-13 02:20 to [02 20]
        timeUtc = "".join(partList) + "00h"           ;# now 022000h
        
        return timeUtc
    
        

    #################################################
    ##
    ## Course
    ##
    #################################################
        
    def GetCourseDegs(self, degs):
        str = "%03i" % (int(degs))
        
        return str
        
        
    #################################################
    ##
    ## Speed
    ##
    #################################################
        
    def GetSpeedKnotsFromSpeedMph(self, speedMph):
        str = "/%03i" % (int(speedMph / 1.151))
        
        return str
        

    #################################################
    ##
    ## Altitude
    ##
    #################################################
        
    def ConvertAltitudeFtToAPRSFeet(self, altitudeFt):
        str = "/A=%06i" % (altitudeFt)
        
        return str
        
        
