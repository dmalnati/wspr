#!/usr/bin/python -u

import os
import subprocess
import time
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *

from libDbWSPR import *
from libWsprToAprsBridge import *


class App:
    def __init__(self, user, password, intervalSec, startMode, debug):
        # Basic object configuration
        self.intervalSec = intervalSec
        
        Log("Configured for:")
        Log("  debug       = %s" % debug)
        Log("  user        = %s" % user)
        Log("  password    = %s" % password)
        Log("  intervalSec = %s" % intervalSec)
        Log("  startMode   = %s" % startMode)
        Log("")
        
        # get handles to database
        self.db  = DatabaseWSPR()
        self.td  = self.db.GetTableDownload()
        self.tnv = self.db.GetTableNameValue()
        
        # get bridge
        self.bridge = WsprToAprsBridge(user, password, debug)
        
        # handle cold start
        if startMode == "cold":
            rowIdLast = self.GetLast()
            
            Log("    Resetting last processed to -1 from %s" % rowIdLast)
            Log("")
            
            self.SetLast(-1)
        
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
        
    def OnStdIn(self, str):
        pass
        
    def Run(self):
        def OnStdIn(inputStr):
            inputStr = inputStr.strip()

            if inputStr != "":
                self.OnKeyboardReadable(inputStr)
            
        WatchStdinEndLoopOnEOF(OnStdIn, binary=True)

        evm_SetTimeout(self.OnTimeout, 0)
        
        self.bridge.Start()
        
        Log("Running")
        Log("")
        
        evm_MainLoop()

    
    

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












