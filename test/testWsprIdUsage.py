#!/usr/bin/python -u

import os
import sys

from libDbWSPR import *


def Main():
    # Access database
    db  = DatabaseWSPR()
    t   = db.GetTableDownload()
    rec = t.GetRecordAccessor()

    # Search for all callsigns
    timeStart = DateTimeNow()
    
    callsign__count = t.Distinct("CALLSIGN")
    
    # Determine which are telemetry callsigns
    countSeen   = 0
    countInScan = 0
    id__count = dict()
    for callsign in callsign__count.keys():
        count = callsign__count[callsign]
        
        countSeen += count
        
        c1 = callsign[0]
        c3 = callsign[2]

        if (c1 == "0" or c1 == "Q") and c3.isnumeric():
            countInScan += count
            
            id = c1 + c3
            
            if id not in id__count:
                id__count[id] = 0
            
            id__count[id] += count

            
    timeEnd = DateTimeNow()
    secDiff = DateTimeStrDiffSec(timeEnd, timeStart)
    
    # Display
    idList = id__count.keys()
    idList.sort()

    print("%s sec scan" % secDiff)
    print("%s / %s in scan" % (Commas(countInScan), Commas(countSeen)))
    for id in idList:
        print("%s - %5s" % (id, Commas(id__count[id])))
    
    
Main()













