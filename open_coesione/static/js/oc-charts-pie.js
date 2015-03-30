var pie_chart_options = {
    chart: {
        renderTo: 'container',
        plotBackgroundColor: null,
        plotBorderWidth: null,
        plotShadow: false,
        backgroundColor: null
    },
    title: { text: '' },
    tooltip: {
        formatter: function() {
            return '<div class="tooltip-box"><b>'+ this.point.name +'</b>: '+ this.percentage.toFixed(2) +'<small>%</small></div>';
        },
        useHTML: true,
        backgroundColor: '#F7F6F1',
        borderWidth: 0,
        shadow: false,
        style: {
            width: '150px',
            'min-height': '20px'
        }
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
                    return '<b>'+ this.point.name +'</b>: '+ this.percentage.toFixed(2) +'<small>%</small>';
                }
            },
            showInLegend: false

        }
    },
    series: [],
    credits: { enabled: false },
    colors: [
        '#c1dccb', '#aed4bd', '#bae2d4', '#bee2cc', '#d0e2d7', '#cae7d5', '#afded4', '#d3ece2', '#dcefe2', '#91c9a8', '#e3f2e8', '#bde3d2', '#b3d7c9'
        //'#ECE7DF', '#CAC7C3', '#979491', '#686462', '#2E2B2A', '#777777', '#AAAAAA', '#BBBBBB', '#CCCCCC', '#DDDDDD', '#EEEEEE'
    ]
};

var print_pie_chart = function( source, destination )
{
    // Main topics chart
    var total = 0;
    var main_topics_options = $.extend(true, {}, pie_chart_options, {
        chart: {
            renderTo: destination
        }
    });
    var series = {
        type: 'pie',
        data: []
    };

    // take values
    $(source +' tr').each(function(ix, line){
        if ( ! ($(line).parent().is('table') || $(line).parent().is('tbody') ) ) {
            return;
        }
        var values = $('a, strong', line).map( function(el, item) { return $(item).text(); });
        if (values.length == 0) {
            values = $('td', line).map( function(el, item) { return $(item).text(); });
        }
        if ( values.length !== 2) {
            values = $('th, strong', line).map( function(el, item) { return $(item).text(); });
        }
        var sub_total = parseInt(values[1].split('.').join(''));
        if (sub_total > 0 ) {
            total += sub_total;
            series.data.push([values[0], sub_total ]);
        }
    });

    // normalize values
    $.each(series.data, function(ix, line) {
        series.data[ix][1] = series.data[ix][1] / total;
    });
    main_topics_options.series.push(series);
    console.log(series);

    return new Highcharts.Chart(main_topics_options);
};
