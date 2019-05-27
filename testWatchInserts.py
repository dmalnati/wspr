#!/usr/bin/python -u

import os
import subprocess
import time
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *

from libDbWSPR import *


class App:
    def __init__(self, intervalSec):
        self.intervalSec = intervalSec
        
        # get handles to database
        self.db  = DatabaseWSPR()
        self.td  = self.db.GetTableDownload()

        self.rowIdLast = self.td.GetHighestRowId() - 20
        
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
        
    
    def Run(self):
        def OnStdIn(inputStr):
            inputStr = inputStr.strip()

            if inputStr != "":
                self.OnKeyboardReadable(inputStr)
            
        WatchStdinEndLoopOnEOF(OnStdIn, binary=True)

        evm_SetTimeout(self.OnTimeout, 0)
        
        evm_MainLoop()

    
    

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












