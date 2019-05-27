import os
import subprocess
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *


class APRSUploader:
    def __init__(self, user, password, debug = False):
        self.user     = user
        self.password = password
        
        self.debug = debug
        
    def Upload(self, aprsMsg):
        loginStr = "user %s pass %s vers TestSoftware 1.0" % (self.user, self.password)

        postData      = str(loginStr) + "\n" + str(aprsMsg)
        contentLength = len(postData)
        
        url = "http://rotate.aprs.net:8080"
        
        procAndArgs = [
            'curl', \
            '-k', \
            '-i', \
            '-w', \
            '-L', \
            '-s', \
            '-X', 'POST', \
            '-H', 'Accept-Type: text/plain', \
            '-H', 'Content-Type: application/octet-stream', \
            '-H', 'Content-Length: ' + str(contentLength), \
            '-d', postData, \
            url \
        ]
        
        #Log(" ".join(procAndArgs))
        retVal = False
        try:
            if not self.debug:
                byteList = subprocess.check_output(procAndArgs)
                #Log("ret: " + str(byteList))
            
            retVal = True
        except:
            pass

        return retVal







