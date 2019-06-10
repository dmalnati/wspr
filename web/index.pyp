<html>
    <head>
        <title>WSPR2APRS</title>
        
        <meta name="viewport" content="initial-scale=1.0, user-scalable=no" />


        <link rel='stylesheet' href='/core/css/core.css'>
        <style>
        * {
            margin: 0px;
            padding: 0px;
        }
        
        html, body {
            height: 100%;
        }
        
        body::-webkit-scrollbar { 
            display: none;
        }
        
        /******** Container of top/bottom, allowing top to stick ********/
        
        #allContent {
        }
        
        
        /******** Top Part ********/
        
        #topPartContainer {
           position: sticky;
           top: 0px;
           z-index: 1;
          
           height: 65vh;
           
           resize: vertical;
           overflow: auto;
        }
        
        #contentNotResizeHandle {
            height: calc(100% - (1.2em + 2px));
        }
        
        #queryInputPartContainer {
           position: absolute;
           top: 0px;
           z-index: 2;
           
           height: 1.9em;
           width: 90vw;
        }
        
        #mapPartContainer {
           height: 100%;
        }
        
        #map {
           height: 100%;
        }
        
        
        
        #resizeHandle {
            height: (1.2em + 2px);
            
            border-top: 1px solid black;
            border-bottom: 1px solid black;
            
            background-color: lightgrey;
        }
        

        
        /******** Bottom Part ********/
        
        #bottomPartContainer {
        }

        
        .chart {
            border: 1px solid black;
            
            height: 30vh;
            width: calc(100vw - 2px);
            
            overflow: hidden;
            display: inline-block;
        }
        
        .chartLineDouble {
            height: 30vh;
            width: 100%;
            
            /*
             * makes it so divs can be on separate lines and the newline between
             * them doesn't count as actual renderable content which messes up
             * alignment
             */
            display: flex;
        }
        
        .chartLineDouble .chart {
            height: calc(100% - 2px);
            width: calc(50% - 2px);
        }
        
        
        
        .notachart {
            text-align: center;
            background-color: lightgrey;
        }
        
        
        
        
        </style>
        
        <script src='/core/js/third-party/moment/moment.min.js'></script>
        <script type='module'>
        import * as libLoad from '/core/js/libLoad.js';
        import * as libSpotApp from '/wspr2aprs/js/libSpotApp.js';
        
        libLoad.DocEventListenerAsPromise('DOMContentLoaded').then(() => {
            let spotApp = new libSpotApp.SpotApp({
                idTimeGte                     : 'timeGte',
                idTimeLte                     : 'timeLte',
                idCallsign                    : 'callsign',
                idButtonQuery                 : 'buttonQuery',
                idMap                         : 'map',
                idMapStatus                   : 'mapStatus',
                idDashboard                   : 'dashboard',
                idChartTimeSeriesAltitudeFt   : 'chartTimeSeriesAltitudeFt',
                idChartTimeSeriesSpeedMph     : 'chartTimeSeriesSpeedMph',
                idChartTimeSeriesTemperatureF : 'chartTimeSeriesTemperatureF',
                idChartTimeSeriesMilliVolts   : 'chartTimeSeriesMilliVolts',
                idChartTimeSeriesDistance     : 'chartTimeSeriesDistance',
                idChartBubbleTimeVsDistance   : 'chartBubbleTimeVsDistance',
                idTableOfDataBubble           : 'tableOfDataBubble',
                idTableOfData                 : 'tableOfData',
            });
            
            spotApp.Run()
        });
        </script>
    </head>

    <body>

<div id='allContent'>

<div id='topPartContainer'>
    <div id='contentNotResizeHandle'>
        <div id='queryInputPartContainer'>
            <input id='timeGte' type='datetime-local'>
            <input id='timeLte' type='datetime-local'>
            <input id='callsign' type='text' placeholder='callsign'>
            <button id='buttonQuery'>Search</button>
        </div>
        
        <div id='mapPartContainer'>
            <div id='map'></div>
        </div>
        
    </div>
    
    <div id='resizeHandle'>
        <span id='mapStatus'></span>
    </div>
        
    
</div>


<div id='bottomPartContainer'>
    <div id='dashboard'>
        <div class='chartLineDouble'>
            <div id='chartBubbleTimeVsDistance' class='chart'></div>
            <div id='tableOfDataBubble' class='chart'></div>
        </div>

        <div class='chartLineDouble'>
            <div id='chartTimeSeriesAltitudeFt' class='chart'></div>
            <div id='chartTimeSeriesSpeedMph' class='chart'></div>
        </div>
        
        <div class='chartLineDouble'>
            <div id='chartTimeSeriesTemperatureF' class='chart'></div>
            <div id='chartTimeSeriesMilliVolts' class='chart'></div>
        </div>
        
        <div class='chartLineDouble'>
            <div id='chartTimeSeriesDistance' class='chart'></div>
            <div class='chart notachart'><br/><br/><br/><br/><br/>no chart here</div>
        </div>
        
        <div id='tableOfData' class='chart'></div>
    </div>
</div>

</div>

    </body>
</html>































