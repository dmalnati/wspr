import * as libLoad from '/core/js/libLoad.js';




////////////////////////////////////////////////////////////////////////////////
//
// SpotMap
//
////////////////////////////////////////////////////////////////////////////////

export
class SpotMap
{
    constructor(idContainer)
    {
        this.idContainer = idContainer;
        this.map = null;
        this.markerList = [];
        this.time__locTx = {};
        
        // mid-eastern seaboard
        this.initialCenterLocation = { lat: 36.521387, lng: -76.303034 };
        this.initialZoom           = 5;
    }

    Load()
    {
        console.log("Load");
        
        let scriptSrc = 'https://maps.googleapis.com/maps/api/js?key=AIzaSyAXdaFYzQw9dxu-dG7t-LDL1jG7jhFjr8g';
        
        let readyFn;
        let promise = new Promise((ready) => {
            readyFn = ready;
        });
        
        libLoad.LoadScriptAsPromise(scriptSrc).then(() => {
            console.log("Google Maps loaded, creating map instance");
            
            this.map = new google.maps.Map(document.getElementById(this.idContainer), {
                center: this.initialCenterLocation,
                zoom: this.initialZoom,
                mapTypeId: google.maps.MapTypeId.TERRAIN,
            });
            
            readyFn()
        });
        
        return promise;
    }
    
    AddSpot(spot)
    {
        let locTx = spot.GetLocationTransmitter();
        let locRx = spot.GetLocationReporter();
        
        //this.AddMarker(locTx);
        this.AddMarker(locRx);
        //this.AddLine(locTx, locRx);
        
        
        // Keep track of flight path
        let time = spot.GetTime();
        
        if (!(time in this.time__locTx))
        {
            this.time__locTx[time] = locTx;
        }
    }
    
    DataDone()
    {
        let timeList = Object.keys(this.time__locTx);
        
        timeList.sort();
        
        let locLast = null;
        for (let time of timeList)
        {
            let loc = this.time__locTx[time];
            
            this.AddMarker(loc);
            
            if (locLast)
            {
                this.AddLine(locLast, loc, 'blue');
            }
            
            locLast = loc;
        }
    }
        
    
    ///////////////////////////////////
    // Private
    ///////////////////////////////////

    AddMarker(point)
    {
        let marker = new google.maps.Marker({position: point});
        
        marker.setMap(this.map);
        
        this.markerList.push(marker);
    }
    
    AddLine(point1, point2, color)
    {
        let line = new google.maps.Polyline({
            path: [point1, point2],
            geodesic: true,
            strokeColor: color,
            strokeOpacity: 1.0,
            strokeWeight: 2
        });
        
        line.setMap(this.map);
    }
 }
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 