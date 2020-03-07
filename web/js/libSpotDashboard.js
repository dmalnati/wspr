import { Log } from '/core/js/libUtl.js';
import * as libLoad from '/core/js/libLoad.js';





////////////////////////////////////////////////////////////////////////////////
//
// Dashboard
//
////////////////////////////////////////////////////////////////////////////////


export
class SpotDashboard
{
    constructor(cfg)
    {
        this.cfg = cfg;
        
        this.dataTable = null;
        
        this.dashboard = null;
        
        this.okToDraw = false;
        
        window.addEventListener('resize', () => {
            Log("RESIZE");

            // should set a timer to come back and look at this, seemingly the event fires twice

            this.Draw()
        });
    }
    
    Load()
    {
        let scriptSrc = 'https://www.gstatic.com/charts/loader.js';
        
        let readyFn;
        let promise = new Promise((ready) => {
            readyFn = ready;
        });
        
        libLoad.LoadScriptAsPromise(scriptSrc).then(() => {
            // Load the Visualization API and the controls package.
            google.charts.load('current', {'packages':['corechart', 'controls']});

            // Set a callback to run when the Google Visualization API is loaded.
            google.charts.setOnLoadCallback(() => {
                Log("Dashboard loaded");

                this.OnLoaded();
                
                readyFn();
            });
        });
        
        return promise;
    }
    
    
    //
    // Approach
    // - want charts/graphs to update dynamically as new data is added to the
    //   underlying dataTable.
    // - unfortunately some data tables (grouped) won't update dynamically.
    // - break operation into two phases
    //
    //
    // Build
    // - libs have loaded, can start doing google-things now.
    // - create data table (empty)
    // - create derived data tables which need to be re-constituted (not deleted) later
    // - create, configure charts and associate to DOM
    //
    // Update
    // - new data has arrived
    // - push into data table
    // - update any derrived data tables
    //
    //
    
    Reset()
    {
        // blank out data table.
        // this will automatically blank out all charts relying on this data.
        this.dataTable.removeRows(0, this.dataTable.getNumberOfRows());
        
        // tell derivative charts to reconstitute themselves against no data
        this.UpdateDerivativeCharts();
        
        // refresh visually
        this.DrawInternal();
    }
    
    
    OnLoaded()
    {
        this.BuildDataTable();
        this.BuildRealtimeCharts();
        this.BuildDerivativeCharts();
        
        this.DrawInternal();
    }
    
    BuildDataTable()
    {
        // Build data table
        this.dataTable = new google.visualization.DataTable();
        
        this.dataTable.addColumn('datetime', 'time');
        this.dataTable.addColumn('number',   'altitudeFt');
        this.dataTable.addColumn('number',   'speedMph');
        this.dataTable.addColumn('number',   'temperatureF');
        this.dataTable.addColumn('number',   'milliVolts');
        this.dataTable.addColumn('string',   'reporter');
        this.dataTable.addColumn('number',   'miles');
    }
    
    BuildRealtimeCharts()
    {
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
    }
    
    BuildDerivativeCharts()
    {
        this.BuildTimeVsDistanceChart();
    }
    
    BuildTimeVsDistanceChart()
    {
        // Hold onto a date object just so we can use it over and over to create
        // a time-of-day value all on the same date.
        let dateTmp = new Date();
        
        //
        // Create:
        // - col 0: time-of-day (grouped, bucketed)
        // - col 1: distance (grouped, bucketed)
        // - col 2: count
        //
        this.dataTableTimeVsDistance = google.visualization.data.group(
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
                    label: 'timeOfDay',
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
                    label: 'distanceMiles',
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
        this.dataTableTimeVsDistanceView = new google.visualization.DataView(this.dataTableTimeVsDistance);
        this.dataTableTimeVsDistanceView.setColumns([
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

        this.chartBubbleTimeVsDistance   = this.MakeChartBubbleTimeOfDay(this.cfg.idChartBubbleTimeVsDistance, [0, 1, 2, 3, 4]);
        this.chartBubbleTimeVsDistance.setDataTable(this.dataTableTimeVsDistanceView);
        
        this.chartTableOfDataBubble = this.MakeChartTableOfData(this.cfg.idTableOfDataBubble);
        this.chartTableOfDataBubble.setDataTable(this.dataTableTimeVsDistanceView);
    }
    
    AddSpotList(spotList)
    {
        this.UpdateDataTable(spotList);
        
        this.UpdateDerivativeCharts();
        
        // return;
        this.DrawInternal();
    }
    
    UpdateDataTable(spotList)
    {
        for (let spot of spotList)
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
    }
    
    UpdateDerivativeCharts()
    {
        this.BuildDerivativeCharts();
    }
    
    DrawInternal()
    {
        this.okToDraw = true;
        this.Draw();
    }
    
    Draw()
    {
        if (this.okToDraw)
        {
            Log("Draw Start");
            this.chartTimeSeriesAltitude.draw();
            this.chartTimeSeriesSpeedMph.draw();
            //this.chartTimeSeriesTemperatureF.draw();
            //this.chartTimeSeriesMilliVolts.draw();
            //this.chartTimeSeriesDistance.draw();
            this.chartBubbleTimeVsDistance.draw();
            //this.chartTableOfDataBubble.draw();
            this.chartTableOfData.draw();
            Log("Draw End");
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
    

    MakeChartBubbleTimeOfDay(id, colList)
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
                'height': '100%',
                'width' : '100%',
            },
        });
        
        return chart;
    }
    

}











































