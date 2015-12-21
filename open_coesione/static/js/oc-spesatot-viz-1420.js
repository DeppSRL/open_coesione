$(document).ready(function(){
    /* set the locale for numeral library */
    numeral.language('it', {
        delimiters: {
            thousands: '.',
            decimal: ','
        },
        abbreviations: {
            thousand: 'mila',
            million:  'mln',
            billion:  'mld',
            trillion: 'trl'
        },
        currency: {
            symbol: '€'
        }
    });

    numeral.language('it');

    var width = $('#spesatot_viz').innerWidth(),
        height = width,
        minSqPixToShow = 5000;

    /* This one is used to map colors and URL from L1 values in the .csv so modify it in case of top level domain */
    var domainL1 = ["Fondi SIE", "CTE", "FEAD", "Programmi Complementari e PAC", "Fondo FSC"];

    var color = d3.scale.ordinal()
        .domain(domainL1)
        .range(["#3e725c", "#9aac9e", "#92c7a8", "#d8e9dd", "#ddffdd"]);

    /* set the URLs to be linked with L1 values from .csv, WARNING: match the order of the above domainL1 definition */
    var urlL1 = d3.scale.ordinal()
        .domain(domainL1)
        .range(["/fonti-di-finanziamento/fesr/", "/fonti-di-finanziamento/fsc/", "/fonti-di-finanziamento/fas/", "/fonti-di-finanziamento/pac/", "/fonti-di-finanziamento/pic/"]);

    var treemap = d3.layout.treemap()
        .mode("squarify")
        .sort(comparator)
        .padding(2)
        .size([width, height]);

    var svg = d3.select("#graph").append("svg")
        .attr("width", width)
        .attr("height",height)
        .append("g")
        .attr("transform", "translate(-.5,-.5)");

    function comparator(a, b) {
        return a.value - b.value;
    }

    function wrap(d) {
        var text = d3.select(this),
        words = d.name.split(/\s+/).reverse(),
        word,
        line = [],
        lineHeight = 1.1,
        tspan = text.append("tspan").attr("dy", lineHeight + "em").attr("x", d.dx/2),
        width = d.dx-8;

        while (word = words.pop()) {
            line.push(word);
            tspan.text(line.join(" "));
            if (tspan.node().getComputedTextLength() > width) {
                line.pop();
                tspan.text(line.join(" "));
                line = [word];
                tspan = text.append("tspan").attr("dy", lineHeight + "em").attr("x", d.dx/2).text(word);
            }
        }
    }

    function leafWrap(d) {
        var text = d3.select(this),
        words = d.name.split(/\s+|\-/).reverse(),
        word,
        line = [],
        lineHeight = 1.1,
        tspan = text.append("tspan").attr("dy", 0).attr("x", d.dx/2),
        width = d.dx-8;

        while (word = words.pop()) {
            line.push(word);
            tspan.text(line.join(" "));
            if (tspan.node().getComputedTextLength() > width) {
                line.pop();
                tspan.text(line.join(" "));
                line = [word];
                tspan = text.append("tspan").attr("dy", lineHeight + "em").attr("x", d.dx/2).text(word);
            }
        }
        text.append("tspan").attr("dy", lineHeight + "em").attr("x", d.dx/2).text(numeral(+d.value).format('0,0.00'));
    }

    var json = { name:"", children:[]};
    var treeMapNodesArray;

    d3.csv("/static/csv/spesatot_data_1420.csv", function(rows) {

        /* convert the CSV file into a json tree,
         each object has a name and children property, children is an array of object. Leaf have name and value property */

        rows.forEach(function(row){
            var L1 = row.L1,
                L2 = row.L2,
                L3 = row.L3,
                value = row.value;

            var LevelFound = 0;
            var nodeFound;

            json.children.forEach(function (d){
                if (d.name == L1) {
                    LevelFound = 1;
                    nodeFound = d;
                }
            });

            if (LevelFound == 0) {
                nodeFound = {"name":L1, "children":[]};
                json.children.push(nodeFound);
            }

            LevelFound = 0;

            var L2nodeFound;
            nodeFound.children.forEach(function (d){
                if (d.name == L2) {
                    LevelFound = 1;
                    L2nodeFound = d;
                }
            });

            if (LevelFound == 0) {
                L2nodeFound = {"name":L2, "children":[]};
                nodeFound.children.push(L2nodeFound);
            }

            L2nodeFound.children.push({"name":L3, "value":value});
        });

        /* compute once the array of node (see d3 doc, set x,y,width and height for all nodes) */
        treeMapNodesArray = treemap.nodes(json);

        drawTreemap();

        /* on windows resize, we shall redraw the treemap*/
        $(window).resize(function () {
            width = $('#spesatot_viz').innerWidth(); /* get the new size */
            height = width;
            treemap.size([width, height]);
            d3.select("#graph").select("svg")
                .attr("width", width)  /* modify svg element width and height*/
                .attr("height",height)
                .select("g").selectAll("g").remove(); /* delete all children node in svg/g/* */
            treeMapNodesArray = treemap.nodes(json); /* recompute the treemap nodes with the new size */
            drawTreemap(); /* draw it */
        });
    });

    function drawTreemap() {
        /* Then add the graph itself, skip level 0 to have the level 1 on top to be able to get the mouseover event on them */
        var cell = svg.selectAll("g")
            .data(treeMapNodesArray.filter(function (d) {
                return d.depth != 0
            }))
            .enter().append("g")
            .attr("class", function (d) {
                return d.children ? "D" + d.depth : "leaf";
                /* set a class, leaf for last level, D<level> for the others */
            })
            .attr("transform", function (d) {
                return "translate(" + d.x + "," + d.y + ")";
            })
            .sort(function (a, b) {
                return b.depth - a.depth;
            });
        /* sort to get the deepest level first so we will have the level 1 on top and be able to get onmouseover event on it */

	/* append rect and manage fills to all the non top-level cells */
        cell.filter(function (d){
                return d.depth>1;
            })
	    .append("rect")
            .attr("width", function (d) {
                return d.dx - 2;
            })
            .attr("height", function (d) {
                return d.dy - 2;
            })
            .style("fill", function (d) {
                if (d.depth==3) return color(d.parent.parent.name); /* level 3 element got a color picked from level 1 parent name */
                return "none"; /* others are transparents */
            })
            .style("stroke-width", 0);

        /* Set the text in leaf: name and value */
        d3.selectAll(".leaf")
            .filter(function (d) {
                return d.dx * d.dy > minSqPixToShow;
            }) /* no text in that area when too small */
            .append("text")
            .attr("x", function (d) {
                return d.dx / 2;
            })
            .attr("y", function (d) {
                return d.dy / 2;
            })
            .attr("text-anchor", "middle")
            .attr("fill", "black")
            .each(leafWrap);
        /* this will wrap name and value into the available rectangle */

        /* Set the text in second level rectangle: name only, color is picked from parent name */
        d3.selectAll(".D2").append("text")
            .filter(function (d) {
                return d.dx * d.dy > minSqPixToShow;
            })
            .attr("x", function (d) {
                return d.dx / 2;
            })
            .attr("y", 3)
            .attr("dy", 0)
            .attr("text-anchor", "middle")
            .attr("fill", function (d) {
                return color(d.parent.name);
            })
            .each(wrap);

        /* Add a white rectangle behind level2 text to make it looks like it's out of the box */
        d3.selectAll(".D2").insert("rect", "text")
            .style("fill", "white")
            .attr("class", "label")
            .attr("x", function (d) {
                return this.previousSibling.getBBox().x;
            })
            .attr("y", function (d) {
                return this.nextSibling.getBBox().y-5;
            })
            .attr("width", function (d) {
                return this.previousSibling.getBBox().width;
            })
            .attr("height", function (d) {
                return this.nextSibling.getBBox().height+6;
            });


	/* Append a link to the top level elements */
        var d1Cells = d3.selectAll(".D1")
	    .append("a")
	    .attr("xlink:href", function (d) {
		    return urlL1(d.name);
	    });


	/* Append a rect and a text in the the top level elements link */
	d1Cells.append("rect")
            .attr("width", function (d) {
                return d.dx - 2;
            })
            .attr("height", function (d) {
                return d.dy - 2;
            })
            .style("fill", function (d) {
                return color(d.name); /* level 1 element got a color picked from their name */
            })
            .style("stroke-width", 4);

        d1Cells.append("text")
            .attr("x", function (d) {
                return d.dx / 2;
            })
            .attr("y", function (d) {
                return d.dy / 2;
            })
            .attr("text-anchor", "middle")
            .each(leafWrap);
    }

});
