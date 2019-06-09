import * as libUtl from '/core/js/libUtl.js';
import * as libWS from '/core/js/libWS.js';
import * as libSpot from '/wspr2aprs/js/libSpot.js';
import * as libSpotMap from '/wspr2aprs/js/libSpotMap.js';
import * as libSpotDashboard from '/wspr2aprs/js/libSpotDashboard.js';



////////////////////////////////////////////////////////////////////////////////
//
// TxEvent
//
////////////////////////////////////////////////////////////////////////////////

export
class TxEvent
{
    constructor()
    {
        this.time     = null;
        this.spotList = [];
    }

    SetTime(time)
    {
        this.time = time;
    }

    AddSpot(spot)
    {
        this.spotList.push(spot);
    }
}




    
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
        this.spotMap = new libSpotMap.SpotMap(cfg.idMap);
        
        // Dashboard
        this.dash = new libSpotDashboard.SpotDashboard(cfg);
        
        // Spots
        this.ws = null;
        this.time__txEvent = {};
        
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
        
        window.addEventListener('resize', () => {
            this.dash.Draw()
        });
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
        
        let spotList = [];
        
        let spotDataList = msg;
        for (let spotData of spotDataList)
        {
            // Organize spot data
            let spot = new libSpot.Spot(spotData);
            
            spotList.push(spot);

            let time = spot.GetTime();
            if (!(time in this.time__txEvent))
            {
                let txEvent = new TxEvent();
                txEvent.SetTime(time);

                this.time__txEvent[time] = txEvent;
            }

            let txEvent = this.time__txEvent[time];

            txEvent.AddSpot(spot);
            
            
            // Hand off a spot to the map
            this.spotMap.AddSpot(spot);
        }
        
        this.spotMap.DataDone();
        
        
        // Hand off to dashboard
        this.dash.AddSpotList(spotList);
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






