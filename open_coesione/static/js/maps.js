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

if (typeof String.prototype.startsWith != 'function') {
    String.prototype.startsWith = function (str){
        return this.indexOf(str) == 0;
    };
}

var MAP;
var the_last;

(function () {

    var instance; // [Singleton]

    MAP = function MAP(db, geojson_url, tiles_url, d3, polymaps, protovis) {

        if (instance) {
            return instance; // [Singleton]
        }

        instance = this; // [Singleton]

        // all the functionality
        this.db = db;
        this.geojson_url = geojson_url;
        this.tiles_url = tiles_url;
        this.po = polymaps;
        this.pv = protovis;
        this.d3 = d3;
        this.map = undefined;
        this.last_layer = undefined;
        this.legend = undefined;
        this.quantiles = {};
        this.layers = {};
        this.legend_titles = {
            'costo': "Milioni di €",
            'pagamento': "Milioni di €",
            'numero' : 'Progetti'
        };
        this.currency_mapping = {
            'costo': "€",
            'pagamento': "€",
            'numero' : 'progetti'
        };
        this.legend_quantile_func = {
            'costo' : function (d, i) {
                return (this['costo'].quantiles()[i] / 1000000).toFixed(2) + " - " + (this['costo'].quantiles()[i+1] / 1000000).toFixed(2);
            },
            'pagamento' : function (d, i) {
                return (this['pagamento'].quantiles()[i] / 1000000).toFixed(2) + " - " + (this['pagamento'].quantiles()[i+1] / 1000000).toFixed(2);
            },
            'numero' : function (d, i) {
                return this['numero'].quantiles()[i] + " - " + this['numero'].quantiles()[i+1];
            }
        };
        this.property_mapping = function(name) {
            if (name=='regioni') return 'cod_reg';
            if (name.startsWith('province')) return 'cod_prov';
            if (name.startsWith('comuni')) return 'cod_com';
        };
        this.sort_unique = function(arr) {
            arr = arr.sort(function (a, b) { return a*1 - b*1; });
            var ret = [arr[0]];
            for (var i = 1; i < arr.length; i++) { // start loop at 1 as element 0 can never be a duplicate
                if (arr[i-1] !== arr[i]) {
                    ret.push(arr[i]);
                }
            }
            return ret;
        };



        // rewrite the contructor [Singleton]
        MAP = function () {
            return instance;
        };

        this.build = function(el, extent, zoomlev, zoomrange) {

            //console.log('build map in #' + el, extent, zoomlev, zoomrange)

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
            this.map.add(
                this.po.image()
                    .url(this.po.url(this.tiles_url).hosts(["a.", "b.", "c.", ""]))
            );

            // set map styles
            this.map.container().setAttribute("class", "Greys");

        };

        this.onLayerShow = function( geojson ) {

            for (var i = 0; i < geojson.features.length; i++) {
                var feature = geojson.features[i];
                //console.log(feature.data);
                var d = this.db[this.new_name][this.new_dataset][feature.data.properties[ this.property_mapping(this.new_name) ]] || 0.0;
                var id = feature.data.properties.id;
                // resetting
                if ( feature.element.hasChildNodes() ) {
                    while (feature.element.childNodes[0]) {
                        feature.element.removeChild(feature.element.childNodes[0]);
                    }
                    //feature.element.removeChild(feature.element.children[0]);
                }
                feature.element.setAttribute("class", "q" + this.quantiles[this.new_name][this.new_dataset](d) + "-" + 5);
                feature.element.appendChild(this.po.svg("title").appendChild(
                    document.createTextNode(feature.data.properties.denominazione + ": " + addCommas(d.toFixed(0)) + " " + this.currency_mapping[this.new_dataset]))
                    .parentNode);

                feature.element.setAttribute("ref", feature.data.properties.id);

                the_last = feature.element;

                $(feature.element).click(function(e){
                    $('.popoverable').popover('hide');
                    $(this).popover('toggle');
                });
                // #TODO change me
                $(feature.element).addClass('popoverable').popover({
                    placement: function(el) {
                        //console.log('element',el);
                        $(el).css({
                            'top' : $(el).height() /2,
                            'left' : $(el).width() /2
                        });
                        return 'top';
                    },
                    title: '<a href="/territori/'+this.new_name.split('-')[0]+'/'+ feature.data.properties.denominazione.toLowerCase() +'/">'+ feature.data.properties.denominazione +'</a>',
                    content: '' +
                        '<br>Finanziamento pubblico: ' + addCommas(
                            (this.db[this.new_name]['costo'][feature.data.properties[ this.property_mapping(this.new_name) ]] || 0.0).toFixed(0)) +
                        '<br>Pagamenti effettuati: ' + addCommas(
                            (this.db[this.new_name]['pagamento'][feature.data.properties[ this.property_mapping(this.new_name) ]] || 0.0).toFixed(0)) +
                        '<br>Numero di progetti: ' + this.db[this.new_name]['numero'][feature.data.properties[ this.property_mapping(this.new_name) ]] +
                        '',
                    trigger:'manual',
                    delay: { show: 500, hide: 100 }
                });

//                $(feature.element).hover(function(){
//                    $(this).popover('show')
//                });
            }
        };

        this.add_point = function(pnt) {
            this.map.add(this.po.geoJson()
                .features([{geometry: {coordinates: pnt, type: "Point"}}])
                //.stylist().attr('class','poi')
                .on("load", function(e) { $(e.features[0]).addClass('poi'); })
            );
        };

        this.add_layer = function(name, dataset) {

            name = name || 'regioni';
            dataset = dataset || 'costo';

            // console.log('add layer', name, dataset, '~ currently', this.new_name, this.new_dataset, (this.new_name == name) && (this.new_dataset == dataset));

            if ( (this.new_name == name) && (this.new_dataset == dataset) ) {
                // console.log('already show');
                return ;
            }

            this.new_name = name;
            this.new_dataset = dataset;

            if ( ! (name in this.quantiles) ) {
                this.quantiles[name] = {};
            }
            if ( ! (dataset in this.quantiles[name]) ) {
                this.quantiles[name][dataset] = this.pv.Scale.quantile()
                    .quantiles(5)
                    .domain(this.sort_unique(pv.values(this.db[name][dataset])))
                    .range(0, 4);
            }

//            if ( ! (name in this.layers) ) {
//                this.layers[name] = {};
//            }
//            if ( ! ( dataset in this.layers[name] ) ) {
            if ( ! (name in this.layers)) {
                //this.layers[name][dataset] = this.po.geoJson()
                this.layers[name] = this.po.geoJson()
                    .url(this.geojson_url +"/"+ "oc-" + name +"/{Z}/{X}/{Y}.geojson")
                    //.on("load", this._load_layer(name, dataset) )
                    .on("load", this.onLayerShow.bind(this) )
                    .id(name);
            }
            else {
                this.layers[name].on("show", this.onLayerShow.bind(this) );
            }

//            if ( this.last_layer == this.layers[name][dataset] ) {
//            if ( this.last_layer == this.layers[name] ) {
//                return; // skip if it is the same
//            }

//            this.map.add(this.layers[name][dataset]);
            this.map.add(this.layers[name]);

            if ( this.last_layer ) {
                if ( this.last_layer == this.layers[name] ) {
                    this.last_layer.reshow();
                }
                else
                {
                    // remove last
                    this.map.remove( this.last_layer );
                }
            }

            d3.select('#map .compass').remove();
            this.map.add(this.po.compass()
                .pan("none"));

            d3.select('#legenda').remove();
            this.build_legend(name, dataset);

//            this.last_layer = this.layers[name][dataset];
            this.last_layer = this.layers[name];

        };


        this.build_legend = function(name, dataset) {

            var title = this.legend_titles[dataset];
            var level_text_func = this.legend_quantile_func[dataset].bind(this.quantiles[name]);

            // Insert legend
            this.legend = this.d3.select("#map svg")
                .insert("svg:g", ".compass")
                .attr("id", "legenda").attr("class", "TODO")
                .attr("transform", "translate(450,30)");

            this.legend.append("svg:rect")
                .attr("x", "-20").attr("y", "-20")
                .attr("width", "120").attr("height", "120")
                .attr("class", "back");


            this.legend.append("svg:text")
                .attr("x", "0")
                .attr("y", "0")
                .attr("font-size", "11")
                .text(title);

            // add the various blocks of the legenda
            this.legend.selectAll("circle")
                .data(this.d3.range(0, 5))
                .enter()
                .append("svg:circle")
                .attr("r", "6").attr("cx", "0")
                .attr("class", function (d, i) {
                    return "q" + i + "-5";
                })
                .attr("cy", function (d, i) {
                    return (i + 1) * 14;
                });

            this.legend.selectAll("text.quantiles")
                .data(this.d3.range(0, 5))
                .enter()
                .append("svg:text")
                .attr("class", "quantiles")
                .attr("font-size", "11")
                .attr("x", "10")
                .attr("y", function (d, i) {
                    return (i + 1) * 14 + 4;
                })
                .text(
                level_text_func
            );
        }

    };
}());