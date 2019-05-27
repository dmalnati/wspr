import os
import subprocess
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *

from libAPRSMessageMaker import *
from libAPRSUploader import *
from libWSPRDecoder import *


class WsprToAprsBridge:
    def __init__(self, user, password, debug = False):
        self.dateLast = ""
        self.nvList = []
        self.call__timeLastUploaded = dict()
        
        self.wsprDecoder  = WSPRDecoder()
        self.amm          = APRSMessageMaker()
        self.aprsUploader = APRSUploader(user, password, debug)
        
        # set up default callbacks
        self.cbFnOnPreUpload      = self.DefaultCbFnOnPreUpload
        self.cbFnOnPeriodComplete = self.DefaultCbFnOnPeriodComplete
        self.cbOnRateLimit        = self.DefaultCbOnRateLimit
        
    def DefaultCbFnOnPreUpload(self, name__value, aprsMsg):
        fieldRawList = [
            'DATE',
            'CALLSIGN',
            'FREQUENCY',
            'SNR',
            'DRIFT',
            'GRID',
            'DBM',
            'WATTS',
            'REPORTER',
            'RGRID',
            'KM',
            'MI'
        ]
        
        fieldList = name__value.keys()
        fieldList.sort()
        
        max = 0
        for field in fieldList:
            strLen = len(field)
            
            if strLen > max:
                max = strLen
    
        formatStr = "%-" + str(max) + "s: %s"

        for field in fieldList:
            prefix = "    "
            if field not in fieldRawList:
                prefix = "   +"
            
            if field != "TIMESTAMP" and field != "rowid":
                Log(prefix + formatStr % (field, str(name__value[field])))
            
        Log(aprsMsg)
        
    
    def SetCbFnOnPreUpload(self, cbFnOnPreUpload):
        self.cbFnOnPreUpload = cbFnOnPreUpload
        
    def DefaultCbFnOnPeriodComplete(self, period):
        Log("Period %s complete, processing uploads" % period)
        
    def SetCbFnOnPeriodComplete(self, cbFnOnPeriodComplete):
        self.cbFnOnPeriodComplete = cbFnOnPeriodComplete
    
    def DefaultCbOnRateLimit(self, call, secWait):
        Log("Sleeping %s sec due to rate limiting for %s" % (secWait, call))
    
    def SetCbOnRateLimit(self, cbOnRateLimit):
        self.cbOnRateLimit = cbOnRateLimit
    
    def Start(self):
        pass
        
    def Stop(self):
        self.OnAllUpdatesThisPeriodComplete()
        
    def OnUpdate(self, name__value):
        # assume updates are in chronological order
        # we want to know when we've seen the last of a 2-minute bucket
        date = name__value["DATE"]
        
        if self.dateLast != date and self.dateLast != "":
            # the time has changed, batch process all stored data
            if len(self.nvList):
                self.OnAllUpdatesThisPeriodComplete()
            
        # keep track of the time, if it changed, you've handled it by now
        self.dateLast = date
    
        if self.wsprDecoder.IsEligibleForUpload(name__value):
            # keep all eligible messages for this time period
            self.nvList.append(name__value)
            
            
    # DOWNLOAD[11680]
    #   DATE     : 2019-05-13 02:20
    #   CALLSIGN : 8P9DH
    #   FREQUENCY: 14.097130
    #   SNR      : -23
    #   DRIFT    : 0
    #   GRID     : GK03
    #   DBM      : +37
    #   WATTS    : 5.012
    #   REPORTER : WA2ZKD
    #   RGRID    : FN13ed
    #   KM       : 3748
    #   MI       : 2329
    #
    #  KN4IUD-11>WSPR,TCPIP*:/225418h2646.53N/08259.54WO294/010/A=008810 MM17  ) !',$   #
    #
    def OnAllUpdatesThisPeriodComplete(self):
        self.cbFnOnPeriodComplete(self.dateLast)
    
        # convert all cached
        nvDecodedList = self.wsprDecoder.DecodeList(self.nvList)
        
        # group by callsign
        call__nvList = dict()
        for nvDecoded in nvDecodedList:
            call = nvDecoded["CALLSIGN_DECODED"]
            
            if call not in call__nvList.keys():
                call__nvList[call] = []
            
            call__nvList[call].append(nvDecoded)
    
        # iterate by callsign
        for call in call__nvList.keys():
            nvList = call__nvList[call]
            
            # determine:
            # furthest signal
            #   reporter at furthest signal
            # best SNR
            #   frequency at best SNR
            distMiMax    = 0
            reporterBest = "UNKN"
            snrMax       = 0
            freqBest     = 0
            for name__value in nvList:
                distMi = name__value["MI"]
                if distMi > distMiMax:
                    distMiMax    = distMi
                    reporterBest = name__value["REPORTER"]
            
                snr = name__value["SNR"]
                if snr[0] == "+":
                    snr = snr[1:]
                if snr > snrMax:
                    snrMax = snr
                    freqBest = name__value["FREQUENCY"]
                    
            # convert freqBest to just the relevant part of the frequency
            # in order to use less space.
            # eg 14.097034 - 14.097000 * 10,000,000=  34

            FREQ_LOW = 14.097000
            freqBest = float(freqBest)
            freqOffset = str(int((freqBest - FREQ_LOW) * 1000000))
            
            # reference using the first element
            name__value = nvList[0]
            countHeard  = len(nvList)
            
            # construct APRS message
            wsprCall = call
            ssid     = 15
            wsprDate = name__value["DATE"]
            wsprGrid = name__value["GRID_DECODED"]
            speedMph = name__value["SPEED_MPH"]
            altitudeFt = name__value["ALTITUDE_FT"]
            
            # extra 43 bytes useful for whatever you want
            extraData  = ""
            extraData += " " + self.ConvertCtoF(name__value["TEMPERATURE_C"]) + "F"
            extraData += " " + self.ConvertMilliVoltToVolt(name__value["VOLTAGE"]) + "V"
            extraData += " " + distMiMax + "mi"
            extraData += " " + name__value["CALLSIGN"]
            extraData += " " + str(countHeard)
            extraData += " " + snrMax
            extraData += " " + freqOffset
            extraData += " " + name__value["DRIFT"]
            
            msg = self.amm.MakeLocationReportMessage(wsprCall, ssid, wsprDate, wsprGrid, speedMph, altitudeFt, extraData)
            
            # upload APRS message
            # but throttle to 1 upload per callsign to avoid server rate limiting
            if call in self.call__timeLastUploaded.keys():
                timeLast = self.call__timeLastUploaded[call]
                timeNow  = DateTimeNow()
                secsDiff = DateTimeStrDiffSec(timeNow, timeLast)
                
                # practical testing showed 1 per second seems to be ok
                if secsDiff < 1:
                    self.cbOnRateLimit(call, 1)
                    time.sleep(1)
            
            self.call__timeLastUploaded[call] = DateTimeNow()
            
            self.cbFnOnPreUpload(name__value, msg)
            
            self.aprsUploader.Upload(msg)        
        
        # reset state
        self.nvList = []

    def ConvertCtoF(self, tempC):
        return str(int((tempC * (9.0 / 5.0)) + 32))

    def ConvertMilliVoltToVolt(self, milliVolt):
        volt = milliVolt / 1000.0
        voltStr = "%0.1f" % volt
        
        return voltStr
        
        
        