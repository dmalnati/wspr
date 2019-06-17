#!/usr/bin/python3.5 -u

import os
import sys

from libWSPRUploader import *


def Main():
    retVal = 0

    if len(sys.argv) != 14 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s <debug0or1> wsjt <myCall> <myGrid> <hhmm> <db> <dt> <freq> <drift> <callsign> <grid> <dBm> <km>" % sys.argv[0])
        print("Usage: %s <debug0or1> direct <rCallsign> <rGrid> <yymmdd> <hhmm> <db> <dt> <freq> <callsign> <grid> <pwrdbm> <drift>" % sys.argv[0])
        sys.exit(-1)

    # upload
    debug = sys.argv[1] != "0"
    dataType = sys.argv[2]

    if dataType == "wsjt":
        uploader = WSPRUploader(debug)
        retVal = uploader.UploadWSJT(sys.argv[3:])
    elif dataType == "direct":
        uploader = WSPRUploader(debug)
        retVal = uploader.UploadDirect(*sys.argv[3:])
    else:
        retVal = 0
        print("Unknown dataType: %s" % dataType)

    print(retVal)

    return (retVal == 0)


exit(Main())












