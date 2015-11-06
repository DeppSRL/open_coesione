$(document).ready(function() {
    var width = 700,
        height = 700,
        minSqPixToShow = 5000;

    var color = d3.scale.ordinal()
        .domain(["Fondi Europei", "Fondi Nazionali", "FAS", "Piano di Azione per la coesione"])
        .range(["#3e725c", "#9aac9e", "#92c7a8", "#d8e9dd"]);

    var treemap = d3.layout.treemap()
        .mode("squarify")
        .sort(comparator)
        .padding(5)
        .size([width, height]);

    var svg = d3.select("#graph").append("svg")
        .attr("width", width)
        .attr("height", height)
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
            tspan = text.append("tspan").attr("dy", lineHeight + "em").attr("x", d.dx / 2),
            width = d.dx - 8;

        while (word = words.pop()) {
            line.push(word);
            tspan.text(line.join(" "));
            if (tspan.node().getComputedTextLength() > width) {
                line.pop();
                tspan.text(line.join(" "));
                line = [word];
                tspan = text.append("tspan").attr("dy", lineHeight + "em").attr("x", d.dx / 2).text(word);
            }
        }
    }

    function leafWrap(d) {
        var text = d3.select(this),
            words = (d.name + ":").split(/\s+|\-/).reverse(),
            word,
            line = [],
            lineHeight = 1.1,
            tspan = text.append("tspan").attr("dy", 0).attr("x", d.dx / 2),
            width = d.dx - 8;

        while (word = words.pop()) {
            line.push(word);
            tspan.text(line.join(" "));
            if (tspan.node().getComputedTextLength() > width) {
                line.pop();
                tspan.text(line.join(" "));
                line = [word];
                tspan = text.append("tspan").attr("dy", lineHeight + "em").attr("x", d.dx / 2).text(word);
            }
        }
        text.append("tspan").attr("dy", lineHeight + "em").attr("x", d.dx / 2).text(d.value);
    }

    var json = {name: "", children: []};

    d3.csv("/static/csv/spesatot_data.csv", function (rows) {

        /* convert the CSV file into a json tree,
         each object has a name and children property, children is an array of object. Leaf have name and value property */

        rows.forEach(function (row) {
            var L1 = row.L1,
                L2 = row.L2,
                L3 = row.L3,
                value = row.value;

            var LevelFound = 0;
            var nodeFound;

            json.children.forEach(function (d) {
                if (d.name == L1) {
                    LevelFound = 1;
                    nodeFound = d;
                }
            });

            if (LevelFound == 0) {
                nodeFound = {"name": L1, "children": []};
                json.children.push(nodeFound);
            }

            LevelFound = 0;

            var L2nodeFound;
            nodeFound.children.forEach(function (d) {
                if (d.name == L2) {
                    LevelFound = 1;
                    L2nodeFound = d;
                }
            });

            if (LevelFound == 0) {
                L2nodeFound = {"name": L2, "children": []};
                nodeFound.children.push(L2nodeFound);
            }

            L2nodeFound.children.push({"name": L3, "value": value});
        });
        /* compute once the array of node (see d3 doc, set x,y,widht and height for all nodes) */
        var treeMapNodesArray = treemap.nodes(json);

        /* First compute the legends, filter on depth==1 to get first level only */
        var legend = d3.select("#legend").selectAll("div")
            .data(treeMapNodesArray.filter(function (d) {
                return d.depth <= 1
            }))
            .enter()
            .append("div")
            .attr("class", "topSection")
            .attr("id", function (d) {
                return "div" + d.name.replace(/\W/g, '')
            })
            /* On mouseover the legend div, highlight the matching level 1 element */
            .on("mouseover", function (d) {
                $("#rec" + d.name.replace(/\W/g, '')).attr("class", "D1 rectHighlight");
            })
            .on("mouseout", function (d) {
                $("#rec" + d.name.replace(/\W/g, '')).attr("class", "D1");
            })
            .html(function (d) {
                if (d.depth == 0) return " <span class='value total'>" + parseFloat(d.value).toFixed(1) + "</span>";
                return "<div class='button' style='background-color:" + color(d.name) + "'> </div>" + d.name + " <span class='value'>" + parseFloat(d.value).toFixed(1) + "</span>"
            })
            .sort(function (a, b) {
                return b.depth - a.depth;
            });
        /* sort to get the level 1 first and level 0 at the end of the list */

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
            .attr("id", function (d) {
                return d.depth == 1 ? "rec" + d.name.replace(/\W/g, '') : null
            })
            .attr("transform", function (d) {
                return "translate(" + d.x + "," + d.y + ")";
            })
            .sort(function (a, b) {
                return b.depth - a.depth;
            });
        /* sort to get the deepest level first so we will have the level 1 on top and be able to get onmouseover event on it */

        cell.append("rect")
            .attr("width", function (d) {
                return d.dx - 2;
            })
            .attr("height", function (d) {
                return d.dy - 2;
            })
            .style("fill", function (d) {
                if (d.depth == 3) return color(d.parent.parent.name);
                /* only level 3 element got a color picked from level 1 parent name */
                return "orange";
            }) /* others are orange filled but transparent by default, just used to highlight them on mouseover */
            .style("stroke", function (d) {
                if (d.depth == 1) return color(d.name);
                if (d.depth == 2) return color(d.parent.name);
                return "#fff"
            })
            .style("stroke-width", function (d) {
                if (d.depth == 1) return 2;
                if (d.depth == 2) return 2;
                return 1;
            });

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

        /* Set the text in second level rectangle: name only */
        d3.selectAll(".D2").append("text")
            .filter(function (d) {
                return d.dx * d.dy > minSqPixToShow;
            })
            .attr("x", function (d) {
                return d.dx / 2;
            })
            .attr("y", 3)
            .attr("dy", ".35em")
            .attr("text-anchor", "middle")
            .attr("fill", "white")
            .each(wrap);

        /* Add a rectangle behind level2 text to hide lower level border properly */
        d3.selectAll(".D2").insert("rect", "text")
            .style("fill", function (d) {
                return color(d.parent.name);
            })
            .attr("class", "label")
            .attr("x", function (d) {
                return this.nextSibling.getBBox().x;
            })
            .attr("y", function (d) {
                return this.nextSibling.getBBox().y;
            })
            .attr("width", function (d) {
                return this.nextSibling.getBBox().width;
            })
            .attr("height", function (d) {
                return this.nextSibling.getBBox().height;
            });


        /* manage onmouseover event on level 1 elements, highlight the matching legend div */
        d3.selectAll(".D1")
            .on("mouseover", function (d) {
                $("#div" + d.name.replace(/\W/g, '')).toggleClass("topSectionHighlight");
            })
            .on("mouseout", function (d) {
                $("#div" + d.name.replace(/\W/g, '')).toggleClass("topSectionHighlight");
            });

    });

});