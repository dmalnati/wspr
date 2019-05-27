#!/usr/bin/python -u

import os
import sys

from libAPRSUploader import *

def Main():
    retVal = 0

    count    = 1
    delaySec = 1

    if len(sys.argv) < 4 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s <user> <pass> <msg> <count=%s> <delaySec=%s>" % (sys.argv[0], count, delaySec))
        sys.exit(-1)

    # pull out arguments
    user     = sys.argv[1]
    password = sys.argv[2]
    msg      = sys.argv[3]

    if len(sys.argv) >= 5:
        count = int(sys.argv[4])
    if len(sys.argv) >= 6:
        delaySec = int(sys.argv[5])
        
    # upload
    uploader = APRSUploader(user, password)

    remaining = count
    while remaining:
        # retVal of 0 for unix program means all ok
        retVal = uploader.Upload(msg) == False

        remaining -= 1

        if remaining:
            time.sleep(delaySec)

    return retVal

exit(Main())












