from libWeb import *
from libGeolocation import *
from libTimeAndTimeZone import *


webHandler = None








class WSSpotQuery(WSEventHandler):
    def __init__(self, db):
        self.db = db
        self.t = self.db.GetTable("WSPR_DECODED")
        self.tatz = TimeAndTimeZone()
        
    def OnWSConnectIn(self, ws):
        # I don't think I care yet, wait for message
        pass
    
    def OnClose(self, ws):
        # also don't care, should have handed off to something else by now
        pass

    def OnMessage(self, ws, msg):
        clientTimeZone = msg["TIMEZONE"]
        
        
        
        
        

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
        
        
        rec = self.t.GetRecordAccessor()
        while rec.ReadNextInLinearScan():
        
            formatStrParse = "%Y-%m-%d %H:%M"
            formatStrSend  = "%Y-%m-%d %H:%M:%S"

            # convert UTC timestamps to the timezone of the client
            self.tatz.SetTime(rec.Get("DATE"), formatStrParse, "UTC")
            timeConverted = self.tatz.GetTimeNativeInTimeZone(clientTimeZone).strftime(formatStrSend)
            
            lat, lng = geo.ConvertGridToLatLngDecimal(rec.Get("GRID_DECODED"))
            rLat, rLng = geo.ConvertGridToLatLngDecimal(rec.Get("RGRID"))
        
            spotList.append({
                "TIME_ORIG": rec.Get("DATE"),
                "TIME": timeConverted,
                "LAT" : lat,
                "LNG" : lng,
                "MI" : rec.Get("MI"),
                "ALTITUDE_FT" : rec.Get("ALTITUDE_FT"),
                "SPEED_MPH" : rec.Get("SPEED_MPH"),
                "TEMPERATURE_C" : rec.Get("TEMPERATURE_C"),
                "VOLTAGE" : rec.Get("VOLTAGE"),
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


        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        


