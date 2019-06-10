<html>
    <head>
        <title>WSPR2APRS</title>

        <link rel='stylesheet' href='/core/css/core.css'>
        <style>
        .chart {
            border: 1px solid black;
            width: 50%;
            height: 300px;
            overflow: hidden;
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
                idButtonShowAllRxMarkers      : 'buttonShowAllRxMarkers',
                idButtonHideAllRxMarkers      : 'buttonHideAllRxMarkers',
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
<input id='timeGte' type='datetime-local'>
<input id='timeLte' type='datetime-local'>
<input id='callsign' type='text'>
<button id='buttonQuery'>Search</button>

<br/>

<div id='map' style='height:400px;'></div>
<button id='buttonShowAllRxMarkers'>Show RX</button>
<button id='buttonHideAllRxMarkers'>Hide RX</button>

<br/>
<br/>
<br/>



<div id='dashboard'>
    <div id='chartBubbleTimeVsDistance' class='chart'></div>
    <div id='tableOfDataBubble'></div>

    
    <div id='chartTimeSeriesAltitudeFt' class='chart'></div>
    <div id='chartTimeSeriesSpeedMph' class='chart'></div>
    <div id='chartTimeSeriesTemperatureF' class='chart'></div>
    <div id='chartTimeSeriesMilliVolts' class='chart'></div>
    <div id='chartTimeSeriesDistance' class='chart'></div>
    <div id='tableOfData'></div>
</div>






    <!--Div that will hold the dashboard-->
    <div id="dashboard_div">
      <!--Divs that will hold each control and chart-->
      <div id="filter_div"></div>
      <div id="chart_div"></div>
    </div>



    </body>
</html>































