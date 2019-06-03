#!/usr/bin/python -u

import os
import subprocess
import time
import sys

from libCore import *

from libWSPRDecoder import *


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


    def Run(self):
        Log("Waiting for Database Available to begin")
        Log("")
        
        self.db.SetCbOnDatabaseStateChange(self.OnDatabaseStateChange)
        
        evm_MainLoop()


    def OnDatabaseAvaiable(self):
        Log("Database Available, starting")

        self.tDl      = self.db.GetTable("WSPR_DOWNLOAD")
        self.tnv      = self.db.GetTable("NAME_VALUE")
        self.tAll     = self.db.GetTable("WSPR_ALL_BALLOON_TELEMETRY")
        self.tDecoded = self.db.GetTable("WSPR_DECODED")

        # get decoder
        self.wsprDecoder = WSPRDecoder()
        
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

    def OnUpdate(self, rec):
        # unpack records
        name__value = rec.GetDict()

        callsign = name__value["CALLSIGN"]

        # check if balloon telemetry and store if yes
        if callsign[0] == "Q" or callsign[0] == "0":
            recAll = self.tAll.GetRecordAccessor()
            recAll.CopyIntersection(rec)
            if not self.debug:
                recAll.Insert()
            else:
                Log("Debug -- would have stored balloon telemetry:")
                recAll.DumpVertical(Log)

        # check if decodable, store if yes
        if self.wsprDecoder.CanBeDecoded(name__value):
            name__value_decoded = self.wsprDecoder.Decode(name__value)

            recDecoded = self.tDecoded.GetRecordAccessor()
            recDecoded.CopyDictIntersection(name__value_decoded)

            if not self.debug:
                retInsert = recDecoded.Insert()

                if retInsert:
                    Log("Stored decoded telemetry:")
                    recDecoded.DumpVertical(Log)
            else:
                Log("Debug -- would have stored decoded telemetry:")
                recDecoded.DumpVertical(Log)


    def Process(self):
        Log("Scanning WSPR_DOWNLOAD for new spots")
        
        # Prepare to walk records
        rec = self.tDl.GetRecordAccessor()
        rec.SetRowId(self.GetLast())
        
        Log("  Starting from rowid %s" % rec.GetRowId())
        
        # Walk list of records starting from last seen
        count = 0
        timeStart = DateTimeNow()
        while rec.ReadNextInLinearScan():
            count += 1
            self.OnUpdate(rec)
        
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

    if len(sys.argv) < 1 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s <intervalSec=%s> <startMode=%s> <debug=normal>" % (sys.argv[0], intervalSec, startMode))
        sys.exit(-1)

    # pull out arguments
    if len(sys.argv) >= 2:
        intervalSec = int(sys.argv[1])

    if len(sys.argv) >= 3:
        startMode = sys.argv[2]
    
    if len(sys.argv) >= 4:
        debug = (sys.argv[3] != "normal")
        
    # create and run app
    app = App(intervalSec, startMode, debug)
    app.Run()



Main()












