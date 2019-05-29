#!/usr/bin/python -u

import os
import subprocess
import time
import sys

from libCore import *


class App(WSApp):
    def __init__(self, intervalSec):
        WSApp.__init__(self)

        self.intervalSec = intervalSec
        
        # get handles to database
        self.db = ManagedDatabase(self)

    def Run(self):
        Log("Waiting for Database Available to begin")
        Log("")
        
        self.db.SetCbOnDatabaseStateChange(self.OnDatabaseStateChange)
        
        evm_MainLoop()

    def OnDatabaseAvaiable(self):
        Log("Database Available, starting")

        self.td        = self.db.GetTable("DOWNLOAD")
        self.rowIdLast = self.td.GetHighestRowId() - 20
        
        evm_SetTimeout(self.OnTimeout, 0)


    def OnDatabaseClosing(self):
        Log("Database Closing, exiting")
        
    def OnDatabaseStateChange(self, dbState):
        if dbState == "DATABASE_AVAILABLE":
            self.OnDatabaseAvaiable()
        if dbState == "DATABASE_CLOSING":
            self.OnDatabaseClosing()

    def CheckForUpdates(self):
        # Prepare to walk records
        recTd = self.td.GetRecordAccessor()
        recTd.SetRowId(self.rowIdLast)
        
        # Walk list of records starting from last seen
        while recTd.ReadNextInLinearScan():
            #recTd.DumpVertical(Log)
            recTd.DumpHorizontal(8, Log)
        
        self.rowIdLast = recTd.GetRowId()
    
    def OnTimeout(self):
        self.CheckForUpdates()
        
        timeoutMs = self.intervalSec * 1000
        
        evm_SetTimeout(self.OnTimeout, timeoutMs)

    
    

def Main():
    # default arguments
    intervalSec = 1

    if len(sys.argv) > 2 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s <intervalSec=%s>" % (sys.argv[0], intervalSec))
        sys.exit(-1)

    # pull out arguments
    if len(sys.argv) >= 2:
        intervalSec = int(sys.argv[1])
        
    # create and run app
    app = App(intervalSec)
    app.Run()



Main()












