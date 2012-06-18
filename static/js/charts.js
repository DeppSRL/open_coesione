
var defaults = {
    credits: {href: 'http://www.opencoesione.gov.it', text: 'Open Coesione'},
    backgroundColor: 'transparent'
}

// ----------
// PIE CHARTS
// ----------
var pie_chart_options = {
    chart: {
        renderTo: 'container',
        plotBackgroundColor: null,
        plotBorderWidth: null,
        plotShadow: false,
        backgroundColor: defaults.backgroundColor
    },
    title: {
        text: ''
    },
    tooltip: {
        formatter: function() {
            return '<b>'+ this.point.name +'</b>: '+ this.percentage.toFixed(2) +' %';
        },
        useHTML: true
    },
    plotOptions: {
        pie: {
            allowPointSelect: true,
            cursor: 'pointer',
            dataLabels: {
                enabled: false,
                color: '#000000',
                connectorColor: '#000000',
                formatter: function() {
                    return '<b>'+ this.point.name +'</b>: '+ this.percentage.toFixed(2) +' %';
                }
            },
            showInLegend: false

        }
    },
    series: [],
    credits: defaults.credits
};

function print_pie_chart( source, destination)
{
    // Main topics chart
    var total = 0;
    var main_topics_options = pie_chart_options;
    main_topics_options.chart.renderTo = destination;
    var series = {
        type: 'pie',
        data: []
    };

    // take values
    $(source +' tr').each(function(ix, line){
        values = $('a, strong', line).map( function(el, item) { return $(item).text(); });
        sub_total = parseInt(values[1].split('.').join(''));
        total += sub_total;
        series.data.push([values[0], sub_total ]);
    });

    // normalize values
    $.each(series.data, function(ix, line) {
        series.data[ix][1] = series.data[ix][1] / total;
    });
    main_topics_options.series.push(series);

    return new Highcharts.Chart(main_topics_options);
}

// ------------
// INDEX CHARTS
// ------------


var line_chart_options = {

    chart: {
        renderTo: 'container',
        type: 'spline',
        marginLeft: 50,
        backgroundColor: defaults.backgroundColor
    },
    title: {
        text: 'Test'
    },
    legend: {
        layout: 'vertical',
        backgroundColor: '#FFFFFF',
        align: 'right',
        verticalAlign: 'top',
        floating: true
    },
    xAxis: {
        showLastLabel: true,
        type: 'datetime',
        dateTimeLabelFormats: {
            month: '%Y',
            year: '%Y'
        },
        min: Date.UTC(1994, 1, 1),
        max: Date.UTC(2012, 1, 1)
    },
    yAxis: {
        title: {
            align: 'high',
            offset: 0,
            text: '%',
            rotation: 0,
            y: -10
        }
    },
    categories: [],
    series_collection: [],
    series: [],
    tooltip: { valueDecimals: 2, valueSuffix: '%'  },
    credits: defaults.credits
};

var regioni = {};
function load_regioni(base_url)
{
    $.get(base_url +"csv/regioni.csv", function(data) {
        // Split the lines
        var lines = data.split('\n');
        // Iterate over the lines and add categories or series
        $.each(lines, function(lineNo, line) {

            if (lineNo == 0 || line == '') {
                return ; // skip headers and blank lines
            }
            var items = line.split(',');

            regioni[items[0]] = {
                denominazione: items[1]
            };
        });
    });
}

var indicatori_tema = {};
function load_tema(base_url, tema_id)
{
    $.get(base_url + "csv/indicatori/" + tema_id + ".csv", function(data) {
        // Split the lines
        var lines = data.split('\n');

        indicatori_tema[tema_id] = {};

        // Iterate over the lines and add categories or series
        for (var lineNo=0; ( lines.length ); lineNo++) {

            var line = lines[lineNo];

            if (lineNo == 0 || line == ''){
                return; // skip headers and blank lines
            }
            var items = line.split(',');

            indicatori_tema[tema_id][ items[0] ] = {

                titolo: items[1],
                sottotitolo: items[2]

            };
        }
    });
}

var line_charts = {};
function print_line_chart(base_url, tema_id, indicatore_id, regione_id)
{
    var options = jQuery.extend( line_chart_options, {
        series: [],
        categories: [],
        series_collection: [],
        title: {
            text: indicatori_tema[tema_id][indicatore_id].titolo
        },
        chart: {
            renderTo: 'theme_index_' + tema_id
        }
    });

    $.get(base_url + "csv/temaind/"+tema_id+"_"+indicatore_id+".csv", function(data) {
        // Split the lines
        var lines = data.split('\n');

        // Iterate over the lines and add categories or series
        $.each(lines, function(lineNo, line) {
            if (line == '') {
                return; // skip blank lines
            }

            var items = line.split(',');

            // header line containes categories
            if (lineNo == 0) {
                $.each(items, function(itemNo, item) {
                    if (itemNo > 0) options.categories.push(Date.UTC(parseInt(item),  1, 1));
                });
            }
            // the rest of the lines contain data with their name in the first position
            else {
                var series = {
                    data: []
                };
                $.each(items, function(itemNo, item) {
                    if (itemNo == 0) {
                        series.name = item;
                    } else {
                        var itemValue = parseFloat(item);
                        if (!isNaN(itemValue)) {
                            series.data.push([options.categories[itemNo-1], itemValue]);
                        }
                    }
                });

                options.series_collection.push(series)
            }

            options.series = [
                // add avarage index
                options.series_collection[20],
                // add specific region index
                options.series_collection[regione_id]
            ]

        });

        // Create the chart
        line_charts[tema_id+"_"+indicatore_id+"_"+regione_id] = new Highcharts.Chart(options);
    });

}


var APP = {
    is_loaded: false,
    base_url: '',
    charts: [],
    locations: [],
    topic_indexes: []
};

APP.start = function(base_url) {
    if (!APP.is_loaded) return self;

    // initialize APP.base_url
    APP.base_url = base_url;

    $.get(APP.base_url +"csv/regioni.csv", function(data) {
        // take locations
        var lines = data.split('\n'); // Split the lines
        // Iterate over the lines and add categories or series
        $.each(lines, function(lineNo, line) {

            if (lineNo == 0 || line == '') {
                return ; // skip headers and blank lines
            }
            var items = line.split(',');

            APP.locations[items[0]] = {
                denominazione: items[1]
            };
        });
    });

    return self;

}

APP.load_index = function( topic_id, callback )
{
    $.get( this.base_url + "csv/indicatori/" + topic_id +'.csv' , function(data) {
        callback(topic_id, data);
    });
}


APP.print_chart = function(topic_id, topic_index_id, location_id)
{
    // load topic definition
    $.get( this.base_url + "csv/indicatori/" + topic_id +'.csv' , function(data) {
        APP.load_topic(data);
        $(APP).trigger('topic_loaded'+ topic_id, topic_id, APP.locations[topic_id])
    });
}



APP.load_topic = function( topic_id )
{
    // Split the lines
    var lines = data.split('\n');

    self.topic_indexes[tema_id] = {};

    // Iterate over the lines and add categories or series
    for (var lineNo=0; ( lines.length ); lineNo++) {

        var line = lines[lineNo];

        if (lineNo == 0 || line == ''){
            return; // skip headers and blank lines
        }
        var items = line.split(',');

        self.topic_indexes[tema_id][ items[0] ] = {

            titolo: items[1],
            sottotitolo: items[2]

        };
    }
}






