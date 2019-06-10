import * as libLoad from '/core/js/libLoad.js';





////////////////////////////////////////////////////////////////////////////////
//
// TxEvent
//
////////////////////////////////////////////////////////////////////////////////

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
    
    GetTime()
    {
        return this.time;
    }
    
    GetSpotList()
    {
        return this.spotList;
    }
}


// returns sorted-by-time list
class TxEventConverter
{
    static GetFromSpotList(spotList)
    {
        let time__txEvent = {};
        
        for (let spot of spotList)
        {
            let time = spot.GetTime();
            
            if (!(time in time__txEvent))
            {
                let txEvent = new TxEvent();
                txEvent.SetTime(time);

                time__txEvent[time] = txEvent;
            }

            let txEvent = time__txEvent[time];

            txEvent.AddSpot(spot);
        }
        
        let timeList = Object.keys(time__txEvent);
        timeList.sort();
        
        let txEventList = [];
        for (let time of timeList)
        {
            txEventList.push(time__txEvent[time]);
        }
        
        return txEventList;
    }
}




////////////////////////////////////////////////////////////////////////////////
//
// SpotMap
//
////////////////////////////////////////////////////////////////////////////////


class Reporter
{
    constructor(name, location)
    {
        this.name     = name;
        this.location = location;
    }
    
    GetName()
    {
        return this.name;
    }
    
    GetLocation()
    {
        return this.location;
    }
}













////////////////////////////////////////////////////////////////////////////////
//
// SpotMap
//
////////////////////////////////////////////////////////////////////////////////

export
class SpotMap
{
    constructor(cfg)
    {
        this.cfg = cfg;
        this.idContainer = this.cfg.idMap;
        this.map = null;
        
        // map element state keeping
        this.reporterName__data = new Map();
        this.markerListRx = [];
        this.txDataList = [];
        this.infoWindowList = [];
        
        this.showAllReceivers = true;
        
        this.tracking = true;
        
        
        // mid-eastern seaboard
        this.initialCenterLocation = { lat: 36.521387, lng: -76.303034 };
        this.initialZoom           = 7;
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
            
            this.SetUpHandlers();
            
            readyFn()
        });
        
        return promise;
    }
    
    
    
    ///////////////////////////////////
    // Event handling
    ///////////////////////////////////
    
    SetUpHandlers()
    {
        document.getElementById(this.cfg.idButtonShowAllRxMarkers).onclick = () => {
            this.OnShowAllReceivers();
        };
        
        document.getElementById(this.cfg.idButtonHideAllRxMarkers).onclick = () => {
            this.OnHideAllReceivers();
        };
        
        this.map.addListener('click', () => {
            this.CloseAllInfoWindows();
            
            this.tracking = false;
        });
    }
    
    OnShowAllReceivers()
    {
        this.showAllReceivers = true;
        
        for (let marker of this.markerListRx)
        {
            marker.setMap(this.map);
        }
    }
    
    OnHideAllReceivers()
    {
        this.showAllReceivers = false;
        
        for (let marker of this.markerListRx)
        {
            marker.setMap(null);
        }
    }
    
    
    
    
    ///////////////////////////////////
    // UI Commands
    ///////////////////////////////////
    
    CloseAllInfoWindows()
    {
        for (let infoWindow of this.infoWindowList)
        {
            infoWindow.close();
        }
    }
    
    CloseAllTransmitterMarkers()
    {
        for (let txData of this.txDataList)
        {
            txData.marker.setVisible(false);
        }
    }
    
    
    
    
    
    
    
    ///////////////////////////////////
    // New Data
    ///////////////////////////////////
    
    AddSpotList(spotList)
    {
        for (let spot of spotList)
        {
            this.AddSpot(spot);
        }
    }
    
    AddSpot(spot)
    {
        let reporterName = spot.GetReporter();
        
        // Maintain reporter data
        if (!(this.reporterName__data.has(reporterName)))
        {
            let rxLocation = spot.GetLocationReporter();
            
            let marker = new google.maps.Marker({
                position : rxLocation,
                icon     : '/wspr2aprs/img/tower.png',
            });
            
            this.GiveMarkerReporterPopup(marker, reporterName);

            let data = {
                marker: marker,
            };
            
            this.reporterName__data.set(reporterName, data);
            this.markerListRx.push(marker);
            
            if (this.showAllReceivers)
            {
                marker.setMap(this.map);
            }
        }
        
        
        
        // Maintain transmitter data
        // (assumes data comes in chronologically)
        let txLocation = spot.GetLocationTransmitter();
        let txTime     = spot.GetTime();
        let found      = false;
        
        for (let txData of this.txDataList)
        {
            if (txData.txLocation.x == txLocation.x &&
                txData.txLocation.y == txLocation.y &&
                txData.txTime == txTime)
            {
                found = true;
            }
        }
        
        if (!found)
        {
            // Decide if you want a line connecting prior position to here
            // (yes if there was a prior position)
            let line = null;
            
            if (this.txDataList.length)
            {
                let txLocationPrev = this.txDataList[this.txDataList.length - 1].txLocation;
                
                line = new google.maps.Polyline({
                    path          : [txLocationPrev, txLocation],
                    geodesic      : true,
                    strokeColor   : 'blue',
                    strokeOpacity : 1.0,
                    strokeWeight  : 4,
                });
                
                line.setMap(this.map);
            }
            
            // Do remaining UI work for this spot regardless of prior spots
            
            // Marker
            let marker = new google.maps.Marker({
                position : txLocation,
                icon     : '/wspr2aprs/img/balloon.png',
            });
            
            let infoWindow = this.GiveMarkerTransmitterPopup(marker, spot);
            this.CloseAllTransmitterMarkers();
            marker.setMap(this.map);
            
            if (this.tracking)
            {
                new google.maps.event.trigger(marker, 'click');
            }

            // Dot
            let dot = new google.maps.Polyline({
                path          : [txLocation, txLocation],
                geodesic      : true,
                strokeColor   : 'red',
                strokeOpacity : 1.0,
                strokeWeight  : 6,
                zIndex        : 10,
            });
            
            dot.addListener('click', () => {
                console.log("poly onclick");
                infoWindow.open(this.map, marker);
            });
            dot.setMap(this.map);
            
            
            
            
            // Retain state about transmitter UI
            let txData = {
                txTime     : txTime,
                txLocation : txLocation,
                marker     : marker,
                infoWindow : infoWindow,
                line       : line,
                dot        : dot,
            };
            
            this.txDataList.push(txData);
            
            if (this.tracking)
            {
                this.map.panTo(txLocation);
            }
        }
    }
    
    
    GiveMarkerTransmitterPopup(marker, spot)
    {
        let time = spot.GetTime();
        
        let contentString = `${time}`;
        
        let infoWindow = new google.maps.InfoWindow({
            content: contentString
        });
        
        marker.addListener('click', () => {
            this.CloseAllInfoWindows();
            infoWindow.open(this.map, marker);
            
            this.tracking = true;
        });
        
        this.infoWindowList.push(infoWindow);
        
        return infoWindow;
    }
    
    GiveMarkerReporterPopup(marker, reporterName)
    {
        let contentString = `${reporterName}`;
        
        let infoWindow = new google.maps.InfoWindow({
            content: contentString
        });
        
        marker.addListener('click', () => {
            this.CloseAllInfoWindows();
            infoWindow.open(this.map, marker);
        });
        
        this.infoWindowList.push(infoWindow);
        
        return infoWindow;
    }
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    ///////////////////////////////////
    // Old Code
    ///////////////////////////////////
    
    
    
    AddSpotListOld(spotList)
    {
        // Keep cache of all spots ever seen
        this.spotList = [...this.spotList, ...spotList];
        
        // Update visuals
        this.Draw();
    }
    
    Draw()
    {
        // Convert cached spot list into tx events
        this.txEventList = TxEventConverter.GetFromSpotList(this.spotList);
        
        // get list of transmitter locations
        let pointListTransmitter = this.GetPointListTransmitter();
        
        // get list of reporters
        let reporterList = this.GetReporterList();
        
        
        // Reset map
        this.ClearMap();
        
        // Draw reporters
        for (let reporter of reporterList)
        {
            this.AddMarker(reporter.GetLocation());
        }
        
        // Draw transmitter path
        let pointLast = null;
        for (let point of pointListTransmitter)
        {
            this.AddMarker(point);
            
            if (pointLast)
            {
                this.AddLine(pointLast, point, 'blue');
            }
            
            pointLast = point;
        }
    }
    
    
    ///////////////////////////////////
    // Private
    ///////////////////////////////////

    
    GetPointListTransmitter()
    {
        let pointList = [];
        
        for (let txEvent of this.txEventList)
        {
            // Each TxEvent will have 1 or more spots, all from the same
            // time and transmitter location.
            let spot = txEvent.GetSpotList()[0];
            
            let point = spot.GetLocationTransmitter();
            
            pointList.push(point);
        }
        
        return pointList;
    }
    
    // Unique list, not necessarily associated with a single event.
    GetReporterList()
    {
        let reporterName__seen = {};
        
        let reporterList = [];
        
        for (let txEvent of this.txEventList)
        {
            for (let spot of txEvent.GetSpotList())
            {
                let reporterName = spot.GetReporter();
                
                if (!(reporterName in reporterName__seen))
                {
                    reporterName__seen[reporterName] = true;
                    
                    let reporter = new Reporter(reporterName, spot.GetLocationReporter());
                    
                    reporterList.push(reporter);
                }
            }
        }
        
        return reporterList;
    }
    
    ClearMap()
    {
        for (let marker of this.markerList)
        {
            marker.setMap(null);
        }
        
        this.markerList = [];
    }

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
        
        // debug
        this.markerList.push(line);
    }
 }
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 