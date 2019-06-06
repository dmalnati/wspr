from libWeb import *
from libGeolocation import *


webHandler = None









class WSSpotQuery(WSEventHandler):
    def __init__(self, db):
        self.db = db
        
    def OnWSConnectIn(self, ws):
        # I don't think I care yet, wait for message
        pass
    
    def OnClose(self, ws):
        # also don't care, should have handed off to something else by now
        pass

    def OnMessage(self, ws, msg):
        # look at request and do query
        #dateTimeGte = msg["DATE_TIME_GTE"]
        #dateTimeLte = msg["DATE_TIME_LTE"]
        #callsign    = msg["CALLSIGN"]
        
        # return data between those date ranges
        # if either end is blank, no limit.
        # for the lower end, that means go back indefinitely far.
        # for the upper end, that means set timer to check back periodically for more.
        
        # return data as
        # {
        #      "TIME" : ...
        #      "LATITUDE",
        #      "LONGITUDE"
        #      "REPORTER_CALLSIGN",
        #      "REPORTER_LATITUDE"
        #      "REPORTER_LONGITUDE"
        # }
        # 

        t = self.db.GetTable("WSPR_DECODED")
        rec = t.GetRecordAccessor()
        
        
        
        

    #    +ALTITUDE_FT     : 10000
    #     CALLSIGN        : Q42SNP
    #    +CALLSIGN_DECODED: KD2KDD
    #     DATE            : 2019-06-04 13:54
    #     DBM             : +17
    #     DRIFT           : 0
    #     FREQUENCY       : 14.097005
    #     GRID            : FN71
    #    +GRID_DECODED    : FN71SN
    #    +ID              : 1574
    #     KM              : 2038
    #     MI              : 1266
    #     REPORTER        : WD4AH
    #     RGRID           : EL89rt
    #     SNR             : -11
    #    +SPEED_MPH       : 18
    #    +TEMPERATURE_C   : 0
    #    +VOLTAGE         : 1500
    #     WATTS           : 0.050

        geo = Geolocation()
        
        spotList = []
        while rec.ReadNextInLinearScan():
        
            lat, lng = geo.ConvertGridToLatLngDecimal(rec.Get("GRID_DECODED"))
            rLat, rLng = geo.ConvertGridToLatLngDecimal(rec.Get("RGRID"))
        
            spotList.append({
                "TIME": rec.Get("DATE"),
                "LAT" : lat,
                "LNG" : lng,
                "REPORTER": rec.Get("REPORTER"),
                "RLAT" : rLat,
                "RLNG" : rLng,
            })
            
        ws.Write(spotList)
    
    
    
    
    
    








class Handler():
    def __init__(self, webServer):
        self.webServer = webServer
        
    def Init(self):
        self.SetUpSpotQuery()
        
    def SetUpSpotQuery(self):
        listner = WSSpotQuery(self.webServer.db)

        self.webServer.AddWSListener(listner, "/wspr2aprs/ws/spotquery")
        
    
    
    
    
    
    
    
    
    
    
    
    

def Init(webServer):
    global webHandler
    
    if not webHandler:
        webHandler = Handler(webServer)
        
        webHandler.Init()


        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        


