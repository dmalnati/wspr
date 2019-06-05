#!/usr/bin/python -u

import os
import subprocess
import time
import sys

from libCore import *

from libWSPRUploader import *



class App(WSApp):
    def __init__(self, intervalSec, startMode, debug):
        WSApp.__init__(self)

        # Basic object configuration
        self.service     = self.GetSelfServiceName()
        self.intervalSec = intervalSec
        self.startMode   = startMode
        self.debug       = debug

        Log("Configured for:")
        Log("  service     = %s" % self.service)
        Log("  debug       = %s" % self.debug)
        Log("  intervalSec = %s" % self.intervalSec)
        Log("  startMode   = %s" % self.startMode)
        Log("")
        
        # get handles to database
        self.db  = ManagedDatabase(self)
        
        self.wsprUploader = WSPRUploader(self.debug)


    def Run(self):
        Log("Waiting for Database Available to begin")
        Log("")
        
        self.db.SetCbOnDatabaseStateChange(self.OnDatabaseStateChange)
        
        evm_MainLoop()


    def OnDatabaseAvaiable(self):
        Log("Database Available, starting")

        self.tWd = self.db.GetTable("WSPR_DECODED")
        self.tnv = self.db.GetTable("NAME_VALUE")
        
        # handle cold start
        if self.startMode == "cold":
            rowIdLast = self.GetLast()
            
            Log("    Resetting last processed to -1 from %s" % rowIdLast)
            Log("")
            
            self.SetLast(-1)

        evm_SetTimeout(self.OnTimeout, 0)

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

    # Period 2019-06-04 13:54 complete, processing uploads
    #    +ALTITUDE_FT     : 10000
    #     CALLSIGN        : Q42SNP
    #    +CALLSIGN_DECODED: KD2KDD
    #     DATE            : 2019-06-04 13:54
    #     DBM             : +17
    #     DRIFT           : 0
    #     FREQUENCY       : 14.097005
    #     GRID            : FN71
    #    +GRID_DECODED    : FN71SN
    #    +ID              : 1574
    #     KM              : 2038
    #     MI              : 1266
    #     REPORTER        : WD4AH
    #     RGRID           : EL89rt
    #     SNR             : -11
    #    +SPEED_MPH       : 18
    #    +TEMPERATURE_C   : 0
    #    +VOLTAGE         : 1500
    #     WATTS           : 0.050 
    def OnUpdate(self, rec):
        
        def GetYYMMDD(wsprDate):
            return wsprDate[2:4] + wsprDate[5:7] + wsprDate[8:10]
        
        def GetHHMM(wsprDate):
            return "".join(wsprDate.split()[1].split(":"))
        
        # Fill out upload parameters
        rCallsign = rec.Get("REPORTER")
        rGrid     = rec.Get("RGRID")
        yymmdd    = GetYYMMDD(rec.Get("DATE"))
        hhmm      = GetHHMM(rec.Get("DATE"))
        db        = rec.Get("SNR")  ; # the + prefix is fine
        dt        = "0"
        freq      = rec.Get("FREQUENCY")
        callsign  = rec.Get("CALLSIGN_DECODED")
        grid      = rec.Get("GRID_DECODED")
        pwrdbm    = rec.Get("DBM")  ; # the + prefix is fine
        drift     = rec.Get("DRIFT")
        
        # upload
        Log("Uploading rec:")
        rec.DumpVertical(Log)
        
        uploadCount = \
            self.wsprUploader.UploadDirect(rCallsign,
                                           rGrid,
                                           yymmdd,
                                           hhmm,
                                           db,
                                           dt,
                                           freq,
                                           callsign,
                                           grid,
                                           pwrdbm,
                                           drift)
        
        return uploadCount
        
        
    def Process(self):
        Log("Scanning WSPR_DECODED for new spots")
        
        # Prepare to walk records
        rec = self.tWd.GetRecordAccessor()
        rec.SetRowId(self.GetLast())
        
        Log("  Starting from rowid %s" % rec.GetRowId())
        rowIdStart = rec.GetRowId()
        
        # Walk list of records starting from last seen
        count = 0
        uploadCountTotal = 0
        timeStart = DateTimeNow()
        while rec.ReadNextInLinearScan():
            count += 1
            uploadCountTotal += self.OnUpdate(rec)
            self.SetLast(rec.GetRowId())
        
        timeEnd = DateTimeNow()
        secDiff = DateTimeStrDiffSec(timeEnd, timeStart)
        
        Log("  Scan took %s sec" % Commas(secDiff))
        Log("  Saw %s new records" % Commas(count))
        Log("  Success in uploading %s" % Commas(uploadCountTotal))
        
        rowIdEnd = rec.GetRowId()
        Log("  Saving %s as last rowid seen" % rowIdEnd)
        
            
    
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
    if len(sys.argv) < 4 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s <intervalSec> <startMode> <debug>" % (sys.argv[0]))
        sys.exit(-1)

    intervalSec = int(sys.argv[1])
    startMode   = sys.argv[2]
    debug       = (sys.argv[3] != "normal")
        
    # create and run app
    app = App(intervalSec, startMode, debug)
    app.Run()



Main()












