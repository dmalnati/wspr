import { Log } from '/core/js/libUtl.js';
import * as libLoad from '/core/js/libLoad.js';





////////////////////////////////////////////////////////////////////////////////
//
// Dashboard
//
////////////////////////////////////////////////////////////////////////////////



class ChartTimeSeries
{
    constructor(domId)
    {
        this.domId = domId;
        
        this.data = [];
    }
    
    // https://www.chartjs.org/docs/latest/axes/cartesian/time.html
    CreateEmpty()
    {
        let domContainer = document.getElementById(this.domId);
        
        let canvas =  document.createElement('canvas');
        
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        
        this.ctx = canvas.getContext('2d');
        
        domContainer.appendChild(canvas);
        
        this.chart = new Chart(this.ctx, {
            type: 'line',
            data: {
                datasets: [
                    {
                        data: this.data,
                        label: 'data',
                        type: 'line',
                        pointRadius: 0,
                        fill: true,
                        backgroundColor: Chart.helpers.color('rgb(255, 99, 132)').alpha(0.5).rgbString(),
                        borderColor: 'rgb(255, 99, 132)',
                    }
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    xAxes: [
                        {
                            type: 'time',
                            distribution: 'linear', // space out relative to time not sample count

                            bounds: 'data',

                            time: {
                                unit: 'hour',

                                displayFormats: {
                                    hour: 'MM-DD HH:mm'
                                }
                            },

                            ticks: {
                                autoSkip: true
                            }
                        }
                    ],
                    yAxes: [
                        {
                            type: 'linear',
                        }
                    ],
                },
            },
        });
    }
    
    AddData(x, y)
    {
        this.data.push({ x: x, y: y });
    }
    
    Draw()
    {
        this.chart.update();
    }
}



class ChartBubbleTimeSeries
{
    constructor(domId)
    {
        this.domId = domId;
        
        this.data = [];
    }
    
    // https://www.chartjs.org/docs/latest/axes/cartesian/time.html
    CreateEmpty()
    {
        let domContainer = document.getElementById(this.domId);
        
        let canvas =  document.createElement('canvas');
        
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        
        this.ctx = canvas.getContext('2d');
        
        domContainer.appendChild(canvas);
        
        this.chart = new Chart(this.ctx, {
            type: 'bubble',
            data: {
                datasets: [
                    {

                        // Will probably need to consider the x-axis a 'category'
                        // where the visible labels are the times of day.

                        // also the series data needs to be pre-calculated.
                        // This entire class needs to be extended to be a chart
                        // manager of types, knowing what it is here to do and
                        // just be a dumping ground of spot data which gets
                        // turned into the right stuff.

                        // can you add series dynamically?  that will be necessary
                        // if you want to discover new distances and consider them
                        // different series (for coloring and labeling purposes).

                        //data: this.data,
                        data: [
                            {
                                x: new Date(Date.parse('2019-06-25 10:52')),
                                y: 3000,
                                r: 3
                            },
                            {
                                x: new Date(Date.parse('2019-06-22 10:22')),
                                y: 4000,
                                r: 5
                            },
                        ],
                        label: 'data',
                        backgroundColor: Chart.helpers.color('rgb(255, 99, 132)').alpha(0.5).rgbString(),
                        borderColor: 'rgb(255, 99, 132)',
                    }
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    xAxes: [
                        {
                            type: 'time',
                            distribution: 'linear', // space out relative to time not sample count

                            // align chart around the ticks rather than the data
                            bounds: 'ticks',

                            time: {
                                unit: 'hour',

                                displayFormats: {
                                    hour: 'HH:mm'
                                }
                            },

                            ticks: {
                                autoSkip: true
                            }
                        }
                    ],
                    yAxes: [
                        {
                            type: 'linear',
                        }
                    ],
                },
            },
        });
    }
    
    AddData(x, y)
    {
        this.data.push({ x: x, y: y });
    }
    
    Draw()
    {
        this.chart.update();
    }
}





export
class SpotDashboard
{
    constructor(cfg)
    {
        this.cfg = cfg;

        this.chartTimeSeriesAltitude = null;
    }
    
    Load()
    {
        let scriptSrc = 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.8.0/Chart.bundle.min.js';
        
        let readyFn;
        let promise = new Promise((ready) => {
            readyFn = ready;
        });
        
        libLoad.LoadScriptAsPromise(scriptSrc).then(() => {
            console.log("Chart loaded");
            
            readyFn()
        });
        
        return promise;
    }
    
    
    Reset()
    {
        this.OnLoaded();
    }
    
    
    OnLoaded()
    {
        this.BuildRealtimeCharts();
        
        this.Draw();
    }
    
    
    BuildRealtimeCharts()
    {
        this.chartTimeSeriesAltitude = new ChartTimeSeries(this.cfg.idChartTimeSeriesAltitudeFt);
        this.chartTimeSeriesAltitude.CreateEmpty();
        this.ChartBubbleTimeSeries = new ChartBubbleTimeSeries(this.cfg.idChartBubbleTimeVsDistance);
        this.ChartBubbleTimeSeries.CreateEmpty();
    }
    
    
    AddSpotList(spotList)
    {
        let timeUnixLast = null;
        for (let spot of spotList)
        {
            let timeUnix = Date.parse(spot.GetTime());

            if (timeUnix != timeUnixLast)
            {
                this.chartTimeSeriesAltitude.AddData(new Date(timeUnix),
                                                     spot.GetAltitudeFt());
                
                timeUnixLast = timeUnix;
            }
        }
        
        this.Draw();
    }
    
    Draw()
    {
        this.chartTimeSeriesAltitude.Draw();
    }
    
    


}











































