from libWeb import *
from libGeolocation import *
from libTimeAndTimeZone import *


webHandler = None





class WSSpotQuery(WSEventHandler):
    def __init__(self, db, ws, pollPeriodMs):
        self.pollPeriodMs = pollPeriodMs
        self.ws = ws
        self.tatz = TimeAndTimeZone()
        self.rec = db.GetTable("WSPR_DECODED").GetRecordAccessor()
        self.rowIdLast = -1
        self.query = None
        self.geo = Geolocation()
        
        self.timer = None
        
        self.firstReply = True

        
    def OnClose(self, ws):
        if self.timer:
            evm_CancelTimeout(self.timer)
            self.timer = None
        
    def OnError(self, ws):
        ws.Close()
        
        if self.timer:
            evm_CancelTimeout(self.timer)
            self.timer = None

    
    def OnMessage(self, ws, msg):
        if "MESSAGE_TYPE" in msg:
            if msg["MESSAGE_TYPE"] == "SPOT_QUERY":
                self.query = {
                    "clientTimeZone" : msg["TIMEZONE"],
                    "dtGte"          : msg["DT_GTE"],
                    "dtLte"          : msg["DT_LTE"],
                    "callsign"       : msg["CALLSIGN"],
                }
                
                Log("Received spot query")
                Log(str(self.query))
                
                self.DoQuery()
            elif msg["MESSAGE_TYPE"] == "HEARTBEAT":
                ws.Write({"MESSAGE_TYPE" : "HEARTBEAT"})
        
        
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
    def DoQuery(self):
        self.timer = None
    
        clientTimeZone = self.query['clientTimeZone']
        dtGte          = self.query['dtGte']
        dtLte          = self.query['dtLte']
        qryCallsign    = self.query['callsign']
        rec            = self.rec
    
        spotList = []
        
        rec.SetRowId(self.rowIdLast)
        
        wentTooFar = False
        
        formatStrParse = "%Y-%m-%d %H:%M"
        formatStrSend  = "%Y-%m-%d %H:%M:%S"
        while rec.ReadNextInLinearScan():
            # Build list of record items to compare to query
        
            # convert UTC timestamps to the timezone of the client
            # Looks like "YYYY-MM-DD HH:MM:SS" and matches query input
            self.tatz.SetTime(rec.Get("DATE"), formatStrParse, "UTC")
            timeConverted = self.tatz.GetTimeNativeInTimeZone(clientTimeZone).strftime(formatStrSend)
            
            callsign = rec.Get("CALLSIGN_DECODED")
            
            # confirm if record matches criteria
            queryMatch = True
            
            if qryCallsign != "":
                queryMatch &= (callsign == qryCallsign)
            else:
                pass
            
            if dtGte != "":
                queryMatch &= (dtGte <= timeConverted)
            else:
                pass
            
            if dtLte != "":
                if timeConverted <= dtLte:
                    queryMatch &= True
                else:
                    queryMatch = False
                    wentTooFar = True
                    
                    break
            else:
                pass
                
            if queryMatch:
                lat, lng   = self.geo.ConvertGridToLatLngDecimal(rec.Get("GRID_DECODED"))
                rLat, rLng = self.geo.ConvertGridToLatLngDecimal(rec.Get("RGRID"))
            
                spotList.append({
                    "TIME_ORIG"     : rec.Get("DATE"),
                    "TIME"          : timeConverted,
                    "LAT"           : lat,
                    "LNG"           : lng,
                    "MI"            : rec.Get("MI"),
                    "ALTITUDE_FT"   : rec.Get("ALTITUDE_FT"),
                    "SPEED_MPH"     : rec.Get("SPEED_MPH"),
                    "TEMPERATURE_C" : rec.Get("TEMPERATURE_C"),
                    "VOLTAGE"       : rec.Get("VOLTAGE"),
                    "REPORTER"      : rec.Get("REPORTER"),
                    "RLAT"          : rLat,
                    "RLNG"          : rLng,
                    "SNR"           : rec.Get("SNR"),
                    "FREQUENCY"     : rec.Get("FREQUENCY"),
                    "DRIFT"         : rec.Get("DRIFT"),
                })
                
        if len(spotList) or self.firstReply:
            self.ws.Write(spotList)
            self.firstReply = False
        
        # retain position in database for next search
        # possible that starting position is the same as the ending position,
        # which means no new records found.  This is expected and fine.
        # when we wake up again, try again and maybe more will have arrived.
        self.rowIdLast = rec.GetRowId()
        
        # Actually only search for more if you didn't pass the end time
        if not wentTooFar:
            self.timer = evm_SetTimeout(self.DoQuery, self.pollPeriodMs)
        else:
            pass
    
    


class WSSpotQueryDispatcher(WSEventHandler):
    def __init__(self, db, pollPeriodMs):
        self.db = db
        self.pollPeriodMs = pollPeriodMs
        
    def OnWSConnectIn(self, ws):
        ws.SetHandler(WSSpotQuery(self.db, ws, self.pollPeriodMs))
    




class Handler():
    def __init__(self, webServer):
        self.webServer = webServer
        
    def Init(self):
        self.SetUpSpotQuery()
        
    def SetUpSpotQuery(self):
        POLL_PERIOD_MS = 15000
        
        listner = WSSpotQueryDispatcher(self.webServer.db, POLL_PERIOD_MS)

        self.webServer.AddWSListener(listner, "/wspr/ws/spotquery")
        
    
    
    
    
    
    
    
    
    
    
    
    

def Init(webServer):
    global webHandler
    
    if not webHandler:
        webHandler = Handler(webServer)
        
        webHandler.Init()


        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        


