// add commas (or dots) to long numbers
// to improve readability
function addCommas(nStr)
{
    nStr += '';
    x = nStr.split('.');
    x1 = x[0];
    x2 = x.length > 1 ? '.' + x[1] : '';
    var rgx = /(\d+)(\d{3})/;
    while (rgx.test(x1)) {
        x1 = x1.replace(rgx, '$1' + '.' + '$2');
    }
    return x1 + x2;
}

// draw a legend
function drawLegend(element, qMin, qMax) {
    // create a new group with the specific base color and add the lower value
    d3.select(element)
        .append(po.svg("g"))
        .attr("id", "legenda").attr("class", "TODO")
        .append("text")
        .attr("x", "20").attr("y", "40").text("Min: " + Math.round(qMin*100)/100);

    // add the various blocks of the legenda
    d3.select(element).select("#legenda").selectAll("rect")
        .data(d3.range(0, 8))
        .enter()
        .append("rect")
        .attr("width", "20").attr("height", "20").attr("y", "0")
        .attr("class", function (d, i) {
            return "q" + i + "-9";
        })
        .attr("x", function (d, i) {
            return (i + 1) * 20;
        });

    // add a text element
    d3.select(element).select("#legenda").append("text")
        .attr("x", "140").attr("y", "40").text("Max: " + Math.round(qMax*100)/100)
}


var MAP;

(function () {

    var instance;

    MAP = function MAP(db, tiles_url, polymaps, protovis) {

        if (instance) {
            return instance; // [Singleton]
        }

        instance = this;

        // all the functionality
        this.db = db;
        this.tiles_url = tiles_url || ("http://{S}tile.cloudmade.com"
            + "/1a1b06b230af4efdbb989ea99e9841af" // http://cloudmade.com/register
            + "/20760/256/{Z}/{X}/{Y}.png");
        this.po = polymaps;
        this.pv = protovis;
        this.map = undefined;
        this.quantiles = {};
        this.layers = {};
        this.legend_mapping = {
            'costo': "Milioni di €",
            'pagamento': "Milioni di €",
            'numero' : 'Progetti'
        };


        // rewrite the contructor [Singleton]
        MAP = function () {
            return instance;
        };

        this.build = function(el, extent, zoomlev, zoomrange) {
            this.map = this.po.map()
                .container(document.getElementById(el).appendChild(this.po.svg("svg")))
                .add(this.po.arrow())
                .add(this.po.drag())
                .add(this.po.dblclick());

            // autocompute the zoom from the extent
            // zoom to zoomlev if specified in the django app
            var z = Math.floor(this.map.extent(extent).zoomBy(-0.25).zoom());
            var zrange = [z-1, z+1];
            if (zoomlev !== null) z = zoomlev;
            if (zoomrange !== null) zrange = zoomrange;
            this.map.zoom(z).zoomRange(zoomrange);

            // add map background tiles
            this.map.add(this.po.image()
                .url(this.po.url(this.tiles_url).hosts(["a.", "b.", "c.", ""])));

            // set map styles
            this.map.container().setAttribute("class", "Greys");

        };

        this.add_layer = function(name, dataset) {

            name = name || 'regioni';
            dataset = dataset || 'costo';

            if (this.quantiles[name] == undefined) {
                this.quantiles[name] = this.pv.Scale.quantile()
                    .quantiles(9)
                    .domain(pv.values( this.db[name][dataset]))
                    .range(0, 8);
            }

            if (this.layers[name] == undefined) {
                this.layers[name] = this.po.geoJson()
                    .url(this.tiles_url +"/oc-regions/{Z}/{X}/{Y}.geojson")
                    .on("load", this._load_layer(name, dataset) )
                    .id("regioni");
            }

            this.map.add(this.layers[name]);

            this.map.add(this.po.compass()
                .pan("none"));

            this.build_legend(name, dataset);

        };

        this._load_layer = function( name, dataset ) {

            return function( geojson ) {

                for (var i = 0; i < geojson.features.length; i++) {
                    var feature = geojson.features[i];
                    var d = this.db[name][dataset][feature.data.properties.cod_reg];
                    var id = feature.data.properties.id;
                    feature.element.setAttribute("class", "q" + this.quantiles[name](d) + "-" + 9);
                    feature.element.appendChild(this.po.svg("title").appendChild(
                        document.createTextNode(feature.data.properties.denominazione + ": " + addCommas(d.toFixed(0)) + " €"))
                        .parentNode);

                    feature.element.setAttribute("ref", feature.data.properties.id);
                }
            }.bind(this);
        }

        this.build_legend = function(name, dataset) {
            // Insert legend
            var legend = d3.select("#map svg")
                .insert("svg:g", ".compass")
                .attr("id", "legenda").attr("class", "TODO")
                .attr("transform", "translate(400,30)");


            legend.append("svg:rect")
                .attr("x", "-20").attr("y", "-20")
                .attr("width", "120").attr("height", "160")
                .attr("class", "back")


            legend.append("svg:text")
                .attr("x", "0")
                .attr("y", "0")
                .attr("font-size", "11")
                .text(self.legend_mapping[name])

// add the various blocks of the legenda
            legend.selectAll("circle")
                .data(d3.range(0, 9))
                .enter()
                .append("svg:circle")
                .attr("r", "6").attr("cx", "0")
                .attr("class", function (d, i) {
                    return "q" + i + "-9";
                })
                .attr("cy", function (d, i) {
                    return (i + 1) * 14;
                })

            legend.selectAll("text.quantiles")
                .data(d3.range(0, 9))
                .enter()
                .append("svg:text")
                .attr("class", "quantiles")
                .attr("font-size", "11")
                .attr("x", "10")
                .attr("y", function (d, i) {
                    return (i + 1) * 14 + 4;
                })
                .text(function (d, i) {
                return (this.quantiles[dataset].quantiles()[i] / 1000000).toFixed(2) + " - " +
                    (this.quantiles[dataset].quantiles()[i+1] / 1000000).toFixed(2);
            }.bind(this));
        }

    };
}());

//// variables taken from django views
//var data = {{ data|safe }}
//var ext = {{ extent }};
//var zoomlev = {{ zoomlev|default:"null" }};
//var zoomrange = {{ zoomrange|default:"null" }};

$(document).ready(function() {

// polymaps object
po = org.polymaps;

// Compute noniles.
quantiles = {};
quantiles['regioni'] = pv.Scale.quantile()
    .quantiles(9)
    .domain(pv.values(data['regioni']['costo']))
    .range(0, 8);
quantiles['province'] = pv.Scale.quantile()
    .quantiles(9)
    .domain(pv.values(data['province']['costo']))
    .range(0, 8);

 map = po.map()
    .container(document.getElementById("map").appendChild(po.svg("svg")))
    .add(po.arrow())
    .add(po.drag())
    .add(po.dblclick());


// autocompute the zoom from the extent
// zoom to zoomlev if specified in the django app
var z = Math.floor(map.extent(ext).zoomBy(-0.25).zoom());
var zrange = [z-1, z+1];
if (zoomlev !== null) z = zoomlev;
if (zoomrange !== null) zrange = zoomrange;
map.zoom(z).zoomRange(zoomrange);

map.add(po.image()
    .url(po.url("http://{S}tile.cloudmade.com"
    + "/1a1b06b230af4efdbb989ea99e9841af" // http://cloudmade.com/register
    + "/20760/256/{Z}/{X}/{Y}.png")
    .hosts(["a.", "b.", "c.", ""])));

/*
 map.add(po.image()
 .url(po.url("{{ TILESTACHE_URL }}/osm-proxy/{Z}/{X}/{Y}.png")
 .hosts(["a.", "b.", "c.", ""]))
 )
 */

var layers = {}
layers['regioni'] = po.geoJson()
    .url(TILESTACHE_URL +"/oc-regions/{Z}/{X}/{Y}.geojson")
    .on("load", load_regioni)
    .id("regioni");

layers['province'] = po.geoJson()
    .url(TILESTACHE_URL+ "/oc-provinces/{Z}/{X}/{Y}.geojson")
    .on("load", load_province)
    .id("province");

map.add(layers['regioni']);

map.add(po.compass()
    .pan("none"));

// Insert legend
var legend = d3.select("#map svg")
    .insert("svg:g", ".compass")
    .attr("id", "legenda").attr("class", "TODO")
    .attr("transform", "translate(400,30)");


legend.append("svg:rect")
    .attr("x", "-20").attr("y", "-20")
    .attr("width", "120").attr("height", "160")
    .attr("class", "back")


legend.append("svg:text")
    .attr("x", "0")
    .attr("y", "0")
    .attr("font-size", "11")
    .text("Milioni di €")

// add the various blocks of the legenda
legend.selectAll("circle")
    .data(d3.range(0, 9))
    .enter()
    .append("svg:circle")
    .attr("r", "6").attr("cx", "0")
    .attr("class", function (d, i) {
        return "q" + i + "-9";
    })
    .attr("cy", function (d, i) {
        return (i + 1) * 14;
    })

legend.selectAll("text.quantiles")
    .data(d3.range(0, 9))
    .enter()
    .append("svg:text")
    .attr("class", "quantiles")
    .attr("font-size", "11")
    .attr("x", "10")
    .attr("y", function (d, i) {
        return (i + 1) * 14 + 4;
    })
    .text(function (d, i) {
        return (quantiles['regioni'].quantiles()[i] / 1000000).toFixed(2) + " - " +
            (quantiles['regioni'].quantiles()[i+1] / 1000000).toFixed(2);
    });


    map.container().setAttribute("class", "Greys");

    $('#selectors #regioni').click(function(){
        map.remove(layers['province']);
        map.add(layers['regioni']);
        map.remove(po.compass());
        map.add(po.compass()
            .pan("none"));
        $(this).addClass("active");
        $('#selectors #province').removeClass("active");
        return false;
    })
    $('#selectors #province').click(function(){
        map.remove(layers['regioni']);
        map.add(layers['province']);
        map.remove(po.compass());
        map.add(po.compass()
            .pan("none"));
        $(this).addClass("active");
        $('#selectors #regioni').removeClass("active");
        return false;
    })




}); // close document.ready

function load_regioni(e) {
    console.log(e);
    for (var i = 0; i < e.features.length; i++) {
        var feature = e.features[i];
        var d = data['regioni']['costo'][feature.data.properties.cod_reg];
        var id = feature.data.properties.id;
        feature.element.setAttribute("class", "q" + quantiles['regioni'](d) + "-" + 9);
        feature.element.appendChild(po.svg("title").appendChild(
            document.createTextNode(feature.data.properties.denominazione + ": " + addCommas(d.toFixed(0)) + " €"))
            .parentNode);

        feature.element.setAttribute("ref", feature.data.properties.id);

        /*
         // disable click on drag
         feature.element.addEventListener("click", function(ev){
         alert("http://localhost:8020/" + this.getAttribute("ref"))
         });
         */

    }
}

function load_province(e) {
    for (var i = 0; i < e.features.length; i++) {
        var feature = e.features[i];
        var d = data['province']['costo'][feature.data.properties.cod_prov];
        var id = feature.data.properties.id;
        feature.element.setAttribute("class", "q" + quantiles['province'](d) + "-" + 9);
        feature.element.appendChild(po.svg("title").appendChild(
            document.createTextNode(feature.data.properties.denominazione + ": " + addCommas(d.toFixed(0)) + " €"))
            .parentNode);

        feature.element.setAttribute("ref", feature.data.properties.id);

        /*
         // disable click on drag
         feature.element.addEventListener("click", function(ev){
         alert("http://localhost:8020/" + this.getAttribute("ref"))
         });
         */

    }
}
