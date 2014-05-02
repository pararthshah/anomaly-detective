var metricChart;
var metricsData; // Stores the machine, metric object.
// red, yellow, purple, green/lime
var anomalyColors = ['#EE454B', '#FFFB94', '#B499FF', '#BAFF7A'];

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
 * Returns an array of plot band IDs.
 */
function addAnomalies(chart, anomalies) {
    $.each(anomalies, function(index, tuple) {
        chart.xAxis[0].addPlotBand({
            from: tuple[0], 
            to: tuple[1],
            color: anomalyColors[index], 
            id:index,
            label: {
                text: "Anomaly " + (index+1),
                verticalAlign: 'bottom',
                y: 0
            }
        });
    });
}

$(document).ready(function() {
    $(function() {
        $.getJSON('http://www.highcharts.com/samples/data/jsonp.php?filename=large-dataset.json&callback=?', function(data) {
            console.log(data);
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
                                // Assign the global variable 
                                metricChart = $("#chart-container").highcharts();
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
                                        type: 'hour',
                                        count: 1,
                                        text: '1h'
                                }, {
                                        type: 'd',
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
                            name: 'Timeseries',
                            data: data,
                            tooltip: {
                                valueDecimals: 1,
                            }
                    }]

            });
        });

    });

    $("#btn-get-metric").click(function() { 
        var selectedMachine = $("#machine-name").val();
        var selectedMetric = $("#metric-name").val();
        // fetch data from server
        $.getJSON("/data", 
            { machine : selectedMachine, metric : selectedMetric },
            function(response) {
                metricChart.series[0].setData(response);
        });
    });

    // Fetch the machine and metrics 
    $.getJSON("metrics", function(response) {
        metricsData = response;
        $("#machine-name").attr('disabled', false);
        addSelectOptions("#machine-name", response, true);
    });

    // Show Metrics list
    $("#machine-name").change(function(event) { 
        // Enable the metrics select dropdown and show the appropriate metrics.
        var selectedMachine = $(this).val();
        addSelectOptions("#metric-name", metricsData[selectedMachine]);
        $("#metric-name").attr('disabled', false);
    });
});
