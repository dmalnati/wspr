import { Log } from '/core/js/libUtl.js';
import * as libWS from '/core/js/libWS.js';
import * as libSpot from '/wspr/js/libSpot.js';
import * as libSpotMap from '/wspr/js/libSpotMap.js';
import * as libSpotDashboard from '/wspr/js/libSpotDashboard.js';






    
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
        this.dom.dtGte       = document.getElementById(this.cfg.idDtGte);
        this.dom.dtLte       = document.getElementById(this.cfg.idDtLte);
        this.dom.callsign    = document.getElementById(this.cfg.idCallsign);
        this.dom.form        = document.getElementById(this.cfg.idForm);
        this.dom.status      = document.getElementById(this.cfg.idStatus);
        this.dom.dialog      = document.getElementById(this.cfg.idDialog);
    }
    
    Run()
    {
        // Set up some initial UI styling
        
        
        // wait for all async modules to be ready
        Log("Waiting for SpotMap and Dashboard to load");
        
        let promiseList = [];
        
        promiseList.push(this.spotMap.Load());
        promiseList.push(this.dash.Load());
        
        this.SetStatus("Loading");
        
        Promise.all(promiseList).then(() => {
            this.SetUpHandlers();
            
            this.SetStatus("Ready");
        });
    }
    
    SetUpHandlers()
    {
        // Don't capture inputs or show old ones
        this.dom.form.autocomplete = 'off';

        
        // Support events without relying on external implementation
        let dynJs = `
        //
        // technique adapted from
        // http://qnimate.com/detecting-end-of-scrolling-in-html-element/
        //
        function CaptureOverScrollOnWheel(domElement, event)
        {
            // check if we're scrolling down
            if (event.deltaY > 0)
            {
                // check if reached bottom
                if(domElement.offsetHeight + domElement.scrollTop == domElement.scrollHeight)
                {
                    event.preventDefault();
                }
            }
            
            // check if we're scrolling up
            if (event.deltaY < 0)
            {
                // check if reached bottom
                if(domElement.scrollTop == 0)
                {
                    event.preventDefault();
                }
            }
        }
        `;
        
        window.eval(dynJs);

        
        // Handle form submission without navigating away the page
        this.dom.form.onsubmit = (event) => {
            if (event)
            {
                event.preventDefault();
            }
            
            // Indicate in the URL bar the parameters
            let dtGte    = this.dom.dtGte.value.trim();
            let dtLte    = this.dom.dtLte.value.trim();
            let callsign = this.dom.callsign.value.trim();
            
            let newPath = `${location.pathname}?dtLte=${dtLte}&dtGte=${dtGte}&callsign=${callsign}`;
            
            let state = { dtGte, dtLte, callsign };
            
            window.history.pushState(state, newPath, newPath);
            
            // Kick off
            this.ReQuery();
            
            return false;
        };
        
        // If you detect forward/backward arrow, see what params were in use
        // and re-populate and re-query.
        window.onpopstate = (event) => {
            if (event.state)
            {
                this.dom.dtGte.value    = event.state.dtGte;
                this.dom.dtLte.value    = event.state.dtLte;
                this.dom.callsign.value = event.state.callsign;
                
                this.ReQuery();
            }
            
            return false;
        };
        
        
        // Check if any inputs are pre-populated.
        // If so, auto-submit the query.
        if (this.dom.dtGte.value.trim()    != '' ||
            this.dom.dtLte.value.trim()    != '' ||
            this.dom.callsign.value.trim() != '')
        {
            this.dom.form.onsubmit();
        }
    }
    
    
    ReQuery()
    {
        // Prepare page elements to be reconstituted
        this.dash.Reset();
        this.spotMap.Reset();
        
        this.OnQuery();
    }
    
    OnQuery()
    {
        Log("New query requested");
        
        if (this.ws)
        {
            Log("Prior connection active, closing");
            
            this.ws.Close();
            this.ws = null;
        }
        
        this.SetStatus("Connecting");
        
        this.ws = libWS.WSManager.Connect(this, "/wspr/ws/spotquery");
    }
    
    
    OnDataArrived(spotDataList)
    {
        this.SetStatus(`Got ${spotDataList.length} spots`);
        
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
            Log("AsyncAdd");
            
            let spot = spotList.shift();
            
            if (spot)
            {
                // Hand off to map
                that.spotMap.AddSpotList([spot]);
                
                // Hand off to dashboard
                //that.dash.AddSpotList([spot]);
                
                ++count;
                
                setTimeout(AsyncAdd, 200);
            }
        }
        
        AsyncAdd()
    }

    
    ShowDialog()
    {
        this.dom.dialog.style.visibility = 'visible';
        this.dom.dialog.showModal();
        this.dom.dialog.style.display = 'hidden';
    }
    
    SetStatus(status)
    {
        this.dom.status.value = status;
        
        Log(status);
    }
    

    
    /////////////////////////////////////////////////////////////
    //
    // WS event handling
    //
    /////////////////////////////////////////////////////////////

    OnConnect(ws)
    {
        Log("Connection established, sending query");
        
        this.SetStatus("Querying");
        
        // Convert from "2019-06-10T22:34:24" to "2019-06-10 22:34:24"
        // (remove the T, replace with space)
        let msg = {
            "TIMEZONE" : Intl.DateTimeFormat().resolvedOptions().timeZone,
            "DT_GTE"   : this.dom.dtGte.value.trim(),
            "DT_LTE"   : this.dom.dtLte.value.trim(),
            "CALLSIGN" : this.dom.callsign.value.trim(),
        };
        
        Log(JSON.stringify(msg));
        
        ws.Write(msg);
    }
    
    OnMessage(ws, msg)
    {
        this.OnDataArrived(msg);
    }
    
    OnClose(ws)
    {
        this.SetStatus("Connection closed");
        
        this.ShowDialog();
        
        this.ws = null;
    }

    OnError(ws)
    {
        this.SetStatus("WS ERR");
        
        this.ShowDialog();
        
        this.ws.Close();
        this.ws = null;
    }
}






