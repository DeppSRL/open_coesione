L.Control.Legend = L.Control.extend({
    options: {
        position: 'topright'
    },

    initialize: function (options) {
        L.Util.setOptions(this, options);
    },

    onAdd: function (map) {
        this._container = L.DomUtil.create('div', 'leaflet-control-legend');
        this._container.innerHTML = '{% spaceless %}{{ legend_html|safe }}{%  endspaceless %}';
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


var map = new L.Map('map', {
    minZoom: 5,
    maxZoom: 10,
    scrollWheelZoom: false,
    attributionControl: false
});

var territori = new L.TileLayer('{{ TILESTACHE_URL }}/{{ layer_name }}/{z}/{x}/{y}.png');


var southWest = new L.LatLng({{ bounds.southwest.lat }},{{ bounds.southwest.lng }}),
northEast = new L.LatLng({{ bounds.northeast.lat }},{{ bounds.northeast.lng }}),
bounds = new L.LatLngBounds(southWest, northEast);
map.fitBounds(bounds);

map.addLayer(territori);
map.on('click', onMapClick);

var popup = new L.Popup();
function onMapClick(e) {
    var latlngStr = '(' + e.latlng.lat.toFixed(3) + ', ' + e.latlng.lng.toFixed(3) + ')';
    var info_url = '{{ info_base_url }}/' +
        '{{ layer_type }}/' +
        e.latlng.lat.toFixed(3) + "/" +
        e.latlng.lng.toFixed(3) + "/";
    jQuery.get(info_url, function(data) {
        popup.setLatLng(e.latlng);
        popup.setContent(
            "<b>Territorio</b>: " + data.territorio.denominazione + "<br/>" +
                "<b>n progetti</b>: " + data.territorio.n_progetti + "<br/>" +
                "<b>costo</b>: " + data.territorio.costo + "<br/>" +
                "<b>pagamento</b>: " + data.territorio.pagamento

        );
        map.openPopup(popup);
    });

}
