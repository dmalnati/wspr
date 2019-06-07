<html>
    <head>
        <title>WSPR2APRS</title>

        <link rel='stylesheet' href='/core/css/core.css'>
        <style>
        </style>

        <script src="/core/js/libWS.js"></script>
        <script src='/core/js/third-party/moment/moment.min.js'></script>








<script>
'use strict'




class Spot
{
    constructor(spotData)
    {
        this.spotData = spotData;
    }

    GetTime()
    {
        return this.spotData['TIME'];
    }

    GetReporterPoint()
    {
        return { lat: this.spotData['RLAT'], lng: this.spotData['RLNG'] };
    }

    GetTransmitterPoint()
    {
        return { lat: this.spotData['LAT'], lng: this.spotData['LNG'] };
    }
}

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


class SpotMap extends WSEventHandler
{
    constructor(idContainer)
    {
        super();
        
        this.idContainer = idContainer;
        this.map = null;
        this.markerList = []
        
        // mid-eastern seaboard
        this.initialCenterLocation = { lat: 36.521387, lng: -76.303034 };
        this.initialZoom           = 5;
        
        this.ws = null;

        // Organize spots
        this.time__txEvent = {};
    }

    Start()
    {
        console.log("Start");
        
        this.map = new google.maps.Map(document.getElementById(this.idContainer), {
            center: this.initialCenterLocation,
            zoom: this.initialZoom
        });
    }

    AddMarker(point)
    {
        let marker = new google.maps.Marker({position: point});
        
        console.log("Adding marker: " + point.lat + " " + point.lng);
        
        marker.setMap(this.map);
        
        this.markerList.push(marker);

        this.map.setCenter(point);
    }
    
    AddLine(point1, point2)
    {
        let line = new google.maps.Polyline({
            path: [point1, point2],
            geodesic: true,
            strokeColor: '#FF0000',
            strokeOpacity: 1.0,
            strokeWeight: 2
        });
        
        line.setMap(this.map);
    }
    
    Query()
    {
        this.ws = WSManager.Connect(this, "/wspr2aprs/ws/spotquery");
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
        console.log(msg);
        
        let spotDataList = msg;
        for (let spotData of spotDataList)
        {
            let rLat = spotData["RLAT"];
            let rLng = spotData["RLNG"];
            
            let point1 = {lat: rLat, lng: rLng};
            this.AddMarker(point1);
            
            let lat = spotData["LAT"];
            let lng = spotData["LNG"];
            
            let point2 = { lat: lat, lng: lng };
            this.AddMarker(point2);
            
            this.AddLine(point1, point2);


            // Organize spot data
            let spot = new Spot(spotData);

            let time = spot.GetTime();
            if (!(time in this.time__txEvent))
            {
                let txEvent = new TxEvent();
                txEvent.SetTime(time);

                this.time__txEvent[time] = txEvent;
            }

            let txEvent = this.time__txEvent[time];

            txEvent.AddSpot(spot);
        }
        
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

let spotMap = new SpotMap('map');






</script>





















        <script>
function OnLoad()
{
console.log("OnLoad");
    SetInitialTimes();
}



function OnSearch()
{
    console.log(document.getElementById('timeGte').value);
    console.log(document.getElementById('timeLte').value);
    console.log(document.getElementById('callsign').value);

}

function SetTime(id, time)
{
    document.getElementById(id).value = time;
}

function SetInitialTimes()
{
    formatStr = 'YYYY-MM-DD[T]HH:mm:ss';

    SetTime('timeGte', moment().subtract(1, "hour").format(formatStr));
    SetTime('timeLte', moment().add(1, "hour").format(formatStr));
}

function AddLatLng()
{


var point = {lat: -25.344, lng: 131.036};
var marker = new google.maps.Marker({position: point, map: map});

map.setCenter(point);

}



        </script>
    </head>

    <body onload='OnLoad();'>


<div id='map' style='height:400px;'></div>

<br/>
<br/>
<button id='buttonQuery'>Query</button>
<br/>
<br/>

<input id='timeGte' type='datetime-local'>
<input id='timeLte' type='datetime-local'>
<input id='callsign' type='text'>
<button onclick='OnSearch()'>Search</button>
<br/>

Lat <input id='lat' type='text'>
Lng <input id='lng' type='text'>
<button onclick='AddLatLng()'>Add Point</button>


    </body>

	<script>

var map;


function OnMapsLoad()
{
    spotMap.Start();
    
    document.getElementById('buttonQuery').onclick = function(){ spotMap.Query(); }
}

	</script>
        <script src='https://maps.googleapis.com/maps/api/js?key=AIzaSyAXdaFYzQw9dxu-dG7t-LDL1jG7jhFjr8g&callback=OnMapsLoad'></script>
</html>













