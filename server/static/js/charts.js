// Reference to the Highcharts chart object.
// Has additional properties - 
// @property anomalies - Array of tuples of start, end of each anomaly.
// @property anomaliesId - Array of anomaly plot band ids. Useful for removing later.
var metricChart;
var metricChartId = "metricChart";
var minTime = 1395723600;
var dateStart = new Date(0);
dateStart.setUTCSeconds(minTime);

var metricsData; // Stores the machine, metric object.
// red, yellow, purple, green/lime
var anomalyColor='#EE454B';

// Algorithm name cache - such informative. wow.
var algorithmNameCache = {
    "MA" : "MA",
    "HMM" : "HMM",
    "NAIVE" : "NAIVE"
}

/*
 * MetricChart object.
 */
function MetricChart(chart) {
    this.chart = chart;
    this.id = metricChartId;
    this.anomalies =  [];
    this.anomaliesId = [];
}

/*
 * Enable the metrics select dropdown and show the appropriate metrics.
 */
function showMetricsForMachine(selectedMachine) {
    addSelectOptions("#metric-name", metricsData[selectedMachine]);
    $("#metric-name").attr('disabled', false);
}

MetricChart.prototype.updateData = function(data) {
    this.chart.series[0].setData(data);
}

/*
 * Updates the stats on the page - min, max, range
 */
function updateStats(data) {
    var miny = Number.POSITIVE_INFINITY, maxy = Number.NEGATIVE_INFINITY;
    var  minx = Number.POSITIVE_INFINITY, maxx = Number.NEGATIVE_INFINITY;
    var mean = 0, n = data.length, variance = 0;

    for (var i = 0;i<n;i++) {
        minx = Math.min(data[i][0], minx);
        maxx = Math.max(data[i][0], maxx);
        miny = Math.min(data[i][1], miny);
        maxy = Math.max(data[i][1], maxy);
        mean += data[i][1];
    } 

    for (var i = 0; i < n; i++) {
        variance += Math.pow(data[i][1] - mean, 2);
    }
    
    mean = mean/n;   
    variance = variance/(n-1);

    $("#stats-min").html(miny.toFixed(2));
    $("#stats-max").html(maxy.toFixed(2));
    $("#stats-range").html((maxy - miny).toFixed(2));
    $("#stats-mean").html(mean.toFixed(2));
    $("#stats-variance").html(variance.toFixed(2));
}

/*
 * Returns the machine name and metric in a JSON object.
 */
function getSelectedMetric() {
    return {
        "machine" : $("#machine-name").val(),
        "metric" : $("#metric-name").val()
    }
}

/*
 * Adds the options from the array to the select element with the given jquery selector
 * Adds the value by default. Passing addKey=true (objects) will add the keys instead.
 */
function addSelectOptions(elementSelector, data, addKey) {
    $(elementSelector).html("");
    $.each(data, function(key, value) {
            var valueToAdd = addKey ? key : value;
            $(elementSelector)
                .append($("<option></option>")
                .attr("value", valueToAdd)
                .text(valueToAdd));
    });
}

/* 
 * Adds a plot band to the chart. 
 * @param chart : Highchart object.
 * @param anomalies : Array of tuples (arrays of size 2) marking start and end of each anomaly.
 * For instance - [[1,2], [2,3], [4,5]]
 * Returns an array of plot band IDs. Also updates the chart object's anomalies/anomaliesId array.
 */
MetricChart.prototype.addAnomalies = function(anomalies) {
    var idArray = []
    console.log(anomalies);
    
    $.each(anomalies, (function(index, tuple) {
        idArray.push(index)

        // Add Plot Bands
        this.chart.xAxis[0].addPlotBand({
            from: tuple[0], 
            to: tuple[1],
            color: anomalyColor,
            id:index,
            label: {
                text: (index+1),
                verticalAlign: 'bottom',
                y: 0
            }
        });

        // Add flags
        this.chart.addSeries({
                type: 'flags',
                data: [{
                    x: (tuple[0]+tuple[1])/2,
                    title: (index+1)
                    //text: 'Information v2'
                }],
                onSeries: this.id,
                shape: 'circlepin',
                width: 20,
                showInLegend: false
        }, false);

    }).bind(this));

    this.chart.redraw();
    this.anomalies = anomalies;
    this.anomaliesId = idArray;
    return idArray;
}

/*
 * Removes anomalies from the chart. Also resets the chart object's anomaliesId array.
 * @param : chart object.
 */
MetricChart.prototype.removeAnomalies = function() {
    $.each(this.anomaliesId, (function(index, id) {
        this.chart.xAxis[0].removePlotBand(id);
    }).bind(this));

    // All series above [1] are flags. Remove them. 
    // Series [0] and [1] are the actual series and the preview below.
    while(this.chart.series.length > 2) {
        this.chart.series[2].remove();
    }

    metricChart.chart.redraw();
    this.anomalies = [];
    this.anomaliesId = [];
}

/*
 * Converts the timeseries data (list of tuples (x,y)) to the required format by doing the following:
 * Convert UNIX epoch to milliseconds by multiplying each x value with 1000.
 */
function convertTSData(tsData) {
    for(var i=0; i<tsData.length;i++) {
        tsData[i][0] = (parseInt(tsData[i][0]) + minTime)*1000;
    }
    return tsData;
}

/*
 * Converts the anomaly data (list of tuples (x,y)) to the required format by doing the following:
 * Convert UNIX epoch to milliseconds by multiplying each x and y value with 1000.
 */
function convertAnomalyData(anomalyData) {
    convertedAnomalyData = []
    for(var i=0; i<anomalyData.length;i++) {
        var startTime = (anomalyData[i][0] + minTime)*1000;
        var endTime = (anomalyData[i][1] + minTime)*1000;
        convertedAnomalyData.push([startTime, endTime]);
    }
    return convertedAnomalyData;
}

$(document).ready(function() {
    // Create the chart
    $('#chart-container').highcharts('StockChart', {
            chart: {
                    type:'line',
                    zoomType: 'x'
            },
            rangeSelector: {
                inputEnabled: $('#chart-container').width() > 480,
                        buttons: [{
                                type: 'second',
                                count: 10,
                                text: '10s'
                        }, {
                                type: 'minute',
                                count: 1,
                                text: '1m'
                        }, {
                                type: 'minute',
                                count: 60,
                                text: '1h'
                        }, {
                                type: 'day',
                                count: 1,
                                text: '1d'
                        },{
                                type: 'all',
                                text: 'All'
                        }],
                        selected: 5
                },
        yAxis: {
            title: {
                text: 'Timestamp'
            }
        },
            title: {
                text: 'Timeseries'
        },
        subtitle: {
            text: 'Built chart in ...' // dummy text to reserve space for dynamic subtitle
        },
        series: [{
                    name: 'Metric',
                    id: metricChartId,
                    pointStart: dateStart
            }]
    });

    metricChart = new MetricChart($("#chart-container").highcharts());

    $("#btn-get-metric").click(function() { 
        var selectedMetric = getSelectedMetric();
        console.log(selectedMetric);
        // show preloader
        $("#load-preloader").show("slow");
        $("#load-error").hide();
        metricChart.removeAnomalies();

        // fetch data from server
        $.ajax({
            url: "/data", 
            dataType: 'json',
            data: selectedMetric,
            success: function(response) {
                // Update the stats on the page (before converting to milliseconds.)
                updateStats(response);
                var data = convertTSData(response);
                // Remove anomalies of last data, if any.
                metricChart.updateData(data);
                $("#load-preloader").hide();
                $("#load-error").hide();
            },
            error: function(response) {
                $("#load-error").show("slow");
                $("#load-preloader").hide();
            }
        });
    });

    // Fetch the machine and metrics 
    $.getJSON("metrics", function(response) {
        metricsData = response;
        $("#machine-name").attr('disabled', false);
        addSelectOptions("#machine-name", response, true);
        showMetricsForMachine($("#machine-name").val());
    });

    // Show Metrics list
    $("#machine-name").change(function(event) { 
        showMetricsForMachine($(this).val())
    });

    // Fetch anomalies
    $("#algorithm-submit").click(function(event) { 
        var selectedAlgorithm = $("#algorithm-name").val();
        var selectedMetric = getSelectedMetric();
        var params = {};

        if (selectedAlgorithm === algorithmNameCache["MA"]) {
            var windowSize = $("#params-ma-window").val();
            var threshold = $("#params-ma-threshold").val();
            var method = algorithmNameCache["MA"];
            params = $.extend(selectedMetric, { "window" : windowSize, "threshold" : threshold, "method" : method });
        } 
        else if (selectedAlgorithm === algorithmNameCache["HMM"]) {
            var numOfStates = $("#params-hmm-states").val(); 
            var percentage = $("#params-hmm-percentage").val();
            var method = algorithmNameCache["HMM"];
            params = $.extend(selectedMetric, { "n_states" : numOfStates, "percentage" : percentage, "method" : method });
        } 
        else if (selectedAlgorithm === algorithmNameCache["NAIVE"]) {
            var deviationFactor = $("#params-naive-deviation").val();
            var method = algorithmNameCache["NAIVE"];
            console.log(deviationFactor);
            params = $.extend(selectedMetric, { "deviation_factor" : deviationFactor, "method" : method });    
        }
        else {
            throw new Exception('Not Supported');    
        }

        console.log(params);
        // Show algorithm-preloader
        $("#algorithm-preloader").show('slow');
        $("#algorithm-error").hide();

         $.ajax({
             url: "/anomalies",
             data: params,
             dataType: "json",
             success: function(response) {
                 // Update 
                 var data = convertAnomalyData(response);
                 console.log(data);
                 metricChart.removeAnomalies();
                 metricChart.addAnomalies(data);
                 $("#algorithm-preloader").hide();
                 $("#algorithm-error").hide();
             },
             error: function(response) {
                 console.log(response);
                 $("#algorithm-preloader").hide();
                 $("#algorithm-error").show('slow');
             }
         });
    });

    // Show/hide appropriate parameters
    $("#algorithm-name").change(function(event) {
        var selectedAlgorithm = event.target.value;
        var paramSelector = "#params-" + algorithmNameCache[selectedAlgorithm].toLowerCase();

        // Hide all other params div.
        $("div[id^=params]").hide('fast', function() {
            $(paramSelector).show('fast');
        });
    });
});
