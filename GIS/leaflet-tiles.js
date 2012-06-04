var map, selectsControls;

function init(){
  // initialize the map on the "map" div
  var map = new L.Map('map', {
    minZoom: 5,
    maxZoom: 10
  });

  var layers = new L.LayerGroup();
  
  // create a tile layer
  var omslayer = new L.TileLayer('http://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
  });

  // create a tile layer
  var layer = new L.TileLayer('http://localhost/open_coesione_gis/tiles/{z}/{x}/{y}.png', {
      attribution: 'Map data &copy; <a href="http://openpolis.it">OpenPolisMaps</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
  });

  
  layers.addLayer(omslayer);
  layers.addLayer(layer);

  // add the CloudMade layer to the map set the view to a given center and zoom
  map.addLayer(layers).setView(new L.LatLng(42.000, 12.000), 5);

};
