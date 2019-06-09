import * as libUtl from '/core/js/libUtl.js';
import * as libLoad from '/core/js/libLoad.js';
import * as libWS from '/core/js/libWS.js';

//import * as moment2 from '/core/js/third-party/moment/moment.min.js';


////////////////////////////////////////////////////////////////////////////////
//
// Spot
//
////////////////////////////////////////////////////////////////////////////////

export
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

    GetLocationReporter()
    {
        return {
            lat: parseFloat(this.spotData['RLAT']),
            lng: parseFloat(this.spotData['RLNG']),
        };
    }

    GetLocationTransmitter()
    {
        return {
            lat: parseFloat(this.spotData['LAT']),
            lng: parseFloat(this.spotData['LNG']),
        };
    }
    
    GetMiles()
    {
        return parseInt(this.spotData['MI']);
    }
    
    GetAltitudeFt()
    {
        return parseInt(this.spotData['ALTITUDE_FT']);
    }
    
    GetSpeedMph()
    {
        return parseInt(this.spotData['SPEED_MPH']);
    }
    
    GetTemperatureC()
    {
        return parseInt(this.spotData['TEMPERATURE_C']);
    }
    
    GetTemperatureF()
    {
        return Math.round((this.GetTemperatureC() * 9.0 / 5.0) + 32);
    }
    
    GetVoltage()
    {
        return parseInt(this.spotData['VOLTAGE']);
    }
    
    GetReporter()
    {
        return this.spotData['REPORTER'];
    }
}


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
        this.markerList = []
        
        // mid-eastern seaboard
        this.initialCenterLocation = { lat: 36.521387, lng: -76.303034 };
        this.initialZoom           = 5;
        
        // Organize spots
        this.time__locTx = {};
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
                zoom: this.initialZoom
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
 
 
 
////////////////////////////////////////////////////////////////////////////////
//
// Dashboard
//
////////////////////////////////////////////////////////////////////////////////

export
class Dashboard
{
    constructor(cfg)
    {
        this.cfg = cfg;
        
        this.spotList = [];
        this.dataTable = null;
        
        this.dashboard = null;
        
        this.okToDraw = false;
    }
    
    Load()
    {
        console.log("Load");
        
        let scriptSrc = 'https://www.gstatic.com/charts/loader.js';
        
        let readyFn;
        let promise = new Promise((ready) => {
            readyFn = ready;
        });
        
        libLoad.LoadScriptAsPromise(scriptSrc).then(() => {
            console.log("Google Charts Loader loaded, creating dashboard");
            
            // Load the Visualization API and the controls package.
            google.charts.load('current', {'packages':['corechart', 'controls']});

            // Set a callback to run when the Google Visualization API is loaded.
            google.charts.setOnLoadCallback(() => {
                this.OnChartsReady();
                readyFn();
            });

        });
        
        return promise;
    }
    
    AddSpotList(spotList)
    {
        this.spotList.push(...spotList);
    }
    
    OnChartsReady()
    {
        console.log("Charts ready, building dashboard");
        
        this.dataTable = new google.visualization.DataTable();
        
        this.dataTable.addColumn('datetime', 'time');
        this.dataTable.addColumn('number', 'altitudeFt');
        this.dataTable.addColumn('number', 'speedMph');
        this.dataTable.addColumn('number', 'temperatureF');
        this.dataTable.addColumn('number', 'milliVolts');
        this.dataTable.addColumn('string', 'reporter');
        this.dataTable.addColumn('number', 'miles');
        
        for (let spot of this.spotList)
        {
            this.dataTable.addRow([
                new Date(Date.parse(spot.GetTime())),
                spot.GetAltitudeFt(),
                spot.GetSpeedMph(),
                spot.GetTemperatureF(),
                spot.GetVoltage(),
                spot.GetReporter(),
                spot.GetMiles(),
            ]);
        }
        
        
        
        
        
        
        // Build charts
        this.chartTimeSeriesAltitude     = this.MakeChartTimeSeries(this.cfg.idChartTimeSeriesAltitudeFt,   [0, 1]);
        this.chartTimeSeriesSpeedMph     = this.MakeChartTimeSeries(this.cfg.idChartTimeSeriesSpeedMph,     [0, 2]);
        this.chartTimeSeriesTemperatureF = this.MakeChartTimeSeries(this.cfg.idChartTimeSeriesTemperatureF, [0, 3]);
        this.chartTimeSeriesMilliVolts   = this.MakeChartTimeSeries(this.cfg.idChartTimeSeriesMilliVolts,   [0, 4]);
        this.chartTimeSeriesDistance     = this.MakeChartTimeSeries(this.cfg.idChartTimeSeriesDistance,     [0, 6]);
        
        this.chartTableOfData            = this.MakeChartTableOfData(this.cfg.idTableOfData);
        
        // Assign data table
        this.chartTimeSeriesAltitude.setDataTable(this.dataTable);
        this.chartTimeSeriesSpeedMph.setDataTable(this.dataTable);
        this.chartTimeSeriesTemperatureF.setDataTable(this.dataTable);
        this.chartTimeSeriesMilliVolts.setDataTable(this.dataTable);
        this.chartTimeSeriesDistance.setDataTable(this.dataTable);
        
        this.chartTableOfData.setDataTable(this.dataTable);
        
        
        
        
        
        // Hold onto a date object just so we can use it over and over to create
        // a time-of-day value all on the same date.
        let dateTmp = new Date();
        
        //
        // Create:
        // - col 0: time-of-day (grouped, bucketed)
        // - col 1: distance (grouped, bucketed)
        // - col 2: count
        //
        let dt2 = google.visualization.data.group(
            this.dataTable,
            // group-by list
            [
                // convert the time to time-of-day, bucketed
                //{
                //    label: 'time',
                //    column: 0,
                //    modifier: (date) => {
                //        let BUCKET_SIZE = 30;
                //        
                //        let hours = date.getHours();
                //        let minutes = Math.floor(date.getMinutes() / BUCKET_SIZE) * BUCKET_SIZE;
                //        let seconds = 0;
                //        
                //        return new Date(dateTmp.setHours(hours, minutes, seconds));
                //    },
                //    type: 'datetime',
                //},
                {
                    label: 'time',
                    column: 0,
                    modifier: (date) => {
                        let BUCKET_SIZE = 30;
                        
                        let hours = date.getHours();
                        let minutes = Math.floor(date.getMinutes() / BUCKET_SIZE) * BUCKET_SIZE;
                        let seconds = 0;
                        
                        return [hours, minutes, seconds];
                    },
                    type: 'timeofday',
                },
                // miles, grouped into buckets
                {
                    label: 'miles',
                    column: 6,
                    modifier: (miles) => {
                        let BUCKET_SIZE = 250;
                        
                        return Math.floor(miles / BUCKET_SIZE) * BUCKET_SIZE;
                    },
                    type: 'number',
                },
            ],
            // columns, aggregate each by the group-by above
            [
                // really just count the two above
                {
                    label: 'count',
                    column: 6,
                    aggregation: google.visualization.data.count,
                    type: 'number',
                }
            ]
        );
        
        
        // Data View
        
        // For the bubble, I need:
        // - 1 row per bubble
        //   - col 0: 'string' ID of each bubble -- call it ... count
        //   - col 1: 'number' x-axis time
        //   - col 2: 'number' y-axis distance
        //   - col 3: 'string' color (group, really, of which multiple IDs can be a part, call it thousand-mile)
        //   - col 4: 'number' size of dot
        let dataView = new google.visualization.DataView(dt2);
        dataView.setColumns([
            {
                label: 'bubbleName',
                type: 'string',
                calc: (dataTable, rowIdx) => {
                    return dataTable.getValue(rowIdx, 2).toString();
                },  
            },
            0,
            1,
            {
                label: 'colorName',
                type: 'string',
                calc: (dataTable, rowIdx) => {
                    let BUCKET_SIZE = 1000;
                    
                    let distance = dataTable.getValue(rowIdx, 1);
                    
                    return (Math.floor(distance / BUCKET_SIZE) * BUCKET_SIZE).toString();
                },
            },
            2,
        ]);

        

        this.chartBubbleTimeVsDistance   = this.MakeChartBubble(this.cfg.idChartBubbleTimeVsDistance, [0, 1, 2, 3, 4]);
        this.chartBubbleTimeVsDistance.setDataTable(dataView);
        
        
        this.chartTableOfDataBubble = this.MakeChartTableOfData(this.cfg.idTableOfDataBubble);
        this.chartTableOfDataBubble.setDataTable(dataView);
        
        
        
        // render
        this.okToDraw = true;
        this.Draw();
    }
    
    Draw()
    {
        if (this.okToDraw)
        {
            this.chartTimeSeriesAltitude.draw();
            this.chartTimeSeriesSpeedMph.draw();
            this.chartTimeSeriesTemperatureF.draw();
            this.chartTimeSeriesMilliVolts.draw();
            this.chartTimeSeriesDistance.draw();
            this.chartBubbleTimeVsDistance.draw();
            
            this.chartTableOfDataBubble.draw();
            
            this.chartTableOfData.draw();
        }
    }
    
    
    MakeChartTimeSeries(id, colList)
    {
        // time format
        // http://userguide.icu-project.org/formatparse/datetime
        
        let chart = new google.visualization.ChartWrapper({
            'chartType': 'AreaChart',
            'containerId': id,
            'options': {
                'theme' : 'maximized',
                'legend': {
                    'position': 'in',
                    'alignment': 'center',
                    'textStyle': {
                        'auraColor': 'none',
                    },
                },
                'explorer': {
                    'axis': 'horizontal',
                    'actions': ['dragToZoom', 'rightClickToReset'],
                },
                'pointSize' : 1,
                'hAxis' : {
                    'format' : 'MMM d,\nh:mma',
                    'textStyle': {
                        'auraColor': 'none',
                    },
                },
                'vAxis': {
                    'minValue': 0,
                    'textStyle': {
                        'auraColor': 'none',
                    },
                    'viewWindowMode': 'pretty',
                },
                'tooltip' : {
                    'isHtml' : true,
                },
            },
            'view': {
                'columns' : colList,
            },
        });
        
        return chart;
    }
    

    MakeChartBubble(id, colList)
    {
        // time format
        // http://userguide.icu-project.org/formatparse/datetime
        
        let chart = new google.visualization.ChartWrapper({
            'chartType': 'BubbleChart',
            'containerId': id,
            'options': {
                'bubble': {
                    'textStyle': {
                        'auraColor': 'none',
                    },
                },
                
                
                
                
                'theme' : 'maximized',
                'legend': {
                    'position': 'in',
                    'alignment': 'center',
                    'textStyle': {
                        'auraColor': 'none',
                    },
                },
                'explorer': {
                    'axis': 'horizontal',
                    'actions': ['dragToZoom', 'rightClickToReset'],
                },

                'pointSize' : 1,
                'hAxis' : {
                    'textStyle': {
                        'auraColor': 'none',
                    },
                    'viewWindow': {
                        'min': [0, 0, 0],
                        'max': [24, 0, 0],
                    },
                },
                'vAxis': {
                    'minValue': 0,
                    'textStyle': {
                        'auraColor': 'none',
                    },
                    'viewWindowMode': 'pretty',
                },
                'tooltip' : {
                    'isHtml' : true,
                },
            },
            'view': {
                'columns' : colList,
            },
        });
        
        return chart;
    }
    
    
    
        
    MakeChartTableOfData(id)
    {
        let chart = new google.visualization.ChartWrapper({
            'chartType': 'Table',
            'containerId': id,
            'options': {
                'height': 300,
            },
        });
        
        return chart;
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
        this.spotMap = new SpotMap(cfg.idMap);
        
        // Dashboard
        this.dash = new Dashboard(cfg);
        
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
        
        this.SetInitialTimes();
        
        
        // wait for map to be ready, then enable interactive elements
        console.log("Waiting for SpotMap to load");
        this.spotMap.Load().then(() => {
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

    SetInitialTimes()
    {
        let formatStr = 'YYYY-MM-DD[T]HH:mm:ss';

        this.dom.timeGte.value = moment().subtract(1, "hour").format(formatStr);
        this.dom.timeLte.value = moment().add(1, "hour").format(formatStr);
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
            let spot = new Spot(spotData);
            
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
        this.dash.Load();
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






