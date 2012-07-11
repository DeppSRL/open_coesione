var APP = {
    base_url: '/static/',
    // caches
    regioni: {},
    temi: {},
    indicatori: {},
    // current chart
    chart: {},
    // current series
    series: {},
    location_ids: []
};

if(typeof String.prototype.trim !== 'function') {
    String.prototype.trim = function() {
        return this.replace(/^\s+|\s+$/g, '');
    }
}

var defaults = {
    credits: { text: 'Fonte: DPS-ISTAT', href:'http://www.istat.it/it/archivio/16777/' },
    backgroundColor: null
};

var pie_chart_options = {
    chart: {
        renderTo: 'container',
        plotBackgroundColor: null,
        plotBorderWidth: null,
        plotShadow: false,
        backgroundColor: defaults.backgroundColor
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
        "#ECE7DF", "#CAC7C3", "#979491", "#686462", "#2E2B2A", "#777777", "#AAAAAA", "#BBBBBB", "#CCCCCC", "#DDDDDD", "#EEEEEE"
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
        renderTo: 'topic_chart',
        type: 'spline',
        backgroundColor: defaults.backgroundColor
    },
    series: [],
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
            text: '',
            rotation: 0
            //y: -10
        }

    },
    tooltip: { valueDecimals: 2, valueSuffix: '', xDateFormat: '%Y' },
    credits: defaults.credits
};

var read_csv = function(csvtext, skip_first, separator) {
    separator = separator || ',';
    // split text in lines
    var lines = csvtext.split(/\n/);
    // remove last empty line
    lines.pop(lines.length-1);
    // remove first line if not required
    (skip_first || false) && (lines.shift());
    // prepare results
    var results = {};
    for( var line=0; line< lines.length; line++) {
        // split line to cells
        var items = lines[line].split(separator);
        // take the first for key
        var key = items.shift().trim();
        // add this line to results
        results[ key ] = items.length == 1 ?
            items.shift().trim() :
            $.map(items, $.trim);
    }
    return results;
};

var read_locations = function(regioni) {
    var locations = {};
    $.each(read_csv(regioni,true), function(index, name) {
        locations[parseInt(index)] = name;
    });
    return locations;
};

var load_topic = function( topic_id, callback ) {
    if ( !(topic_id in APP.indicatori ))  {

        $.when( $.get(APP.base_url + 'csv/indicatori/' + topic_id + '.csv') ).done(function(csvtext) {
            APP.indicatori[topic_id] = {};
            $.each( read_csv(csvtext, true), function(index_id, values) {
                APP.indicatori[topic_id][index_id] = {
                    titolo: values[0],
                    sottotitolo: values[1]
                }
            });
            callback(APP.indicatori[topic_id])
        });

    }
    else {
        callback(APP.indicatori[topic_id]);
    }

};

var read_values = function(values, years)
{
    var results = [];
    for ( var i=0; i< years.length; i++ ) {
        var value = parseFloat(values[i]);
        // skip empty
        if ( isNaN(value) ) continue;
        // add index data
        results.push([ Date.UTC(years[i], 1, 1), value ]);
    }
    return results;
};

var get_location_id = function(name) {
    var index;
    Object.keys( APP.regioni ).forEach(function(key) {
        if (APP.regioni[key] == name) {
            index = key;
        }
    });
    return parseInt(index);
};


var filter_series = function( series, location_ids ) {
    return series.filter(function(el,index,array) {
        return location_ids.indexOf(el['location_id']) > -1;
    });
};

var print_chart = function(topic_id, index_id, location_ids) {
    // load data
    $.when(

        $.get(APP.base_url + 'csv/temaind/' + topic_id + '_' + index_id + '.csv')

    ).done(function(csvtext) {
            // prepare APP
            APP.series[index_id] = [];
            var years = [];
            // parse data
            $.each( read_csv(csvtext), function(location, values) {
                if ( location == 'Regione' ) {
                    // headers
                    years = values;
                }
                else {
                    // location data-set
                    APP.series[index_id].push({
                        name: location,
                        data: read_values( values, years ),
                        location_id: get_location_id(location)
                    });
                }
            });

            var options = $.extend(true, {}, line_chart_options, {
                title: { text: APP.indicatori[topic_id][index_id].titolo },
                subtitle: { text: APP.indicatori[topic_id][index_id].sottotitolo },
                series: filter_series(APP.series[index_id], location_ids)
            });

            //console.log('chart',topic_id, index_id,APP.indicatori[topic_id][index_id].titolo, options);
            // create chart
            APP.chart = new Highcharts.Chart(options);
        });
};

var print_line_chart = function(container, min_regions, max_regions) {
    $.when(
        $.get(APP.base_url + 'csv/regioni.csv'),
        $.get(APP.base_url + 'csv/temi.csv')
    )
        .done(function(regioni, temi) {

            APP.regioni  = read_locations(regioni[0]);
            APP.temi     = read_csv(temi[0],true);

            var topic_id = $( container ).data('topic') || Object.keys(APP.temi)[0];
            // reset locations
            APP.location_ids = [];
            // add Italia
            APP.location_ids.push(get_location_id('Italia'));
            // add default location
            $( container ).data('location') && APP.location_ids.push( parseInt( $( container ).data('location')) );
            var index_id = $( container).attr('data-index') || 0;

            load_topic(topic_id, function( indexes ) {
                // take first index or selected
                index_id = index_id == 0 ? Object.keys(indexes)[0] : index_id;

                // add indexes to select field
                if ( $("#indicator-selector").length) {
                    var $selector = $("#indicator-selector").empty()[0];
                    for (var idx in indexes) {
                        $selector.options.add(new Option(APP.indicatori[topic_id][idx].titolo, idx));
                    }
                }

                // add location to select field
                $selector = $("#region-selector");
                // reset location selector
                $selector.val('').children('option:not(:first)').remove();
                for ( idx in APP.regioni ) {
                    idx = parseInt(idx);
                    if ( APP.location_ids.indexOf(idx) == -1 )
                    {
                        $selector[0].options.add(new Option(APP.regioni[idx], idx));
                    }
                }

                // show the chart
                print_chart(topic_id, index_id, APP.location_ids );

                // set index to select field
                $("#indicator-selector").length && $('#indicator-selector').val(index_id);
            });

        });

    min_regions = min_regions || 2;
    max_regions = max_regions || 3;

    // the region select handler
    $('#region-selector').unbind('change').change(function() {
//        console.log('region selected',arguments);
        if (APP.chart.series.length == max_regions) {
            APP.chart.series[max_regions-1].remove();
        }
        var location_id = $(this).val();
        var serie = APP.chart.series.filter(function(el){ return location_id == get_location_id(el.name); });
        if (location_id != '' ) {
            if (serie.length > 0) {
//                console.log('check', serie, serie[0].visible);
                if( serie[0].visible ) {
//                    console.log('hide',serie);
                    serie[0].hide();
                }
                else {
//                    console.log('show',serie);
                    serie[0].show();
                }
            }
            else {
//                console.log('create serie',filter_series(APP.series[$( container).attr('data-index') || $('#indicator-selector').val()], [parseInt(location_id)] ));
                APP.chart.addSeries(
                    filter_series(APP.series[$( container).attr('data-index') || $('#indicator-selector').val()], [parseInt(location_id)] )[0],
                    true // APP.chart.redraw();
                );
            }

        }

    });

    $('#region-reset').click(function() {
//        console.log('reset',min_regions,max_regions,APP.chart.series.length);
        var elements_count = APP.chart.series.length;
        while( elements_count > min_regions ) {
//            console.log('removing',elements_count, APP.chart.series.pop().remove() );
            elements_count--;
        }

        $('#region-selector').val('');
        return false;
    });

    // the indicator select handler
    $('#indicator-selector').change(function() {
        var indicator_id = $(this).val();
        if (indicator_id != '') {
            APP.chart.destroy();
            $('#region-selector').val('');
            print_chart($( container ).data('topic'), indicator_id, APP.location_ids);
        }
    });
};