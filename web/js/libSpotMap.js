import * as libUtl from '/core/js/libUtl.js';
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
        this.domMapStatus = null;
        
        // map element state keeping
        this.reporterName__data = new Map();
        this.markerListRx = [];
        this.txDataList = [];
        this.infoWindowList = [];

        this.tracking = true;
        
        // Initial state of map
        this.initialCenterLocation = { lat: 36.521387, lng: -76.303034 };
        this.initialZoom           = 4;
    }

    Load()
    {
        console.log("SpotMap::Load");
        
        let libraryList = ['geometry'];
        let libraryListStr = libraryList.join(',');
        
        let scriptSrc  = 'https://maps.googleapis.com/maps/api/js';
            scriptSrc += '?key=AIzaSyAXdaFYzQw9dxu-dG7t-LDL1jG7jhFjr8g';
            scriptSrc += '&libraries=' + libraryListStr;
        
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
                gestureHandling: 'greedy',
            });
            
            this.SetUpHandles();
            this.SetUpHandlers();
            
            readyFn()
        });
        
        return promise;
    }
    
    
    ///////////////////////////////////
    // Handles to other resources
    ///////////////////////////////////
    
    SetUpHandles()
    {
        this.domMapStatus = document.getElementById(this.cfg.idMapStatus);
    }
    
    
    ///////////////////////////////////
    // Event handling
    ///////////////////////////////////
    
    SetUpHandlers()
    {
        this.map.addListener('click', () => {
            this.CloseAllInfoWindows();
            
            this.tracking = false;
            
            this.CloseAllReporterPaths();
        });
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
    
    CloseAllReporterPaths()
    {
        for (let txData of this.txDataList)
        {
            for (let reporterLine of txData.reporterLineList)
            {
                reporterLine.setMap(null);
            }
        }
    }
    
    OpenReporterPaths(txData)
    {
        for (let reporterLine of txData.reporterLineList)
        {
            reporterLine.setMap(this.map);
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
            this.UpdateMapInfo();
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
            
            marker.setMap(this.map);
        }
        
        
        
        // Maintain transmitter data
        // (assumes data comes in chronologically)
        let txLocation = spot.GetLocationTransmitter();
        let txTime     = spot.GetTime();
        let found      = false;
        
        
        let txData;
        for (let txDataTmp of this.txDataList)
        {
            if (txDataTmp.txLocation.x == txLocation.x &&
                txDataTmp.txLocation.y == txLocation.y &&
                txDataTmp.txTime == txTime)
            {
                found = true;
                
                txData = txDataTmp;
            }
        }
        
        if (!found)
        {
            txData = {};
            
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
                this.CloseAllInfoWindows();
                
                infoWindow.open(this.map, marker);
                
                // if you click this marker, show the paths
                this.CloseAllReporterPaths();
                this.OpenReporterPaths(txData);
            });
            dot.setMap(this.map);
            
            
            
            
            // Retain state about transmitter UI
            txData.txTime               = txTime;
            txData.txLocation           = txLocation;
            txData.marker               = marker;
            txData.infoWindow           = infoWindow;
            txData.line                 = line;
            txData.dot                  = dot;
            txData.reporterMarkerList   = [];
            txData.reporterLineList     = [];
            
            this.txDataList.push(txData);
            
            if (this.tracking)
            {
                new google.maps.event.trigger(marker, 'click');
                
                this.CloseAllReporterPaths();
                
                this.map.panTo(txLocation);
            }
        }
        
        // have txData now, either from finding, or creating
        // have a spot
        // each spot is a unique reporter
        let reporterMarker = this.reporterName__data.get(reporterName).marker;
        txData.reporterMarkerList.push(reporterMarker);
        
        let reporterLine = new google.maps.Polyline({
            path          : [txData.txLocation, reporterMarker.position],
            geodesic      : true,
            strokeColor   : 'red',
            strokeOpacity : 1.0,
            strokeWeight  : 0.75,
        });
        txData.reporterLineList.push(reporterLine);
        
        if (this.tracking)
        {
            reporterLine.setMap(this.map);
        }
    }
    
    UpdateMapInfo()
    {
        // Update map info
        let distanceTraveledMetersTotal = 0;
        
        for (let i = 1; i < this.txDataList.length; ++i)
        {
            let pointFrom = this.txDataList[i - 1].txLocation;
            let pointTo   = this.txDataList[i].txLocation;
            
            let pointFromLatLng = new google.maps.LatLng(pointFrom.lat, pointFrom.lng);
            let pointToLatLng = new google.maps.LatLng(pointTo.lat, pointTo.lng);
            
            let distanceTraveledMeters = google.maps.geometry.spherical.computeDistanceBetween(pointFromLatLng, pointToLatLng);
            distanceTraveledMetersTotal += distanceTraveledMeters;
        }
        
        let distanceTraveledMilesTotal = Math.floor(distanceTraveledMetersTotal / 1609.344);
        
        let mapStatus = "";
        mapStatus += "Traveled " + libUtl.Commas(distanceTraveledMilesTotal) + " miles<br/>";
        mapStatus += `${this.txDataList.length} transmissions<br/>`;
        mapStatus += `${this.markerListRx.length} unique reporters`;
        
        this.domMapStatus.innerHTML = mapStatus;
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
            
            // if you click this marker, show the paths
            this.CloseAllReporterPaths();
            this.OpenReporterPaths(this.txDataList[this.txDataList.length - 1]);
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
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 