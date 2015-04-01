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

// tnx to zio bill -__-'
if(typeof String.prototype.trim !== 'function') {
    String.prototype.trim = function() {
        return this.replace(/^\s+|\s+$/g, '');
    }
}
if (!Array.indexOf) {
    Array.prototype.indexOf = function (obj, start) {
        for (var i = (start || 0); i < this.length; i++) {
            if (this[i] == obj) {
                return i;
            }
        }
        return -1;
    }
}


var defaults = {
    credits: { text: 'Fonte: DPS-ISTAT', href:'http://www.opencoesione.gov.it/opendata' },
    backgroundColor: null
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
        units: [
            ['year', null]
        ]
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
        var items = parse_row(lines[line], separator);
        // take the first for key
        var key = items.shift().trim();
        // add this line to results
        results[ key ] = items.length == 1 ?
            items.shift().trim() :
            $.map(items, $.trim);
    }
    return results;
};

// Parse a CSV row, accounting for commas inside quotes
var parse_row = function(row, separator){
  var insideQuote = false,
      entries = [],
      entry = [];
  row.split('').forEach(function (character) {
    if(character === '"') {
      insideQuote = !insideQuote;
    } else {
      if(character == separator && !insideQuote) {
        entries.push(entry.join(''));
        entry = [];
      } else {
        entry.push(character);
      }
    }
  });
  entries.push(entry.join(''));
  return entries;
}

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
        results.push([ Date.UTC(years[i], 0, 1), value ]);
    }
    return results;
};

var get_location_id = function(name) {
    var index;
    //console.log(APP.regioni, typeof APP.regioni )
    for( var key in APP.regioni ) {
        //console.log( key, APP.regioni[key] )
        if (APP.regioni[key] == name) {
            index = key;
        }
    }
    return parseInt(index);
};


var filter_series = function( series, location_ids ) {
    return jQuery.grep(series,function(el,index,array) {
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

var get_first_key = function(obj, default_value) {
    for ( var k in obj ) {
        return k;
    }
    return default_value || false;
}

var print_line_chart = function(container, min_regions, max_regions) {
    $.when(
        $.get(APP.base_url + 'csv/regioni.csv'),
        $.get(APP.base_url + 'csv/temi.csv')
    )
        .done(function(regioni, temi) {

            APP.regioni  = read_locations(regioni[0]);
            APP.temi     = read_csv(temi[0],true);

            var topic_id = $( container ).data('topic') || get_first_key(APP.temi);
            // reset locations
            APP.location_ids = [];
            // add Italia
            APP.location_ids.push(get_location_id('Italia'));
            // add default location
            $( container ).data('location') && APP.location_ids.push( parseInt( $( container ).data('location')) );
            var index_id = $( container).attr('data-index') || 0;

            load_topic(topic_id, function( indexes ) {
                // take first index or selected
                index_id = index_id == 0 ? get_first_key(indexes) : index_id;

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
//        console.log('region selected',arguments, APP.chart.series, APP.chart.series.length, max_regions);
        if (APP.chart.series.length == max_regions) {
            APP.chart.series[max_regions-1].remove();
        }
        var location_id = $(this).val();
        var serie = jQuery.grep(APP.chart.series,function(el){ return location_id == get_location_id(el.name); });
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
        //console.log('reset',min_regions,max_regions,APP.chart.series.length);
        var elements_count = APP.chart.series.length;
        while( elements_count > min_regions ) {
            APP.chart.series.pop().remove()
            elements_count--;
        }

        $('#region-selector').val('').change();
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