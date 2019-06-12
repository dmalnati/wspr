import datetime
import os
import subprocess
import sys

from libCore import *


#
# Originally had a script which would periodically post the contents of the file populated
# by WSJT.
#
# Bafflingly the file grew unbounded, and each upload sent the entire file and the webserver
# on the WSPR side had to sift through what was already seen.
#
#
# Script to upload was this:
#
# http://wsprnet.org/automate.txt
# while true;
# do
#     date
#     curl -F allmept=@/cygdrive/c/Users/doug/AppData/Local/WSJT-X/ALL_WSPR.TXT -F call=KD2KDD -F grid=FN20xr http://wsprnet.org/meptspots.php;
#     echo $?
#     sleep 120;
# done


#
# The response from the webserver on the WSPR side would indicate how many of the
# spots in the file were accepted into the database.
#
# This is what was seen after running the above script where I re-uploaded a single spot
# previously uploaded.
#
#
# Tue, Jun  4, 2019 11:53:31 PM
# <html>
# <body>
# <h1>Processing Log Upload</h1><pre>
# 0 out of 1 spot(s) added<br>
# Processing took 116 milliseconds.<br>
# Old database interface is now <a href='olddb'>here</a>.
# </body>
# </html>
# 0





class WSPRUploader:
    def __init__(self, debug = False):
        self.debug  = debug

    def UploadWSJT(self, colList):
        retVal = False
        
        rCallsign        = colList[0]
        rGrid            = colList[1]
        colConvertedList = self.ConvertFromWSJTProgram(colList[2:])
    
        retVal = self.Upload(rCallsign, rGrid, *colConvertedList)
            
        return retVal
        
    
    def UploadDirect(self, rCallsign, rGrid, yymmdd, hhmm, db, dt, freq, callsign, grid, pwrdbm, drift):
        return self.Upload(rCallsign, rGrid, yymmdd, hhmm, db, dt, freq, callsign, grid, pwrdbm, drift)


    # The formats I care about:
    # - WSJT ALL_WSPR.TXT (I want to craft this)
    # - WSJT program
    # - WSPRnet new db [changed mind, don't want]
    # - WSPRnet olddb  [changed mind, don't want]







    # Here are the entries in the ALL_WSPR.TXT file:
    #
    # headers (not listed, I just worked them out with my eyes):
    #    0     1   2  3     4     5            6       7   8       9     10     11  12  13   14
    # YYMMDD HHMM  ?  dB   DT    freq       CALLSIGN GRID PWRDBM    DRIFT cycles?  time_tweaks?
    #
    #
    # 190529 0044   1 -30  0.45  14.0971785  K4COD  EM73  33         0     1   32    3  810  1
    # 190529 1342   2 -25  0.71  14.0970998  KK4WJF EM95  50         0     1    0    1  174  0
    # 190604 0130   3  -7 -3.05  14.0970475  Q02XRT FN20   0         0     1    0    1  810  1
    # 190604 0130   2 -19 -3.01  14.0971675  Q02XRT FN20   0         0   765    0    1 -202  0
    # 190604 0134   4 -14 -1.98  14.0970556  Q02XRT FN20   0         0     1    0    1  629  0
    # 190604 0134   5  -0 -1.94  14.0971757  Q02XRT FN20   0         0     1    0    1  583  0
    # 190604 0138   3 -11 -2.45  14.0970688  Q22XRT FN20   0         0     1    0    1  306  0
    #
    #
    # Further, 
    # An article about hacking and uploading your own file.
    # https://www.qrp-labs.com/images/appnotes/AN002_A4.pdf
    # They mention using this as a template:
    # 161116 0846   9 -23 -0.4  14.097158  CALL LOCATOR 23          0     1    0
    #
    # It's 12 columns.  The data from my file is 15 columns.
    #
    # Perhaps new versions simply add fields to the end of the line.
    #
    #
    #
    # The data returned by the converters below should be of the form:
    #
    # headers (9):
    #
    #    0     1      2    3      4           5       6   7       8
    # YYMMDD HHMM    dB   DT    freq       CALLSIGN GRID PWRDBM  DRIFT
    #







    def GetTodaysYYMMDD(self):
        return datetime.datetime.now().strftime("%y%m%d")




    # Here is data from the WSJT program:
    #
    # headers (9):
    #  0     1    2      3           4      5           6       7      8
    # HHMM  dB   DT     freq       drift callsign     grid     dBm    km 
    #
    # 0130   -7  -3.0   14.097048    0   Q02XRT        FN20      0     81
    # 0130  -19  -3.0   14.097168    0   Q02XRT        FN20      0     81
    # 0134  -14  -2.0   14.097056    0   Q02XRT        FN20      0     81
    # 0134   -0  -1.9   14.097176    0   Q02XRT        FN20      0     81
    # 0138  -11  -2.5   14.097069    0   Q22XRT        FN20      0     81

    def ConvertFromWSJTProgram(self, argList):
        colConvertedList = []
        
        colConvertedList.append(self.GetTodaysYYMMDD()) ;# YYMMDD
        colConvertedList.append(argList[0]) ;# HHMM
        colConvertedList.append(argList[1]) ;# dB
        colConvertedList.append(argList[2]) ;# DT
        colConvertedList.append(argList[3]) ;# freq
        colConvertedList.append(argList[5]) ;# CALLSIGN
        colConvertedList.append(argList[6]) ;# GRID
        colConvertedList.append(argList[7]) ;# PWRDBM
        colConvertedList.append(argList[4]) ;# DRIFT
        
        return colConvertedList
















#
# Notably the curl -F allmept=@<filename> means:
# - do a form post
# - upload the file as an attachment, not simply the contents
#
# The man page says:
#
# -F, --form <name=content>
#
# This  lets curl emulate a filled-in form in which a user
# has pressed the submit button.
# This causes  curl  to  POST  data using  the  Content-Type  multipart/form-data 
# according to RFC 2388.
#
# This enables uploading of binary files etc. To  force  the
# 'content'  part  to  be  a  file, prefix the file name with an @ sign.
#
# To just get the content part from a file, prefix the  file
# name  with  the symbol <.
#
# The difference between @ and < is then that @ makes a file get attached
# in the post as a  file  upload,
# while  the  <  makes  a text field and just get the contents for
# that text field from a file.
#
#


#
# The sent data looks like this:
#
#
# POST / HTTP/1.1
# Host: centcom:8080
# User-Agent: curl/7.59.0
# Accept: */*
# Content-Length: 481
# Content-Type: multipart/form-data; boundary=------------------------d88730e5c67d2cb5
# 
# --------------------------d88730e5c67d2cb5
# Content-Disposition: form-data; name="allmept"; filename="ALL_WSPR.TXT"
# Content-Type: text/plain
# 
# 190529 0044   1 -30  0.45  14.0971785  K4COD EM73 33           0     1   32    3  810  1
# 
# --------------------------d88730e5c67d2cb5
# Content-Disposition: form-data; name="call"
# 
# KD2KDD
# --------------------------d88730e5c67d2cb5
# Content-Disposition: form-data; name="grid"
# 
# FN20xr
# --------------------------d88730e5c67d2cb5--
#
#


# 
# Given the complexity of the above, just make a temporary file and curl it as above instead
# of trying to fake the upload yourself.
#

    
    
    
    
    
    
    
    
    # return number of spots accepted by wspr
    def Upload(self, rCallsign, rGrid, yymmdd, hhmm, db, dt, freq, callsign, grid, pwrdbm, drift):
        retVal = 0
        
        directory = MakeTmpDir()
        
        if directory:
            fName = directory + "/ALL_WSPR.TXT"
            fileExists = True
            try:
                line = "%s %s 1 %s %s %s %s %s %s %s 1 0" % (
                    yymmdd, hhmm, db, dt, freq, callsign, grid, pwrdbm, drift
                )
                
                fd = open(fName, "w")
                fd.write(line)
                fd.write("\n")
                fd.close()
                
                if self.debug:
                    print("Line created: %s" % line)
                
            except:
                fileExists = False
        
            if fileExists:
                retVal = self.Curl(fName, rCallsign, rGrid)
                
            else:
                if self.debug:
                    print("Could not create ALL_WSPR.TXT")
        
            RemoveDir(directory)
        
        else:
            if self.debug:
                print("Could not create temporary directory")

        return retVal
        
    # return number of spots accepted by wspr
    def Curl(self, fName, call, grid):
        retVal = 0
        
        cmd  = "curl -s "
        cmd += "-F allmept=@%s " % fName
        cmd += "-F call=%s " % call
        cmd += "-F grid=%s http://wsprnet.org/meptspots.php" % grid

        if self.debug:
            print("cmd: %s" % cmd)

        try:
            if not self.debug:
                # invoke command, capture output to look for upload count
                byteList = subprocess.check_output(cmd.split())
                
                # extract upload count
                match = re.search(r"([0123456789]*) out of ", byteList.decode())
                uploadCount = 0
                if match:
                    matchStr = match.groups()[0]
                    try:
                        uploadCount = int(matchStr)
                    except Exception as e:
                        Log("Could not parse WSPR upload count: %s" % e)
                        log(matchStr)
                
                retVal = uploadCount
                
            else:
                print("not uploading due to debug mode")
        except:
            pass

        return retVal

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        


    # WSPRnet new db
    #
    # headers (12)
    #
    #   0           1         2             3           4      5         6         7            8           9           10       11
    #  date        time      Call           MHz        SNR    Drift     Grid       Pwr       Reporter     RGrid         km       az
    #  2019-06-05 12:58      QK0FAV      14.097171      -19      0      EG72      0.002      DK6UG        JN49cm      12519      45
    #  2019-06-05 12:36      Q10ZNX      21.096178      -14      0      AD52      501        KA3JIJ       EM84cj      12909      66
    #  2019-06-05 08:06      QY7WAI      7.040152       -26      0      HB78      0.002      DK8JP/2      JO31gk      13897      23
    #  2019-06-05 08:02      QJ1KDS      7.040134       -31      0      NK25      20         G8CQX        IO81xu       8457     321
    #  2019-06-04 14:50      Q22ANS      14.097165      -16      0      FN81      0.001      WA2ZKD       FN13ed       1212     284
    #  2019-06-04 14:50      Q22ANS      14.097169        0      0      FN81      0.001      N2HQI        FN13sa       1116     283

    def ConvertFromNewDb(self, argList):
        rCallsign        = None
        rGrid            = None
        colConvertedList = []
        
        #colConvertedList.append(argList[]) ;# YYMMDD
        #colConvertedList.append(argList[]) ;# HHMM
        #colConvertedList.append(argList[]) ;# dB
        #colConvertedList.append(argList[]) ;# DT
        #colConvertedList.append(argList[]) ;# freq
        #colConvertedList.append(argList[]) ;# CALLSIGN
        #colConvertedList.append(argList[]) ;# GRID
        #colConvertedList.append(argList[]) ;# PWRDBM
        #colConvertedList.append(argList[]) ;# DRIFT
        
        return rCallsign, rGrid, colConvertedList


    #
    # WSPRnet old db
    # headers (13)
    #
    #    0         1          2             3           4       5        6          7        8          9            10        11        12
    #  date       time       Call       Frequency      SNR    Drift    Grid        dBm       W          by           loc       km        mi
    #  2019-06-05 13:44      LA6GH      14.097143      -28      0      JP32cl      +20      0.100       G8LCO      IO91vu      1242      772 
    #  2019-06-05 13:44      G7WIR      14.097072      -25      0      JO01bj      +27      0.501       G8LCO      IO91vu      56         35 
    #  2019-06-05 13:44      HB4FV      10.140128      -28     -3      JN36fq      +30      1.000       G8LCO      IO91vu      750       466 
    #  2019-06-05 13:44      DL0IF      18.106133      -28     -3      JN48        +20      0.100      CT1JJU      IM57ol      1884     1171 
    #  2019-06-05 13:44      AC8MO      18.106142      -17      0      EN82fm      +23      0.200      CT1JJU      IM57ol      6182     3841 

    def ConvertFromOldDb(self, argList):
        rCallsign        = None
        rGrid            = None
        colConvertedList = []
        
        #colConvertedList.append(argList[]) ;# YYMMDD
        #colConvertedList.append(argList[]) ;# HHMM
        #colConvertedList.append(argList[]) ;# dB
        #colConvertedList.append(argList[]) ;# DT
        #colConvertedList.append(argList[]) ;# freq
        #colConvertedList.append(argList[]) ;# CALLSIGN
        #colConvertedList.append(argList[]) ;# GRID
        #colConvertedList.append(argList[]) ;# PWRDBM
        #colConvertedList.append(argList[]) ;# DRIFT
        
        return rCallsign, rGrid, colConvertedList




        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        






