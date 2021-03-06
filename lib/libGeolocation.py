


class Geolocation:

    
    #################################################
    ##
    ## Latitude and Longitude
    ##
    #################################################
    
    def ConvertLatLngToDegreesMinutesSeconds(self, latOrLongInMillionths):
        ONE_MILLION     = 1000000
        MIN_PER_DEGREE  = 60
        SECONDS_PER_MIN = 60
        
        # Capture input value for manipulation
        valRemaining = float(latOrLongInMillionths)                    ;# eg 40736878

        # Calculate degrees
        degrees = int(valRemaining / ONE_MILLION)                     ;# eg 40

        # Calculate minutes by converting millionths of a degree
        valRemaining = abs(valRemaining) - \
                       (abs(degrees) * ONE_MILLION)                   ;# eg   736878
        
        valRemaining = (valRemaining / ONE_MILLION) * MIN_PER_DEGREE  ;# eg   44.21268

        minutes = int(valRemaining)                                   ;# eg 44

        # Calculate seconds by converting the fractional minutes
        valRemaining -= minutes                                       ;# eg .21268
        
        valRemaining *= SECONDS_PER_MIN                               ;# eg 12.7608
        
        seconds = valRemaining                                        ;# eg 12.7608
        
        return degrees, minutes, seconds

        
    #################################################
    ##
    ## Grid
    ##
    #################################################
    
    def ConvertGridToLatLngDecimal(self, grid):
        latMillionths = self.GetLatitudeFromGrid(grid)
        lngMillionths = self.GetLongitudeFromGrid(grid)
        
        lat = latMillionths / 1000000.0
        lng = lngMillionths / 1000000.0
        
        return lat, lng
    
    #################################################
    ##
    ## Latitude
    ##
    #################################################
    
    def ConvertGridToLatitudeDegMinHundredths(self, grid):
        latMillionths = self.GetLatitudeFromGrid(grid)
        
        degrees, minutes, seconds = self.ConvertLatLngToDegreesMinutesSeconds(latMillionths)
        
        aprsStr = self.ConvertLatitudeFromDegMinSecToDegMinHundredths(degrees, minutes, seconds)
        
        return aprsStr
    
    
    def GetLatitudeFromGrid(self, grid):
        lat  = 0
        lat += (ord(grid[1]) - ord('A')) * 100000
        lat += (ord(grid[3]) - ord('0')) *  10000
        
        if len(grid) >= 6:
            lat += (ord(grid[5]) - ord('A')) *    417
        
        lat -= (90 * 10000)
        
        lat *= 100  ; # in millions of a degree
        
        return lat

    #
    # The latitude is shown as the 8-character string
    # ddmm.hhN (i.e. degrees, minutes and hundredths of a minute north)
    #
    # ex: 4903.50N is 49 degrees 3 minutes 30 seconds north
    #
    def ConvertLatitudeFromDegMinSecToDegMinHundredths(self, degrees, minutes, seconds):
        # Constrain values
        if degrees < -90:
            degrees = -90
        
        if degrees > 90:
            degrees = 90
            
        if minutes > 59:
            minutes = 59
            
        if seconds > 59:
            seconds = 59
            
        
        # Calculate values
        northOrSouth = "S"
        if degrees >= 0:
            northOrSouth = "N"
        
        degreesPos          = int(abs(degrees))
        secondsAsHundredths = int(round(seconds / 60.0 * 100.0))
        
        if secondsAsHundredths == 100:
            secondsAsHundredths = 99
        
        str = "%02i%02i.%02i%c" % (degreesPos, minutes, secondsAsHundredths, northOrSouth)
        
        return str
    
    
    #################################################
    ##
    ## Longitude
    ##
    #################################################
    
    def ConvertGridToLongitudeDegMinHundredths(self, grid):
        lngMillionths = self.GetLongitudeFromGrid(grid)
        
        degrees, minutes, seconds = self.ConvertLatLngToDegreesMinutesSeconds(lngMillionths)
        
        aprsStr = self.ConvertLongitudeFromDegMinSecToDegMinHundredths(degrees, minutes, seconds)
        
        return aprsStr
        
    
    def GetLongitudeFromGrid(self, grid):
        lng  = 0
        lng += (ord(grid[0]) - ord('A')) * 200000
        lng += (ord(grid[2]) - ord('0')) *  20000
        
        if len(grid) >= 5:
            lng += (ord(grid[4]) - ord('A')) *    834
        
        lng -= (180 * 10000)
        
        lng *= 100  ; # in millions of a degree
        
        return lng
        
    #
    # The longitude is shown as the 9-character string
    # dddmm.hhW (i.e. degrees, minutes and hundredths of a minute west)
    #
    # ex: 07201.75W is 72 degrees 1 minute 45 seconds west
    #
    def ConvertLongitudeFromDegMinSecToDegMinHundredths(self, degrees, minutes, seconds):
        # Constrain values
        if degrees < -179:
            degrees = -179
            
        if degrees > 180:
            degrees = 180
            
        if minutes > 59:
            minutes = 59
        
        if seconds > 59:
            seconds = 59
        
        
        # Calculate values
        eastOrWest = "W"
        if degrees >= 0:
            eastOrWest = "E"
        
        degreesPos = int(abs(degrees))
        secondsAsHundredths = int(round(seconds / 60.0 * 100.0));
        
        if secondsAsHundredths == 100:
            secondsAsHundredths = 99
        
        str = "%03i%02i.%02i%c" % (degreesPos, minutes, secondsAsHundredths, eastOrWest)
        return str
        

    #################################################
    ##
    ## Course
    ##
    #################################################
        
    def GetCourseDegs(self, degs):
        str = "%03i" % (int(degs))
        
        return str
        
        
    #################################################
    ##
    ## Speed
    ##
    #################################################
        
    def GetSpeedKnotsFromSpeedMph(self, speedMph):
        str = "/%03i" % (int(speedMph / 1.151))
        
        return str
        

    #################################################
    ##
    ## Altitude
    ##
    #################################################
        
    def ConvertAltitudeFtToAPRSFeet(self, altitudeFt):
        str = "/A=%06i" % (altitudeFt)
        
        return str
        
        
