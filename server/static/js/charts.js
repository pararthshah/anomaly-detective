// Reference to the Highcharts chart object.
// Has additional properties - 
// @property anomalies - Array of tuples of start, end of each anomaly.
// @property anomaliesId - Array of anomaly plot band ids. Useful for removing later.
var metricChart;
var metricChartId = "metricChart";

var metricsData; // Stores the machine, metric object.
// red, yellow, purple, green/lime
var anomalyColor='#EE454B';

// Algorithm name cache - such informative. wow.
var algorithmNameCache = {
    "MA" : "MA",
    "HMM" : "HMM"
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
        console.log(id);
        this.chart.xAxis[0].removePlotBand(id);
    }).bind(this));

    // All series above [0] are flags. Remove them.
    while(this.chart.series.length > 1) {
        this.chart.series[1].remove();
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
        tsData[i][0] *= 1000;
    }
}

/*
 * Converts the anomaly data (list of tuples (x,y)) to the required format by doing the following:
 * Convert UNIX epoch to milliseconds by multiplying each x and y value with 1000.
 */
function convertAnomalyData(anomalyData) {
    for(var i=0; i<anomalyData.length;i++) {
        anomalyData[i][0] *= 1000;
        anomalyData[i][1] *= 1000;
    }
}

$(document).ready(function() {
    $(function() {
        $.getJSON('http://www.highcharts.com/samples/data/jsonp.php?filename=large-dataset.json&callback=?', function(data) {
            // Create a timer
            var start = + new Date();

            // Create the chart
            $('#chart-container').highcharts('StockChart', {
                    chart: {
                        type:'line',
                        events: {
                            load: function(chart) {
                                this.setTitle(null, {
                                    text: 'Built chart in '+ (new Date() - start) +'ms'
                                });
        
                                metricChart = new MetricChart($("#chart-container").highcharts());
                            }
                        },
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
                                selected: 3
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
                            data: data,
                }]
            });
        });

    });

    $("#btn-get-metric").click(function() { 
        var selectedMetric = getSelectedMetric();
        console.log(selectedMetric);
        // show preloader
        $("#loader-preloader").show("slow");
        $("#load-error").hide();

        // fetch data from server
        $.ajax({
            url: "/data", 
            dataType: 'json',
            data: selectedMetric,
            success: function(response) {
                convertTSData(response);
                // Remove anomalies of last data, if any.
                metricChart.removeAnomalies();
                metricChart.chart.series[0].setData(response);
                $("#load-preloader").hide("slow");
                $("#load-error").hide();
            },
            error: function(response) {
                $("#load-error").show("slow");
                $("#load-preloader").hide("slow");
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

        if(selectedAlgorithm === algorithmNameCache["MA"]) {
            var windowSize = $("#params-ma-window").val();
            var threshold = $("#params-ma-threshold").val();
            var method = algorithmNameCache["MA"];
            params = $.extend(selectedMetric, { "window" : windowSize, "threshold" : threshold, "method" : method });
        } 
        else if(selectedAlgorithm == algorithmNameCache["HMM"]) {
            var numOfStates = $("#params-hmm-states").val(); 
            var percentage = $("#params-hmm-percentage").val();
            var method = algorithmNameCache["HMM"];
            params = $.extend(selectedMetric, { "n_states" : numOfStates, "percentage" : percentage, "method" : method });
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
                convertAnomalyData(response);
                console.log(response);
                metricChart.removeAnomalies();
                metricChart.addAnomalies(response);
                $("#algorithm-preloader").hide();
                $("#algorithm-error").hide();
            },
            error: function(response) {
                $("#algorithm-preloader").hide();
                $("#algorithm-error").show('slow');
            }
        });
    });

    // Show/hide appropriate parameters
    $("#algorithm-name").change(function(event) {
        var selectedAlgorithm = event.target.value;
        var paramSelector;

        if(selectedAlgorithm === algorithmNameCache["MA"]) {
            paramSelector = "#params-ma";       
        } else if(selectedAlgorithm === algorithmNameCache["HMM"]) {
            paramSelector = "#params-hmm"
        }
         // Hide all other params div.
        $("div[id^=params]").hide('fast', function() {
            $(paramSelector).show('fast');
        });
    });
});
