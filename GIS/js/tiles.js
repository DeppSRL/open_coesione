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
	olmapquest = new OpenLayers.Layer.OSM(
	  "Comuni d'Italia", 
	  "http://localhost:8020/world/tiles/comuni/${z}/${x}/${y}.png",
	  {'isBaseLayer': false});
	map.addLayer(olmapnik);
	map.addLayer(olmapquest);	
	var ls= new OpenLayers.Control.LayerSwitcher(); 
	map.addControl(ls); 
	ls.maximizeControl(); 


	extent = new OpenLayers.Bounds(6.62773,35.494,18.5211,47.0926).transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:900913"));
	map.zoomToExtent(extent);
};
