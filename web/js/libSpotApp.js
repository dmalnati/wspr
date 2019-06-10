import * as libUtl from '/core/js/libUtl.js';
import * as libWS from '/core/js/libWS.js';
import * as libSpot from '/wspr2aprs/js/libSpot.js';
import * as libSpotMap from '/wspr2aprs/js/libSpotMap.js';
import * as libSpotDashboard from '/wspr2aprs/js/libSpotDashboard.js';






    
////////////////////////////////////////////////////////////////////////////////
//
// SpotApp
//
////////////////////////////////////////////////////////////////////////////////
    
export
class SpotApp extends libWS.WSEventHandler
{
    constructor(cfg)
    {
        super();
        
        this.cfg = cfg;
        
        // Map App
        this.spotMap = new libSpotMap.SpotMap(this.cfg);
        
        // Dashboard
        this.dash = new libSpotDashboard.SpotDashboard(this.cfg);
        
        // Spots
        this.ws = null;
        
        // UI
        this.dom = {};
        this.dom.timeGte     = document.getElementById(this.cfg.idTimeGte);
        this.dom.timeLte     = document.getElementById(this.cfg.idTimeLte);
        this.dom.callsign    = document.getElementById(this.cfg.idCallsign);
        this.dom.buttonQuery = document.getElementById(this.cfg.idButtonQuery);
    }
    
    Run()
    {
        console.log("Run");
        
        // Set up some initial UI styling
        let formatStr = 'YYYY-MM-DD[T]HH:mm:ss';

        this.dom.timeGte.value = moment().subtract(1, "hour").format(formatStr);
        this.dom.timeLte.value = moment().add(1, "hour").format(formatStr);
        
        
        // wait for all async modules to be ready
        console.log("Waiting for SpotMap and Dashboard to load");
        
        let promiseList = [];
        
        promiseList.push(this.spotMap.Load());
        promiseList.push(this.dash.Load());
        
        Promise.all(promiseList).then(() => {
            console.log("Spot map loaded, setting up UI handlers");
            
            this.SetUpHandlers();
        });
    }
    
    SetUpHandlers()
    {
        this.dom.buttonQuery.onclick = () => this.OnQuery();
        
        // debug
        this.OnQuery();
    }
    
    OnQuery()
    {
        console.log("OnQuery");
        this.ws = libWS.WSManager.Connect(this, "/wspr2aprs/ws/spotquery");
    }

    
    /////////////////////////////////////////////////////////////
    //
    // WS event handling
    //
    /////////////////////////////////////////////////////////////

    OnConnect(ws)
    {
        console.log("OnConnect");
        ws.Write({
            "TIMEZONE" : Intl.DateTimeFormat().resolvedOptions().timeZone,
        });
    }

    OnMessage(ws, msg)
    {
        console.log("OnMessage");
        
        // Convert data into Spot classes
        let spotDataList = msg;
        
        let spotList = [];
        for (let spotData of spotDataList)
        {
            let spot = new libSpot.Spot(spotData);
            
            spotList.push(spot);
        }
        
        if (1)
        {
            // Hand off to map
            this.spotMap.AddSpotList(spotList);
            
            // Hand off to dashboard
            this.dash.AddSpotList(spotList);
        }
        else
        {
            this.AsyncHandoff(spotList);
        }
    }
    
    
    AsyncHandoff(spotList)
    {
        let that = this;
        
        let count = 0;
        function AsyncAdd() {
            console.log("AsyncAdd");
            
            let spot = spotList.shift();
            
            if (spot)
            {
                // Hand off to map
                that.spotMap.AddSpotList([spot]);
                
                // Hand off to dashboard
                //that.dash.AddSpotList([spot]);
                
                
                ++count;
                
                if (count < 120)
                {
                    setTimeout(AsyncAdd, 200);
                }
            }
        }
        
        AsyncAdd()
    }

    
    
    
    
    
    
    
    
    
    
    
    

    OnClose(ws)
    {
        console.log("OnClose");
    }

    OnError(ws)
    {
        console.log("OnError");
    }

    
}






