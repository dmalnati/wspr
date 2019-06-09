


// https://www.chartjs.org/docs/latest/
function Example()
{
    function Load()
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
    }

    function MakeChart()
    {
        Load().then(() => {
            chart = new ChartLinearSeries('container');
            chart.CreateEmpty();
            chart.Draw();
            chart.AddData(1, 2);
            chart.Draw();
        });
    }
}



export
class ChartLinearSeries
{
    constructor(domId)
    {
        this.domId = domId;
        
        this.data = [];
    }
    
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
                    }
                ],
            },
            options: {
                maintainAspectRatio: false,
                scales: {
                    xAxes: [
                        {
                            type: 'linear',
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
