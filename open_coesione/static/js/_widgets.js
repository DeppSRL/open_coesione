/**
 * Created by daniele on 16/10/13.
 */

!(function(d, w){

    if (!w.console) w.console = {};
    if (!w.console.log) w.console.log = function () { };

    var EMBED_DIV_CLASSNAME = 'widget-opencoesione';

    var Opencoesione = w.Opencoesione || {};
    w.Opencoesione = Opencoesione;

    if(!Opencoesione.foundEls) Opencoesione.foundEls = [];
    var foundEls = Opencoesione.foundEls;

    Opencoesione.locateElements = function(klass){
        return Opencoesione.getElementsByClassName(klass);
    };
    Opencoesione.loadWidget = function(el){
        // extract all data params
        // https://gist.github.com/remy/362081
        var regex = /^data-(.+)/,
            paramsEmbed = {},
            match;
        [].forEach.call(el.attributes, function(attr){
            if (match = attr.name.match(regex)) {
                paramsEmbed[match[1]] = attr.value;
            }
        });
        var width = paramsEmbed['width'] || 460,
            height = paramsEmbed['height'] || 400,
            widget = paramsEmbed['widget'],
            url = paramsEmbed['base_url'] + '/widgets/' + widget +'/?' + encodeQueryData(paramsEmbed);
        el.innerHTML = '<iframe allowtransparency="true" frameBorder="0" scrolling="no" ' +
            'style="border: none; max-width: 100%; min-width: 180px;" ' +
            'width="'+width+'" height="'+height+'" ' +
            'src="'+ url +'"></iframe>';
    };

    /*
    http://stackoverflow.com/questions/111529/create-query-parameters-in-javascript
    */
    var encodeQueryData = Opencoesione.encodeQueryData = function(data) {
       var ret = [];
       for (var d in data)
          ret.push(encodeURIComponent(d) + "=" + encodeURIComponent(data[d]));
       return ret.join("&");
    };

    /*
    Developed by Robert Nyman, http://www.robertnyman.com
    Code/licensing: http://code.google.com/p/getelementsbyclassname/
    */
    var getElementsByClassName = Opencoesione.getElementsByClassName = function (className, tag, elm) {
        if (d.getElementsByClassName) {
            getElementsByClassName = function (className, tag, elm) {
                elm = elm || d;
                var elements = elm.getElementsByClassName(className),
                    nodeName = (tag) ? new RegExp("\\b" + tag + "\\b", "i") : null,
                    returnElements = [],
                    current;
                for (var i = 0, il = elements.length; i < il; i += 1) {
                    current = elements[i];
                    if (!nodeName || nodeName.test(current.nodeName)) {
                        returnElements.push(current);
                    }
                }
                return returnElements;
            };
        }
        else if (d.evaluate) {
            getElementsByClassName = function (className, tag, elm) {
                tag = tag || "*";
                elm = elm || d;
                var classes = className.split(" "),
                    classesToCheck = "",
                    xhtmlNamespace = "http://www.w3.org/1999/xhtml",
                    namespaceResolver = (d.documentElement.namespaceURI === xhtmlNamespace) ? xhtmlNamespace : null,
                    returnElements = [],
                    elements,
                    node;
                for (var j = 0, jl = classes.length; j < jl; j += 1) {
                    classesToCheck += "[contains(concat(' ', @class, ' '), ' " + classes[j] + " ')]";
                }
                try {
                    elements = d.evaluate(".//" + tag + classesToCheck, elm, namespaceResolver, 0, null);
                }
                catch (e) {
                    elements = d.evaluate(".//" + tag + classesToCheck, elm, null, 0, null);
                }
                while ((node = elements.iterateNext())) {
                    returnElements.push(node);
                }
                return returnElements;
            };
        }
        else {
            getElementsByClassName = function (className, tag, elm) {
                tag = tag || "*";
                elm = elm || d;
                var classes = className.split(" "),
                    classesToCheck = [],
                    elements = (tag === "*" && elm.all) ? elm.all : elm.getElementsByTagName(tag),
                    current,
                    returnElements = [],
                    match;
                for (var k = 0, kl = classes.length; k < kl; k += 1) {
                    classesToCheck.push(new RegExp("(^|\\s)" + classes[k] + "(\\s|$)"));
                }
                for (var l = 0, ll = elements.length; l < ll; l += 1) {
                    current = elements[l];
                    match = false;
                    for (var m = 0, ml = classesToCheck.length; m < ml; m += 1) {
                        match = classesToCheck[m].test(current.className);
                        if (!match) {
                            break;
                        }
                    }
                    if (match) {
                        returnElements.push(current);
                    }
                }
                return returnElements;
            };
        }
        return getElementsByClassName(className, tag, elm);
    };

    var els = Opencoesione.locateElements(EMBED_DIV_CLASSNAME),
    nEls = els.length;

    for(var i = 0; i < nEls; i++) {
        var el = els[i];
        if(foundEls.indexOf(el) < 0) {
            foundEls.push(el);
            Opencoesione.loadWidget(el);
        }
    }

})(document, window);
