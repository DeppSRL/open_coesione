var map, selectsControls;

function init(){
	//OpenLayers.ImgPath = "js/theme/dark/img/";
	var option = {
		projection: new OpenLayers.Projection("EPSG:900913"),
		displayProjection: new OpenLayers.Projection("EPSG:4326"),
		scales: [50000000, 30000000, 10000000, 5000000]
	};
	map = new OpenLayers.Map('map', option);
	olmapnik = new OpenLayers.Layer.OSM("OpenStreetMap Mapnik", "http://tile.openstreetmap.org/${z}/${x}/${y}.png");

    var url = "http://localhost:8020/territori/regione/12.json";
    vector_layer = new OpenLayers.Layer.Vector()
    OpenLayers.loadURL(url, {}, null, function (response) {
        var gformat = new OpenLayers.Format.GeoJSON();
        gg = '{"type":"FeatureCollection", "features":' +
            response.responseText + '}';
        var feats = gformat.read(gg);
        vector_layer.addFeatures(feats);
    });


	map.addLayer(olmapnik);
	map.addLayer(vector_layer);
	var ls= new OpenLayers.Control.LayerSwitcher(); 
	map.addControl(ls); 
	ls.maximizeControl(); 


	extent = new OpenLayers.Bounds(6.62773,35.494,18.5211,47.0926).transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:900913"));
	map.zoomToExtent(extent);
};
