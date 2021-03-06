#!/usr/bin/python3.5 -u

import os
import subprocess
import time
import sys

from libCore import *


class App(WSApp):
    def __init__(self, hoursToKeep, intervalSec, batchSize, firstBatchSize):
        WSApp.__init__(self)
        
        self.hoursToKeep         = hoursToKeep
        self.intervalSec         = intervalSec
        self.batchSize           = firstBatchSize
        self.subsequentBatchSize = batchSize
        
        Log("Configured for:")
        Log("  hoursToKeep = %s" % self.hoursToKeep)
        Log("  intervalSec = %s" % self.intervalSec)
        Log("  batchSize   = %s" % self.batchSize)
        Log("")
        
        self.db = ManagedDatabase(self)

        
    def Run(self):
        Log("Waiting for Database Available to begin")
        Log("")
        
        self.db.SetCbOnDatabaseStateChange(self.OnDatabaseStateChange)
        
        evm_MainLoop()

        
    def OnDatabaseAvaiable(self):
        Log("Database Available, starting")
        self.t = self.db.GetTable("WSPR_DOWNLOAD")
        
        evm_SetTimeout(self.OnTimeout, 0)

    def OnDatabaseClosing(self):
        Log("Database Closing, no action taken")
        
    def OnDatabaseStateChange(self, dbState):
        if dbState == "DATABASE_AVAILABLE":
            self.OnDatabaseAvaiable()
        if dbState == "DATABASE_CLOSING":
            self.OnDatabaseClosing()


    def GetDataAtUrl(self, url, timeoutSecs = 60, retries = 1):
        byteList = bytearray()
        
        try:
            # -t retries
            # -T timeout on all of:
            #   DNS
            #   Connection (waiting to connect via TCP)
            #   Idle during download (duration between bytes)
            #
            # Unfortunately can't find a way to have it give up if the total
            # duration of the download exceeds a limit.  A wrapper may be
            # necessary if becomes problematic.
            byteList = subprocess.check_output(['wget', '-t', str(retries), '-T', str(timeoutSecs), '-qO-', url])
        except Exception as e:
            Log("Could not download url (%s): %s" % (url, e))
        
        return byteList
        
    def MakeWSPRUrl(self, limit):
        url  = "http://wsprnet.org/olddb"
        url += "?mode=html"
        url += "&band=20"
        url += "&limit=%i" % (limit)
        url += "&findcall="
        url += "&findreporter="
        url += "&sort=date"

        return url

    # https://repl.it/@nickangtc/python-strip-non-ascii-characters-from-string
    def strip_non_ascii(self, string):
            ''' Returns the string without non ASCII characters'''
            stripped = (c for c in string if 0 < ord(c) < 127)
            return ''.join(stripped)
            
        
    def ParseAndStoreWsprSpotFromOldDatabaseHtml(self, byteList):
        rowList = self.Parse(byteList)
        self.Store(rowList)
        
        
    def Parse(self, byteList):
        rowList = []
        
        Log("Parsing downloaded file")
        timeStart = DateTimeNow()
        
        lineList = byteList.decode().splitlines()
        
        for line in lineList:
            if line.find("&nbsp;") != -1:
                linePartList = line.split("&nbsp;")
                
                row = linePartList[1::2]
                
                rowList.append(row)
                
        
        # put in chronological order
        rowList = rowList[::-1]
        
        timeEnd = DateTimeNow()
        secDiff = DateTimeStrDiffSec(timeEnd, timeStart)
        
        recPerSecStr = "inf"
        if secDiff != 0:
            recPerSecStr = Commas(len(rowList) // secDiff)
        
        Log("  Parsing took %s seconds" % secDiff)
        Log("  %s Records downloaded (%s rec/sec)" % (Commas(len(rowList)), recPerSecStr))
        Log("")
        
        return rowList
    
    
    def Store(self, rowList):
        rec = self.t.GetRecordAccessor()
        
        Log("Local cache starting count: %s" % Commas(self.t.Count()))
        Log("")
        
        # wipe out all the old records
        ONE_HOUR_IN_SECONDS = 60 * 60
        durationToKeepInSeconds = ONE_HOUR_IN_SECONDS * self.hoursToKeep
        Log("Removing records older than %s hour(s)" % self.hoursToKeep)

        timeStart = DateTimeNow()
        timeNow = timeStart
        deleteCount = self.t.DeleteOlderThan(durationToKeepInSeconds)
        timeEnd = DateTimeNow()
        secDiff = DateTimeStrDiffSec(timeEnd, timeStart)
        
        Log("Deleted %s records" % Commas(deleteCount))
        Log("  Removing took %s seconds" % secDiff)
        Log("")
        
        # add new records
        Log("Updating with new records")
        timeStart = DateTimeNow();
        
        self.db.BatchBegin()
        
        rec.Reset()
        insertCount = 0
        for row in rowList:
            # Get all the spots
            # table 3
            #
            # the first two rows are headers
            # after that it's data
            #
            # 12 columns of data (ignore the goofy double header rows)
            #                                                         Power,       Reported,     Distance
            # Date,             Call,  Frequency, SNR, Drift, Grid,   dBm, W,     by,   loc,    km,   mi
            # 2019-05-11 23:58, W6LVP, 7.040035,  -28, 0,     DM04li, +37, 5.012, K2JY, EM40xa, 2762, 1716
            # ...
            #
            
            valList = row
            
            doInsert = False
            try:
                rec.Set("DATE",      valList[0])
                rec.Set("CALLSIGN",  valList[1])
                rec.Set("FREQUENCY", valList[2])
                rec.Set("SNR",       valList[3])
                rec.Set("DRIFT",     valList[4])
                rec.Set("GRID",      valList[5])
                rec.Set("DBM",       valList[6])
                rec.Set("WATTS",     valList[7])
                rec.Set("REPORTER",  valList[8])
                rec.Set("RGRID",     valList[9])
                rec.Set("KM",        valList[10])
                rec.Set("MI",        valList[11])
                
                doInsert = True
            except Exception as e:
                Log("ERR: Unable to populate record: %s" % e)
                Log("ERR: Row: \"%s\"" % row)
            
            if doInsert:
                if rec.Insert():
                    insertCount += 1
        
        self.db.BatchEnd()
        
        timeEnd = DateTimeNow()
        secDiff = DateTimeStrDiffSec(timeEnd, timeStart)
        
        Log("Inserted %s records" % Commas(insertCount))
        Log("  Inserting took %s seconds" % secDiff)
        
        Log("")
        Log("Local cache ending count: %s" % Commas(self.t.Count()))
        Log("")
        
        
    def file_get_contents(self, filename):
        with open(filename) as f:
            return f.read()


    def Download(self):
        url = self.MakeWSPRUrl(self.batchSize)

        Log("")
        Log("")
        Log("#################################################")
        Log("#")
        Log("#  Next Download")
        Log("#")
        Log("#################################################")
        Log("")
        
        Log("Downloading latest %s spots from WSPRnet" % Commas(self.batchSize))
        timeStart = DateTimeNow()
        byteList = self.GetDataAtUrl(url)
        #byteList = self.file_get_contents("old.huge.html")
        #byteList = self.file_get_contents("testInputMineFull.txt")
        timeEnd = DateTimeNow()
        secDiff = DateTimeStrDiffSec(timeEnd, timeStart)
        Log("  Download took %i seconds -- %s bytes" % (secDiff, Commas(len(byteList))))
        Log("")
        
        if len(byteList):
            Log("Parsing data")
            self.ParseAndStoreWsprSpotFromOldDatabaseHtml(byteList)
        else:
            Log("No data to parse")
        
        #exit()
    
    
    def OnTimeout(self):
        timeStart = DateTimeNow()
        self.Download()
        timeEnd = DateTimeNow()
        
        secDiff = DateTimeStrDiffSec(timeEnd, timeStart)
        
        # schedule next download
        timeoutMs = 0
        if self.intervalSec > secDiff:
            timeoutMs = (self.intervalSec - secDiff) * 1000
        
        Log("Scheduling next wakeup")
        Log("  Processing took %s sec"  % secDiff)
        Log("  Interval %s sec" % self.intervalSec)
        Log("  Waking again in %s sec" % (timeoutMs // 1000))
        Log("")
        
        self.batchSize = self.subsequentBatchSize

        evm_SetTimeout(self.OnTimeout, timeoutMs)

    
    

def Main():
    LogIncludeDate(True)
    
    # default arguments
    hoursToKeep    = 24
    intervalSec    = 30
    batchSize      = 2000
    firstBatchSize = 50000

    if len(sys.argv) > 4 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s <hoursToKeep=%s> <intervalSec=%s> <batchSize=%s> <firstBatchSize=%s>" % (sys.argv[0], hoursToKeep, intervalSec, batchSize, firstBatchSize))
        sys.exit(-1)

    # pull out arguments
    if len(sys.argv) >= 2:
        hoursToKeep = int(sys.argv[1])
        
    if len(sys.argv) >= 3:
        intervalSec = int(sys.argv[2])
    
    if len(sys.argv) >= 4:
        batchSize = int(sys.argv[3])
    
    if len(sys.argv) >= 5:
        batchSize = int(sys.argv[4])
    
    # create and run app
    app = App(hoursToKeep, intervalSec, batchSize, firstBatchSize)
    app.Run()



Main()












