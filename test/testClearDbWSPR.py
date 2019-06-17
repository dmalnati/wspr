#!/usr/bin/python3.5 -u

import os
import sys

from libCore import *

def Run(db, callsign):
    t   = db.GetTable("DOWNLOAD")
    rec = t.GetRecordAccessor()

    timeStart = DateTimeNow()
    
    # Process each line as a record
    timeStart = DateTimeNow()

    db.BatchBegin()

    countSeen   = 0
    countDelete = 0
    while rec.ReadNextInLinearScan():
        countSeen += 1

        if callsign == "*" or callsign == rec.Get("CALLSIGN"):
            countDelete += 1
            rec.Delete()
    
    db.BatchEnd()
    
    timeEnd = DateTimeNow()
    secDiff = DateTimeStrDiffSec(timeEnd, timeStart)

    print("%s / %s deleted in %s sec" % (countDelete, countSeen, secDiff))

def Main():
    if len(sys.argv) != 2 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s <callsign>" % (sys.argv[0]))
        sys.exit(-1)

    callsign = sys.argv[1]
    
    # Access database
    db  = Database()
    if db.Connect():
        Run(db, callsign)
    else:
        print("Could not connect to the database")
    
    
Main()













