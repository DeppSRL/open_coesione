$(document).ready(function() {
    $('#menu-search-territori,#city,#map-city').on('focus', function() {
        if (!$(this)._cleared) {
            $(this)._cleared = true;
            $(this).val('');
        }
    }).autocomplete({
        source: function(request, response) {
            $.getJSON(
                '/territori/autocomplete/',
                {
                    query: request.term
                },
                function(data) {
                    response($.map(data.territori, function(item) {
                        return {
                            label: item.denominazione,
                            url: item.url
                        }
                    }));
                }
            );
        },
        minLength: 2,
        select: function(event, ui) {
            window.location.href = ui.item.url;
        },
        open: function() {
            $(this).removeClass('ui-corner-all').addClass('ui-corner-top');
        },
        close: function() {
            $(this).removeClass('ui-corner-top').addClass('ui-corner-all');
        }
    }).css('z-index', 10);
});
