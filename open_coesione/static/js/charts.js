var APP = {
    base_url: '/',
    regioni: {},
    indicatori_tema: {},
    charts: {}
};
var defaults = {
    credits: {href: 'http://www.opencoesione.gov.it', text: 'Open Coesione'},
    backgroundColor: 'transparent'
}

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

APP.init = function(base_url) {
    this.base_url = base_url;

    $.ajax({
        url: this.base_url +"csv/regioni.csv",
        async: false
    }).done(function(data) {
            $.each( data.split('\n'), function(lineNo,line) {
                if (lineNo == 0 || !line ) return;
                var items = line.split(',');
                APP.regioni[ items[0] ] = { denominazione: items[1] };
            })
        });
};

APP.print_pie_chart = function( source, destination )
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
        var values = $('a, strong', line).map( function(el, item) { return $(item).text(); });
        var sub_total = parseInt(values[1].split('.').join(''));
        total += sub_total;
        series.data.push([values[0], sub_total ]);
    });

    // normalize values
    $.each(series.data, function(ix, line) {
        series.data[ix][1] = series.data[ix][1] / total;
    });
    main_topics_options.series.push(series);

    return new Highcharts.Chart(main_topics_options);
};


var line_chart_options = {

    chart: {
        renderTo: 'container',
        type: 'spline',
        marginLeft: 50,
        backgroundColor: defaults.backgroundColor,
        height: 250
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

APP.load_topic_indexes = function(topic_id) {

    APP.indicatori_tema[topic_id] = {};

    $.ajax({
        url: this.base_url + "csv/indicatori/" + topic_id + ".csv",
        async: false
    }).done(function(data) {
            $.each( data.split('\n'), function(lineNo,line) {
                if (lineNo == 0 || !line ) return;
                var items = line.split(',');
                APP.indicatori_tema[topic_id][ items[0] ] = { titolo: items[1], sottotitolo: items[2] };
            })
        });
}

APP.print_line_chart = function(topic_id, container, location_id, index_id)
{
    APP.load_topic_indexes(topic_id);

    index_id = index_id || Object.keys(APP.indicatori_tema[topic_id]).shift();

    $.get(APP.base_url + "csv/temaind/"+topic_id+"_"+index_id+".csv", function(data) {
        APP._print_line_chart(topic_id, container, location_id, index_id, data);
    });
};

APP._print_line_chart = function(topic_id, container, location_id, index_id, data) {

    var options = jQuery.extend( true, line_chart_options, {
        series: [],
        categories: [],
        series_collection: [],
        title: {
            text: APP.indicatori_tema[topic_id][index_id].titolo
        },
        chart: {
            renderTo: container
        }
    });

    $.each( data.split('\n'), function(lineNo,line) {
        if (!line ) return;

        var items = line.split(',');

        // header line containes categories
        if (lineNo == 0 ) {
            $.each(items, function(itemNo, item) {
                if (itemNo > 0) options.categories.push(Date.UTC(parseInt(item),  1, 1));
            });
        }
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
            options.series_collection[location_id]
        ];
    });

    // Create the chart
    APP.charts[topic_id+"_"+location_id+"_"+index_id] = new Highcharts.Chart(options);
}
