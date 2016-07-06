var MAPPA, MAPPA_LAYER, MAPPA_MONDO, MAPPA_ONCLICK, MAPPA_POPUP, MAPPA_CACHE = {}, IS_LOADING = false;

$(document).ready(function() {
    var selectors1 = $('#selectors');
    var selectors2 = $('#procapite_selectors');

//    var layer_name = selectors1.find('.btn.active').prop('id');
    var dataset_name = $('#map-layer-selector').find('.block-chart.block-active').data('dataset');

    var data_url = function() {
        return '/territori/leaflet/' + $('#map').data('mapselector') + selectors1.find('.btn.active').data('path') + '.json?tematizzazione=' + dataset_name + selectors2.find('.btn.active').data('path');
    };

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
