#!/usr/bin/python3.5 -u

import os
import subprocess
import time
import sys

from libCore import *

from libAPRSMessageMaker import *
from libAPRSUploader import *



class WsprToAprsBridge:
    def __init__(self, user, password, debug = False):
        self.dateLast = ""
        self.nvList = []
        self.call__timeLastUploaded = dict()
        
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
        
        fieldList = sorted(name__value.keys())
        
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
    
        # keep all eligible messages for this time period
        self.nvList.append(name__value)
            
            
# Period 2019-06-03 20:26 complete, processing uploads
#    +ALTITUDE_FT     : 13500
#     CALLSIGN        : QJ2XRH
#    +CALLSIGN_DECODED: KD2KDD
#     DATE            : 2019-06-03 20:26
#     DBM             : +20
#     DRIFT           : 0
#     FREQUENCY       : 14.097118
#     GRID            : FN20
#    +GRID_DECODED    : FN20XR
#    +ID              : 1536
#     KM              : 81
#     MI              : 50
#     REPORTER        : KD2KDD
#     RGRID           : FN20
#     SNR             : 16
#    +SPEED_MPH       : 74
#    +TEMPERATURE_C   : -30
#    +VOLTAGE         : 3000
#     WATTS           : 0
#
# KD2KDD-15>WSPR,TCPIP*:/202600h4042.53N/07404.91WO000/064/A=013500 -22F 3.0V 50mi QJ2XRH 2 16 118 0
    def OnAllUpdatesThisPeriodComplete(self):
        if len(self.nvList):
            self.OnAllUpdatesThisPeriodCompleteInternal()
            self.dateLast = ""
    
    def OnAllUpdatesThisPeriodCompleteInternal(self):
        self.cbFnOnPeriodComplete(self.dateLast)
    
        # convert all cached
        nvDecodedList = self.nvList
        
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
            snrMax       = -99
            freqBest     = 0
            for name__value in nvList:
                distMi = int(name__value["MI"])
                if distMi > distMiMax:
                    distMiMax    = distMi
                    reporterBest = name__value["REPORTER"]
            
                snr = name__value["SNR"]
                if snr[0] == "+":
                    snr = snr[1:]
                snr = int(snr)
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
            speedMph = int(name__value["SPEED_MPH"])
            altitudeFt = int(name__value["ALTITUDE_FT"])
            
            # extra 43 bytes useful for whatever you want
            extraData  = ""
            extraData += " " + self.ConvertCtoF(int(name__value["TEMPERATURE_C"])) + "F"
            extraData += " " + self.ConvertMilliVoltToVolt(int(name__value["VOLTAGE"])) + "V"
            extraData += " " + str(distMiMax) + "mi"
            extraData += " " + name__value["CALLSIGN"]
            extraData += " " + str(countHeard)
            extraData += " " + str(snrMax)
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
        








class App(WSApp):
    def __init__(self, user, password, intervalSec, startMode, debug):
        WSApp.__init__(self)

        # Basic object configuration
        self.service     = self.GetSelfServiceName()
        self.user        = user
        self.password    = password
        self.intervalSec = intervalSec
        self.startMode   = startMode
        self.debug       = debug

        Log("Configured for:")
        Log("  service     = %s" % self.service)
        Log("  debug       = %s" % self.debug)
        Log("  user        = %s" % self.user)
        Log("  password    = %s" % self.password)
        Log("  intervalSec = %s" % self.intervalSec)
        Log("  startMode   = %s" % self.startMode)
        Log("")
        
        # get handles to database
        self.db  = ManagedDatabase(self)


    def Run(self):
        Log("Waiting for Database Available to begin")
        Log("")
        
        self.db.SetCbOnDatabaseStateChange(self.OnDatabaseStateChange)
        
        evm_MainLoop()


    def OnDatabaseAvaiable(self):
        Log("Database Available, starting")

        self.tWd = self.db.GetTable("WSPR_DECODED")
        self.tnv = self.db.GetTable("NAME_VALUE")
        
        # get bridge
        self.bridge = WsprToAprsBridge(self.user, self.password, self.debug)
        
        # handle cold start
        if self.startMode == "cold":
            rowIdLast = self.GetLast()
            
            Log("    Resetting last processed to -1 from %s" % rowIdLast)
            Log("")
            
            self.SetLast(-1)

        evm_SetTimeout(self.OnTimeout, 0)
        
        self.bridge.Start()

    def OnDatabaseClosing(self):
        Log("Database Closing, no action taken")
        
    def OnDatabaseStateChange(self, dbState):
        if dbState == "DATABASE_AVAILABLE":
            self.OnDatabaseAvaiable()
        if dbState == "DATABASE_CLOSING":
            self.OnDatabaseClosing()


    def GetLast(self):
        rec = self.tnv.GetRecordAccessor()
        
        rec.Set("NAME", "%s_LAST_PROCESSED" % self.service)
        if not rec.Read():
            rec.Set("VALUE", "-1")
            rec.Insert()
        
        rec.Set("NAME", "%s_LAST_PROCESSED" % self.service)
        rec.Read()
        retVal = int(rec.Get("VALUE"))
        
        return retVal
        
    def SetLast(self, rowid):
        rec = self.tnv.GetRecordAccessor()
        
        rec.Set("NAME", "%s_LAST_PROCESSED" % self.service)
        rec.Read()
        rec.Set("VALUE", str(rowid))
        
        retVal = rec.Update()
        
        return retVal

    def OnUpdate(self, rec):
        # unpack records
        name__value = rec.GetDict()
        
        # send to bridge
        self.bridge.OnUpdate(name__value)
        
    def OnBatchComplete(self):
        self.bridge.OnAllUpdatesThisPeriodComplete()

    def Process(self):
        Log("Scanning WSPR_DECODED for new spots")
        
        # Prepare to walk records
        rec = self.tWd.GetRecordAccessor()
        rec.SetRowId(self.GetLast())
        
        Log("  Starting from rowid %s" % rec.GetRowId())
        
        # Walk list of records starting from last seen
        count = 0
        timeStart = DateTimeNow()
        while rec.ReadNextInLinearScan():
            count += 1
            self.OnUpdate(rec)
        self.OnBatchComplete()
        
        timeEnd = DateTimeNow()
        secDiff = DateTimeStrDiffSec(timeEnd, timeStart)
        
        Log("  Scan took %s sec" % Commas(secDiff))
        Log("  Saw %s new records" % Commas(count))
        
        if count != 0:
            rowId = rec.GetRowId()
            Log("    Saving %s as last rowid seen" % rowId)
            self.SetLast(rowId)
            
    
    def OnTimeout(self):
        timeStart = DateTimeNow()
        self.Process()
        timeEnd = DateTimeNow()
        
        secDiff = DateTimeStrDiffSec(timeEnd, timeStart)
        
        timeoutMs = self.intervalSec * 1000
        
        Log("Waking in %s sec" % str(timeoutMs // 1000))
        Log("")
        
        evm_SetTimeout(self.OnTimeout, timeoutMs)
        
    

def Main():
    LogIncludeDate(True)
    
    # default arguments
    intervalSec = 30
    startMode   = "warm"
    debug       = False

    if len(sys.argv) < 3 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s <user> <pass> <intervalSec=%s> <startMode=%s> <debug=normal>" % (sys.argv[0], intervalSec, startMode))
        sys.exit(-1)

    user     = sys.argv[1]
    password = sys.argv[2]
    
    # pull out arguments
    if len(sys.argv) >= 4:
        intervalSec = int(sys.argv[3])

    if len(sys.argv) >= 5:
        startMode = sys.argv[4]
    
    if len(sys.argv) >= 6:
        debug = (sys.argv[5] != "normal")
        
    # create and run app
    app = App(user, password, intervalSec, startMode, debug)
    app.Run()



Main()












