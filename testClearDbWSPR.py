#!/usr/bin/python -u

import os
import sys

from libDbWSPR import *


def Main():
    if len(sys.argv) != 2 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s <callsign>" % (sys.argv[0]))
        sys.exit(-1)

    callsign = sys.argv[1]
    
    # Access database
    db  = DatabaseWSPR()
    t   = db.GetTableDownload()
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
    
    
Main()













