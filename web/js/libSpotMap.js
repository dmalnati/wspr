import { Log, Commas } from '/core/js/libUtl.js';
import * as libLoad from '/core/js/libLoad.js';


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
        
        // Initial state of map
        this.initialCenterLocation = { lat: 36.521387, lng: -76.303034 };
        this.initialZoom           = 4;
        
        // hold all map elements regardless of other access routes
        this.mapElementList = [];
    }
    
    TrackMapElement(mapElement)
    {
        this.mapElementList.push(mapElement);
    }
    
    DiscardAllMapElements()
    {
        for (let mapElement of this.mapElementList)
        {
            mapElement.setMap(null);
        }
    }

    Load()
    {
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
            Log("SpotMap Loaded");
            
            this.Reset();
            
            readyFn()
        });
        
        return promise;
    }
    
    Reset()
    {
        // Keep state
        this.reporterName__data = new Map();
        this.markerListRx = [];
        this.txDataList = [];
        this.infoWindowList = [];

        this.tracking = true;
        
        if (this.map)
        {
            this.DiscardAllMapElements();
        }
        else
        {
            // Load map instance
            this.map = new google.maps.Map(document.getElementById(this.idContainer), {
                center: this.initialCenterLocation,
                zoom: this.initialZoom,
                mapTypeId: google.maps.MapTypeId.TERRAIN,
                gestureHandling: 'greedy',
                
                zoomControl: false,
                mapTypeControl: false,
                scaleControl: true,
                streetViewControl: false,
                rotateControl: false,
                fullscreenControl: true,
            });
        }
        
        // Tie in
        this.SetUpHandles();
        this.SetUpHandlers();
        this.UpdateMapInfo();
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
            if (infoWindow.map != null)
            {
                infoWindow.close();
            }
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
                if (reporterLine.getMap() != null)
                {
                    reporterLine.setMap(null);
                }
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
        }
        this.UpdateMapInfo();
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
                icon     : '/wspr/img/tower.png',
            });
            this.TrackMapElement(marker);
            
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
                this.TrackMapElement(line);
                
                line.setMap(this.map);
            }
            
            // Do remaining UI work for this spot regardless of prior spots
            
            // Marker
            let marker = new google.maps.Marker({
                position : txLocation,
                icon     : '/wspr/img/balloon.png',
            });
            this.TrackMapElement(marker);
            
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
            this.TrackMapElement(dot);
            
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
            txData.spotList             = [];
            
            this.txDataList.push(txData);
            
            if (this.tracking)
            {
                new google.maps.event.trigger(marker, 'click');
                
                this.CloseAllReporterPaths();
                
                this.map.panTo(txLocation);
            }
        }
        
        txData.spotList.push(spot);
        
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
        this.TrackMapElement(reporterLine);
        txData.reporterLineList.push(reporterLine);
        
        if (this.tracking)
        {
            reporterLine.setMap(this.map);
        }
        
        this.SetInfoWindow(txData);
    }
    
    SetInfoWindow(txData, spot)
    {
        let status = "";
        
        let spotFirst = txData.spotList[0];
        
        status += txData.txTime + "<br/>";
        status += `${spotFirst.GetSpeedMph()} MPH, ${Commas(spotFirst.GetAltitudeFt())} ft`;
        status += `, ${spotFirst.GetTemperatureF()} F, ${spotFirst.GetVoltage()/1000} V<br/>`;
        status += `${txData.spotList.length} reports<br/>`;
        status += "<hr>";
        
        
        // sorted table of reporter, distance, snr, freq, drift, 
        let spotList = txData.spotList;
        spotList.sort((a, b) => {
            return this.CalcDistMilesBetween(b.GetLocationTransmitter(), b.GetLocationReporter()) -
                   this.CalcDistMilesBetween(a.GetLocationTransmitter(), a.GetLocationReporter());
        });
        
        
        status += `<div class='spotListContainer'
                        onwheel='CaptureOverScrollOnWheel(this, event);'
                   >`;
        status += "<table>";
        status += "<style>";
        status += `
        
        .spotListContainer {
            
            /* I want to show the header plus 5 rows */
            /* upper/lower padding on each is equal to 1px */
            /* em = current font size, ex = the x-height of the current font */
            /* the fact the header is bolded seems to throw off my calc, so
               throw in another few px for the hell of it */
            
            max-height: calc((4 * (2px + 1em)) + 2px);
            
            overflow-y: scroll;
        }
        
        /* no scrollbar */
        .spotListContainer::-webkit-scrollbar { 
            display: none;
        }
        
        table {
            border-collapse: collapse;
        }
        
        th, td {
            padding-left: 10px;
            padding-right: 10px;
        }
        
        tr th:first-child, td:first-child {
            padding-left: 0px;
        }
        
        tr th:last-child, td:last-child {
            padding-right: 0px;
        }
        
        
                  `;
        status += "</style>";

        
        status += "<tr><th>Reporter</th><th>DistanceMI</th><th>SNR</th><th>Freq</th><th>Drift</th></tr>";
        for (let spot of spotList)
        {
            let distanceMiles = Math.round(this.CalcDistMilesBetween(spot.GetLocationTransmitter(), spot.GetLocationReporter()));
            
            status += "<tr>"
            
            status += `<td>${spot.GetReporter()}</td>`;
            status += `<td style='text-align: right;'>${Commas(distanceMiles)}</td>`;
            status += `<td style='text-align: right;'>${spot.GetSNR()}</td>`;
            status += `<td style='text-align: right;'>${spot.GetFrequency()}</td>`;
            status += `<td style='text-align: right;'>${spot.GetDrift()}</td>`;
            
            status += "</tr>";
        }
        status += "</table>";
        status += "</div>";
        
        txData.infoWindow.setContent(status);
    }
    
    // takes { lat: lat, lng: lng }
    CalcDistMilesBetween(point1, point2)
    {
        let pointFromLatLng = new google.maps.LatLng(point1.lat, point1.lng);
        let pointToLatLng = new google.maps.LatLng(point2.lat, point2.lng);
        
        let distanceMeters = google.maps.geometry.spherical.computeDistanceBetween(pointFromLatLng, pointToLatLng);
        let distanceMiles  = distanceMeters / 1609.344;

        return distanceMiles;
    }
    
    UpdateMapInfo()
    {
        // Update map info
        let distanceTraveledMilesTotal = 0;
        
        for (let i = 1; i < this.txDataList.length; ++i)
        {
            let pointFrom = this.txDataList[i - 1].txLocation;
            let pointTo   = this.txDataList[i].txLocation;
            
            let distanceTraveledMiles = this.CalcDistMilesBetween(pointFrom, pointTo);
            distanceTraveledMilesTotal += distanceTraveledMiles;
        }
        
        distanceTraveledMilesTotal = Math.round(distanceTraveledMilesTotal);
        
        let mapStatus = "";
        mapStatus += `Traveled ${Commas(distanceTraveledMilesTotal)} miles, `;
        mapStatus += `${this.txDataList.length} transmissions, `;
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
        this.TrackMapElement(infoWindow);
        
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
        this.TrackMapElement(infoWindow);
        
        marker.addListener('click', () => {
            this.CloseAllInfoWindows();
            infoWindow.open(this.map, marker);
        });
        
        this.infoWindowList.push(infoWindow);
        
        return infoWindow;
    }
 }
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
