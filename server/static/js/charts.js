var metricChart;
var metricsData; // Stores the machine, metric object.

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

$(document).ready(function() {
    $(function() {

        $.getJSON('http://www.highcharts.com/samples/data/jsonp.php?filename=large-dataset.json&callback=?', function(data) {
            // Create a timer
            var start = + new Date();

            // Create the chart
            $('#chart-container').highcharts('StockChart', {
                    chart: {
                    events: {
                        load: function(chart) {
                            this.setTitle(null, {
                                text: 'Built chart in '+ (new Date() - start) +'ms'
                            });
                            metricChart = $("#chart-container").highcharts();
                        }
                    },
                    zoomType: 'x'
                    },
                    rangeSelector: {
                    inputEnabled: $('#chart-container').width() > 480,
                            buttons: [{
                                    type: 'day',
                                    count: 3,
                                    text: '3d'
                            }, {
                                    type: 'week',
                                    count: 1,
                                    text: '1w'
                            }, {
                                    type: 'month',
                                    count: 1,
                                    text: '1m'
                            }, {
                                    type: 'month',
                                    count: 6,
                                    text: '6m'
                            }, {
                                    type: 'year',
                                    count: 1,
                                    text: '1y'
                            }, {
                                    type: 'all',
                                    text: 'All'
                            }],
                            selected: 3
                    },
                yAxis: {
                    title: {
                        text: 'Temperature (°C)'
                    }
                },
                    title: {
                    text: 'Hourly temperatures in Vik i Sogn, Norway, 2004-2010'
                },
                subtitle: {
                    text: 'Built chart in ...' // dummy text to reserve space for dynamic subtitle
                },
                series: [{
                            name: 'Temperature',
                            data: data,
                            pointStart: Date.UTC(2004, 3, 1),
                            pointInterval: 3600 * 1000,
                            tooltip: {
                                valueDecimals: 1,
                                valueSuffix: '°C'
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
