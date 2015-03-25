// Leaflet add-on: Legend Control

/*
 * Legend definition build and positioning
 */
L.Control.Legend = L.Control.extend({
    options: {
        position: 'topright'
    },
    content: '',

    initialize: function (options) {
        L.Util.setOptions(this, options);
    },

    onAdd: function (map) {
        this._container = L.DomUtil.create('div', 'leaflet-control-legend');
        this._container.innerHTML = this.content;
        L.DomEvent.disableClickPropagation(this._container);

        return this._container;
    }

});

L.Map.mergeOptions({
    legendControl: true
});

L.Map.addInitHook(function () {
    if (this.options.legendControl) {
        this.legendControl = (new L.Control.Legend()).addTo(this);
    }
});

// OpenCoesione map builder

var MAPPA, MAPPA_LAYER, MAPPA_MONDO, MAPPA_ONCLICK, MAPPA_POPUP, MAPPA_CACHE = {}, IS_LOADING = false;

$(document).ready(function() {
    var selectors1 = $('#selectors');
    var selectors2 = $('#procapite_selectors');

//    var layer_name = selectors1.find('.btn.active').prop('id');
    var dataset_name = $('#map-layer-selector').find('.block-chart.block-active').data('dataset');

    var data_url = function() {
        return '/territori/leaflet/' + $('#map').data('mapselector') + selectors1.find('.btn.active').data('path') + '.json?tematizzazione=' + dataset_name + selectors2.find('.btn.active').data('path');
    }

    build_map('map', data_url(), function(data) {
        if (data.layer_name == 'world') {
            // marker added if necessary
            var marker = selectors1.find('.btn.active').data('coords');
            if (marker) {
                marker = marker.split(',');
                MAPPA.addLayer(new L.Circle(new L.LatLng(marker[1], marker[0]), 30 * 1000, {
                    color: '#343434'
                }));
            }
        }
    });

    $([selectors1, selectors2]).each(function() {
        $(this).find('.btn').on('click', function() {
            var self = $(this);

            if (!IS_LOADING && !self.hasClass('active')) {
                IS_LOADING = true;

                self.addClass('active').siblings().removeClass('active');

                // close popup if opened
                MAPPA_POPUP && MAPPA.closePopup(MAPPA_POPUP);

                build_map('map', data_url(), function() {
                    IS_LOADING = false;
                });
            }
        });
    });
});

function build_map( container, data_url, callback, failback ) {
    /*
     * Create map instance, and popup
     */
    if ( !MAPPA ) {
        MAPPA = new L.Map(container, {
            //minZoom: 5,
            //maxZoom: 7,
            scrollWheelZoom: false,
            attributionControl: false
        });
    }
    if ( !MAPPA_POPUP ) {
        MAPPA_POPUP = new L.Popup();
    }

    /*
     * Loads the data with a JSON call, and then load the map layer, using the data
     */
    var loader = new ajaxLoader('#'+container);
    $.getJSON( data_url ,function(data){
        load_map_layer(data);
        loader.remove();
        callback && callback(data);
    }).error( failback || callback );
}

/*
 * Function to properly generate the map
 * necessary data are passed as arguments
 */
function load_map_layer(data) {

    // layer removal, if necessary
    if (MAPPA_LAYER && MAPPA.hasLayer(MAPPA_LAYER)) {
        MAPPA.removeLayer(MAPPA_LAYER);
    }

    if ( !MAPPA_MONDO ) {
        // world layer
        MAPPA_MONDO = new L.TileLayer(data.tilestache_url+'/world/{z}/{x}/{y}.png',{
            maxZoom: data['zoom']['max'],
            minZoom: data['zoom']['min']
        })  ;

        MAPPA.addLayer(MAPPA_MONDO);
    }

    // boundaries retrieval from data
    var southWest = new L.LatLng(data.bounds.southwest.lat, data.bounds.southwest.lng ),
        northEast = new L.LatLng(data.bounds.northeast.lat, data.bounds.northeast.lng),
        bounds = new L.LatLngBounds(southWest, northEast);
    MAPPA.fitBounds(bounds);


    if ( data.layer_name == 'world' ) {
//        // marker added if necessary
//        var marker = $('#selectors .btn.active').data('coords');
//        if ( marker ) {
//            marker = marker.split(',');
//            MAPPA.addLayer(new L.Circle(new L.LatLng( marker[1], marker[0]), 30 * 1000, {
//                color: '#343434'
//            }));
//        }
        // removing LegendControl from map
        MAPPA.legendControl.removeFrom(MAPPA);
        return;
    }

    if ( !MAPPA_CACHE[data.layer_name] ) {
        // layer instance creation
        MAPPA_CACHE[data.layer_name] = new L.TileLayer(data.tilestache_url+'/'+data.layer_name+'/{z}/{x}/{y}.png',{
            maxZoom: data['zoom']['max'],
            minZoom: data['zoom']['min']
        });
    }

    MAPPA_LAYER = MAPPA_CACHE[data.layer_name];

    // layer is added
    MAPPA.addLayer(MAPPA_LAYER);

    // legend is updated
    $('.leaflet-control-legend').html(data.legend_html).each(function(){
        //console.log($(this).text());
        //intword
        $('li',this).each(function(){
            if ($(this).text().indexOf('-') != -1)
            {
                var values = $(this).text().split(' - ');
                $(this).text(intword(values[0].split('.').join('')) + ' - ' + intword(values[1].split('.').join('')));
            }
            else if ($(this).text().indexOf('fino a') != -1)
            {
                var values = $(this).text().split('fino a ');
                $(this).text('fino a ' + intword(values[1].split('.').join('')));
            }
        }).prepend($('<i />').addClass('icon-sign-blank'));
    });

    // onclick event disabled on map
    if (MAPPA_ONCLICK) {
        MAPPA.off('click', MAPPA_ONCLICK);
    }

    // onclick event defined
    MAPPA_ONCLICK = function onMapClick(e) {
        var latlngStr = '(' + e.latlng.lat.toFixed(3) + ', ' + e.latlng.lng.toFixed(3) + ')';
        var info_url = data.info_base_url +'/' + data.layer_type +'/'+
            e.latlng.lat.toFixed(3) + "/" +
            e.latlng.lng.toFixed(3) + "/";

        //MAPPA_POPUP.setContent('<div id="map-info-loader" style="height:40px; width: 60px;"></div>');


        var loader = new ajaxLoader('#map');

        jQuery.get(info_url, function(data) {
            if (!data.success) {
                loader.remove();
                return;
            }
            loader.remove(function() {
                // popup building
                MAPPA_POPUP.setLatLng(e.latlng);
                MAPPA.openPopup(MAPPA_POPUP);

                var content = '';
                content += '<a href="'+data.territorio.territori[0][1]+'">'+data.territorio.territori[0][0]+'</a>';
                if ( data.territorio.territori[1] ) {
                    content += ' &gt; <a href="'+data.territorio.territori[1][1]+'">'+data.territorio.territori[1][0]+'</a>';
                }
                if ( data.territorio.territori[2] ) {
                    content += '<br><a href="'+data.territorio.territori[2][1]+'">'+data.territorio.territori[2][0]+'</a>';
                }
                MAPPA_POPUP.setContent(
                    content + "<br/>" +
                        "<b>finanziamento</b>: " + intword(data.territorio.costo) + " &euro;<br/>" +
                        "<b>finanziamento pro capite</b>: " + intword(data.territorio.costo_procapite) + " &euro;<br/>" +
                        "<b>pagamento</b>: " + intword(data.territorio.pagamento) + " &euro;<br/>" +
                        "<b>n. progetti</b>: " + intword(data.territorio.n_progetti)

                );
            });

        });
    };
    
    // on click event activated
    MAPPA.on('click', MAPPA_ONCLICK );
}


// ---------------------------------------------------------------------------

/*
 * Some functions taken from http://vanzonneveld.net, to humanize big numbers
 */
function number_format( number, decimals, dec_point, thousands_sep ) {
    // http://kevin.vanzonneveld.net
    // +   original by: Jonas Raoni Soares Silva (http://www.jsfromhell.com)
    // +   improved by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
    // +	 bugfix by: Michael White (http://crestidg.com)
    // +	 bugfix by: Benjamin Lupton
    // +	 bugfix by: Allan Jensen (http://www.winternet.no)
    // +	revised by: Jonas Raoni Soares Silva (http://www.jsfromhell.com)
    // *	 example 1: number_format(1234.5678, 2, '.', '');
    // *	 returns 1: 1234.57

    var n = number, c = isNaN(decimals = Math.abs(decimals)) ? 2 : decimals;
    var d = dec_point == undefined ? "," : dec_point;
    var t = thousands_sep == undefined ? "." : thousands_sep, s = n < 0 ? "-" : "";
    var i = parseInt(n = Math.abs(+n || 0).toFixed(c)) + "", j = (j = i.length) > 3 ? j % 3 : 0;

    return s + (j ? i.substr(0, j) + t : "") + i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + t) + (c ? d + Math.abs(n - i).toFixed(c).slice(2) : "");
}
var intcomma = function( number, decimals ) {
    decimals = decimals === undefined ? 0 : decimals;
    return number_format( number, decimals, ',', '.' );
};
var intword = function( number ) {
    number = parseInt( number );
    if( number < 100 ) {
        return number;
    } else if( number < 1000000 ) {
        return intcomma( number, 0 );
    } else if( number < 1000000000 ) {
        return intcomma( number / 1000000.0, 1 ) + " mil.";
    } else {
        return intcomma( number / 1000000000.0, 1 ) + " mld.";
    }
};