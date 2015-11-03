$(document).ready(function() {
    $('#location').on('focus', function() {
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
                            url: item.url,
                            cod_com: item.cod_com,
                            cod_prov: item.cod_prov,
                            cod_reg: item.cod_reg
                        }
                    }));
                }
            );
        },
        minLength: 2,
        select: function(event, ui) {
            $('#territorio-com').val(ui.item.cod_com);
            $('#territorio-prov').val(ui.item.cod_prov);
            $('#territorio-reg').val(ui.item.cod_reg);
        },
        open: function() {
            $(this).removeClass('ui-corner-all').addClass('ui-corner-top');
        },
        close: function() {
            $(this).removeClass('ui-corner-top').addClass('ui-corner-all');
        }
    }).css('z-index', 999);

    function handle_keydown(event) {
        // track enter key
        var keycode = (event.keyCode ? event.keyCode : (event.which ? event.which : event.charCode));
        if (keycode == 13) { // keycode for enter key
            // force the 'Enter Key' to implicitly click the Update button
            document.getElementById('search-button').click();
            return false;
        } else {
            return true;
        }
    }

    $('#query').bind('keydown', handle_keydown);
    $('#clear-query').on('click', function() {
        $('#query').val('');
        document.getElementById('search-button').click();
    });

    $('#location').bind('keydown', handle_keydown);

    $('#clear-location').on('click', function() {
        $('#location').val('');
        $('#territorio-com').val('');
        $('#territorio-prov').val('');
        $('#territorio-reg').val('');
        document.getElementById('search-button').click();
    });
});
