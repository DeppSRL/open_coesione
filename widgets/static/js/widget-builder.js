// fix window location origin for old browsers
if (!window.location.origin)
    window.location.origin = window.location.protocol + "//" + window.location.host;

window.WidgetBuilder = (function(window, undefined) {
    var builder = function(form, preview, embed) {

    }
});

window.Widgets.collectParams = function () {
    var inputParams = {
        base_url: window.location.origin
    };
    _.each($('#widget-builder').serializeArray(), function (el) {
        if (el.name != undefined && el.name != '') {
            console.log(el.name, _.has(inputParams, el.name), inputParams);
            if (_.has(inputParams, el.name)) {
                if (_.isArray(inputParams[el.name])) {
                    inputParams[el.name].push(el.value);
                } else {
                    inputParams[el.name] = [inputParams[el.name], el.value];
                }
            } else {
                inputParams[el.name] = el.value;
            }
        }
    });
    return inputParams;
};

window.Widgets.formatValue = function (value) {
    return _.escape(_.isArray(value) ? value.join(',') : value);
};

window.Widgets.createEmbedDiv = function (params) {
    var el = _.reduce(_.keys(params), function (memory, key) {
        return memory + ' data-' + key + '="' + formatValue(params[key]) + '"';
    }, '<div class="widget-opencoesione"');
    el += '></div>';
    return el;
};

window.Widgets.createEmbedScript = function () {
    var url = "http://{{ request.get_host }}{{ STATIC_URL }}js/widgets.js";
    return '<script id="opencoesione-loader" src="' + url + '" async ><\/script>';
};

window.Widgets.embedCode = function (params) {
    var code = createEmbedDiv(params || {}) + createEmbedScript();
    $('#embed_code_preview').empty().html(code);
    return code;
};



var loadWidget = function () {
    $('#id_embed_code').val(embedCode(collectParams()));
};

$(function () {

    $('#id_embed_code').on('click', function () {
        $(this).focus();
        $(this).select();
    });

    $('#widget-builder').on('submit', function () {
        loadWidget();
        return false;
    });


    // start all
    loadWidget();
});