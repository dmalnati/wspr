#!/usr/bin/python3.5 -u

import os
import sys
from collections import defaultdict 

from libCore import *



db = Database()

def DoScan(dayLookback = 14):
    t   = db.GetTable("WSPR_ALL_BALLOON_TELEMETRY")
    rec = t.GetRecordAccessor()

    # Measure duration of scan
    timeStart = DateTimeNow()
    
    # Search for all callsigns
    callsign__count = defaultdict(int)

    # Examine records within a lookback period
    tatz = TimeAndTimeZone()
    now = tatz.Now()
    timeThreshold = now - datetime.timedelta(days=dayLookback)

    rec.Reset()
    while rec.ReadPrevInLinearScan():
        recTime = tatz.ParseAndGetTimeNativeInTimeZone(rec.Get("DATE"), "%Y-%m-%d %H:%M", "UTC")

        if recTime >= timeThreshold:
            callsign = rec.Get("CALLSIGN")

            callsign__count[callsign] += 1
        else:
            break
    
    # Determine which are telemetry callsigns
    countSeen   = 0
    countInScan = 0
    id__count = defaultdict(int)
    for callsign in callsign__count.keys():
        count = callsign__count[callsign]
        
        countSeen += count
        
        c1 = callsign[0]
        c3 = callsign[2]

        if (c1 == "0" or c1 == "1" or c1 == "Q") and c3.isnumeric():
            countInScan += count
            
            id = c1 + c3
            
            id__count[id] += count

            
    timeEnd = DateTimeNow()
    secDiff = DateTimeStrDiffSec(timeEnd, timeStart)
    
    # Display
    idList = sorted(id__count.keys())

    print("Records : %9s" % (Commas(t.Count())))
    print("Examined: %9s" % (Commas(countSeen)))
    print("Ballon  : %9s" % (Commas(countInScan)))
    print("%s sec scan" % secDiff)
    print()

    for id0 in ['0', '1', 'Q']:
        for id1 in range(10):
            id = id0 + str(id1)
            
            print("%s - %5s" % (id, Commas(id__count[id])))


def Main():
    dayLookback = 14

    if (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s <dayLookback=%s>" % (sys.argv[0], dayLookback))
        sys.exit(-1)

    if len(sys.argv) == 2:
        dayLookback = int(sys.argv[1])

    print("Day Lookback: {}".format(dayLookback))
    
    # Access database
    if db.Connect():
        DoScan(dayLookback)
    else:
        print("Could not connected to Database")
    
    
Main()













