var map, selectsControls;

function init(){
    //OpenLayers.ImgPath = "js/theme/dark/img/";
    var option = {
    };
    map = new OpenLayers.Map('map', option);
    olmapnik = new OpenLayers.Layer.OSM("OpenStreetMap Mapnik",
                                        "http://tile.openstreetmap.org/${z}/${x}/${y}.png",
                                        {layers: 'basic'}
                                       );
    map.addLayer(olmapnik);



    var featurecollection = {
        "type": "FeatureCollection",
        "features": [
            {"geometry": {
                "type": "GeometryCollection",
                "geometries": [
                    {
                        "type": "LineString",
                        "coordinates":
                            [[11.0878902207, 45.1602390564],
                                [15.01953125, 48.1298828125]]
                    },
                    {
                        "type": "Polygon",
                        "coordinates":
                            [[[11.0878902207, 45.1602390564],
                                [14.931640625, 40.9228515625],
                                [0.8251953125, 41.0986328125],
                                [7.63671875, 48.96484375],
                                [11.0878902207, 45.1602390564]]]
                    },
                    {
                        "type":"Point",
                        "coordinates":[12.32, 44.1748046875]
                    }
                ]
            },
                "type": "Feature",
                "properties": {}}
        ]
    };
    var geojson_format = new OpenLayers.Format.GeoJSON();
    var vector_layer = new OpenLayers.Layer.Vector(
        "Test",
        {
            projection: 'wgs84',
            strategies: [new OpenLayers.Strategy.Fixed()],
            protocol: new OpenLayers.Protocol.HTTP({
                url: "http://localhost:8020/territori/regione/12.json",
                projection: 'wgs84',
                format: new OpenLayers.Format.GeoJSON()
            }) // protocol
        }
    );
    map.addLayer(vector_layer);

    //vector_layer.addFeatures(geojson_format.read(featurecollection));

    var geojson_format = new OpenLayers.Format.GeoJSON();
    var vectors = new OpenLayers.Layer.Vector("Comuni");
    var url = "http://localhost:8020/territori/regione/12.json";
    OpenLayers.loadURL(url, {}, null, function (response) {
        var feats = geojson_format.read(response.responseText);
        vectors.addFeatures(feats);
    });
    map.addLayer(vectors);

    map.setCenter(new OpenLayers.LonLat(12, 42), 5);


    var ls= new OpenLayers.Control.LayerSwitcher();
    map.addControl(ls);
    ls.maximizeControl();
}


