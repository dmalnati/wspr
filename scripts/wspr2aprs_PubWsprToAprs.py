#!/usr/bin/python -u

import os
import subprocess
import time
import sys

from libCore import *

from libWsprToAprsBridge import *


class App(WSApp):
    def __init__(self, user, password, intervalSec, startMode, debug):
        WSApp.__init__(self)

        # Basic object configuration
        self.user        = user
        self.password    = password
        self.intervalSec = intervalSec
        self.startMode   = startMode
        self.debug       = debug

        Log("Configured for:")
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

        self.td  = self.db.GetTable("DOWNLOAD")
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
        if self.tnv.Count() == 0:
            rec.Set("NAME", "LAST_PROCESSED")
            rec.Set("VALUE", "-1")
            rec.Insert()
        
        rec.Set("NAME", "LAST_PROCESSED")
        rec.Read()
        retVal = int(rec.Get("VALUE"))
        
        return retVal
        
    def SetLast(self, rowid):
        rec = self.tnv.GetRecordAccessor()
        
        rec.Set("NAME", "LAST_PROCESSED")
        rec.Read()
        rec.Set("VALUE", str(rowid))
        
        retVal = rec.Update()
        
        return retVal

    def OnUpdate(self, recTd):
        # unpack records
        name__value = recTd.GetDict()
        
        # send to bridge
        self.bridge.OnUpdate(name__value)

    def Process(self):
        Log("Scanning DOWNLOAD for new spots")
        
        # Prepare to walk records
        recTd = self.td.GetRecordAccessor()
        recTd.SetRowId(self.GetLast())
        
        Log("  Starting from rowid %s" % recTd.GetRowId())
        
        # Walk list of records starting from last seen
        count = 0
        timeStart = DateTimeNow()
        while recTd.ReadNextInLinearScan():
            count += 1
            self.OnUpdate(recTd)
        
        timeEnd = DateTimeNow()
        secDiff = DateTimeStrDiffSec(timeEnd, timeStart)
        
        Log("  Scan took %s sec" % Commas(secDiff))
        Log("  Saw %s new records" % Commas(count))
        
        if count != 0:
            rowId = recTd.GetRowId()
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












