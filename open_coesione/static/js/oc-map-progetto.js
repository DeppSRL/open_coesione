var MAPPA, MAPPA_LAYER, MAPPA_MONDO, MAPPA_ONCLICK, MAPPA_POPUP, MAPPA_CACHE = {};

$(document).ready(function() {
    build_map('map', '/territori/leaflet/world.json', function(data) {
        var base_style = {
            color: '#343434',
            radius: 6
        },
        hover_style = {
            color: '#003A33',
            radius: 10
        };
        $('.map-location').each(function() {
            var $this = $(this);
            if ($this.data('coords')) {
                var marker = $this.data('coords').split(',');
                var circle = new L.CircleMarker(new L.LatLng(marker[1], marker[0]), base_style);
                MAPPA.addLayer(circle);
                // add mouse hover effect
                $this.hover(function() { circle.setStyle(hover_style).setRadius(hover_style.radius) }, function() { circle.setStyle(base_style).setRadius(base_style.radius) });
                $(circle).hover(function() { $this.addClass('map-location-active') }, function() { $this.removeClass('map-location-active') })
            }
        });
    });
});
