#!/usr/bin/python -u

import os
import sys

from libDbWSPR import *


def MMSSToWsprDate(val):
    return DateNow() + " " + val[0:2] + ":" + val[2:4]

def KmToMi(val):
    return str(int(float(val) / 1.609))

def PowerWattsToPowerDbm(powerWatts):
    powerWatts__powerDbm = [
        ( 0.001,  0 ),
        ( 0.002,  3 ),
        ( 0.005,  7 ),
        ( 0.01 , 10 ),
        ( 0.02 , 13 ),
        ( 0.05 , 17 ),
        ( 0.1  , 20 ),
        ( 0.2  , 23 ),
        ( 0.5  , 27 ),
        ( 1    , 30 ),
        ( 2    , 33 ),
        ( 5    , 37 ),
        ( 10   , 40 ),
        ( 20   , 43 ),
        ( 50   , 47 ),
        ( 100  , 50 ),
        ( 200  , 53 ),
        ( 500  , 57 ),
        ( 1000 , 60 )
    ]
    
    retVal = 0
    if powerWatts in powerWatts__powerDbm:
        retVal = powerWatts__powerDbm[powerWatts]
    
    if retVal != 0:
        retVal = "+" + str(retVal)
    
    return str(retVal)

def PowerDbmToPowerWatts(powerDbm):
    powerDbm__powerWatts = [
        (  0,  0.001 ),
        (  3,  0.002 ),
        (  7,  0.005 ),
        ( 10,  0.01  ),
        ( 13,  0.02  ),
        ( 17,  0.05  ),
        ( 20,  0.1   ),
        ( 23,  0.2   ),
        ( 27,  0.5   ),
        ( 30,  1     ),
        ( 33,  2     ),
        ( 37,  5     ),
        ( 40,  10    ),
        ( 43,  20    ),
        ( 47,  50    ),
        ( 50,  100   ),
        ( 53,  200   ),
        ( 57,  500   ),
        ( 60,  1000  )
    ]
    
    retVal = 0
    if powerDbm in powerDbm__powerWatts:
        retVal = powerDbm__powerWatts[powerWatts]
    
    return str(retVal)
    

def Main():
    if (len(sys.argv) != 2 and len(sys.argv) != 14 and len(sys.argv) != 12 and len(sys.argv) != 10)  or \
       (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage:")
        print("  %s <spotFileAnySource.txt>" % (sys.argv[0]))
        print("  %s // then fields from any 3 formats as individual arguments" % (sys.argv[0]))
        sys.exit(-1)

    # pull out arguments
    lineList = []
    if len(sys.argv) == 2:
        spotFile = sys.argv[1]
        
        # Parse file contents
        byteList = []
        with open(spotFile) as f:
            byteList = f.read()
            
        lineList = sorted(byteList.split("\n"))
    else:
        lineList = [ " ".join(sys.argv[1:]) ]
    
    # Access database
    db  = DatabaseWSPR()
    t   = db.GetTableDownload()
    rec = t.GetRecordAccessor()

    timeStart = DateTimeNow()
    
    blankLineCount = 0
    badLineCount   = 0
    goodLineCount  = 0
    insertCount    = 0
    
    # Process each line as a record
    db.BatchBegin()
    
    for line in lineList:
        if len(line):
            linePartList = line.split()
            
            valList = []
            
            recOk = True
            if len(linePartList) == 13:
                # this is a copy/paste from the olddb on wsprnet
                goodLineCount += 1
                
                # need to combine the first two whitespace separated columns because
                # they together constitute the first field
                valList.append(linePartList[0] + " " + linePartList[1])
                valList.extend(linePartList[2:])
                
                # store in database
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
                
            elif len(linePartList) == 11:
                goodLineCount += 1
                # this is a copy/paste from the new database on wsprnet
                
                #      0              1           2           3     4      5      6         7          8         9       10
                # Timestamp          Call        MHz         SNR  Drift  Grid    Pwr     Reporter    RGrid       km      az
                # 2019-05-10 22:10 	 KD2KDD 	 14.097113 	 -16 	 1 	 GL18 	 0.1 	 VE3ZLB 	 EN96mn 	 2892 	 321 
                # 2019-05-10 20:34 	 KD2KDD 	 14.097022 	 -18 	 0 	 GL18 	 0.1 	 2E0PYB 	 JO01is 	 5374 	 44
                
                # need to combine the first two whitespace separated columns because
                # they together constitute the first field
                valList.append(linePartList[0] + " " + linePartList[1])
                valList.extend(linePartList[2:])

                rec.Set("DATE",      valList[0])
                rec.Set("CALLSIGN",  valList[1])
                rec.Set("FREQUENCY", valList[2])
                rec.Set("SNR",       valList[3])
                rec.Set("DRIFT",     valList[4])
                rec.Set("GRID",      valList[5])
                rec.Set("DBM",       PowerWattsToPowerDbm(valList[6]))    ;# but in the wrong format, convert in
                rec.Set("WATTS",     valList[6])    ;# equal format
                rec.Set("REPORTER",  valList[7])
                rec.Set("RGRID",     valList[8])
                rec.Set("KM",        valList[9])
                rec.Set("MI",        KmToMi(valList[9]))   ;# need to convert from KM to MI
                
            elif len(linePartList) == 9:
                goodLineCount += 1
                valList.extend(linePartList)
            
                # this is a copy/paste from the WSJT-X
                
                #  0      1    2     3           4     5             6      7     8
                # UTC    dB   DT    Freq       Drift Call          Grid    dBm    km                  
                # 0320   -7   1.0   14.096991    0   QJ1XRV        FN20     20     81
                # 0320   32   1.0   14.097051    0   QJ1XRV        FN20     20     81
                # 0320  -22   1.2   14.097111    0   QJ1XRV        FN20     20     81
                # 0320   18   1.0   14.097171    0   QJ1XRV        FN20     20     81
                
                rec.Set("DATE",      MMSSToWsprDate(valList[0]))    ;# today's date plus that with a colon
                rec.Set("CALLSIGN",  valList[5])
                rec.Set("FREQUENCY", valList[3])
                rec.Set("SNR",       valList[1])
                rec.Set("DRIFT",     valList[4])
                rec.Set("GRID",      valList[6])
                rec.Set("DBM",       "+" + str(valList[7]))    ;# need to add the preceeding +
                rec.Set("WATTS",     PowerDbmToPowerWatts(valList[7]))    ;# need to convert
                rec.Set("REPORTER",  "KD2KDD")    ;# use my callsign KD2KDD
                rec.Set("RGRID",     "FN20")    ;# use my grid FN20
                rec.Set("KM",        valList[8])   
                rec.Set("MI",        KmToMi(valList[8]))    ;# convert
                
                pass
            else:
                recOk = False
                
            if recOk:
                rec.DumpVertical()
                if rec.Insert():
                    insertCount += 1
            
            else:
                badLineCount += 1
        else:
            blankLineCount += 1
        
    db.BatchEnd()
    
    timeEnd = DateTimeNow()
    secDiff = DateTimeStrDiffSec(timeEnd, timeStart)

    if badLineCount:
        print("%s mismatched columns" % badLineCount)
    print("%s / %s inserted in %s sec" % (insertCount, goodLineCount, secDiff))
    
    
Main()













