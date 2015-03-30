$(document).ready(function() {
    var filetypes = /\.(pdf|zip|csv|xls*)$/i;
    $('a').each(function() {
        var href = $(this).attr('href');
        if (href && (href.match(filetypes) || $(this).data('ga-track'))) {
            $(this).click(function() {
                var extension = (/[.]/.exec(href)) ? /[^.]+$/.exec(href).toString().toUpperCase() : undefined;
                extension = extension || $(this).data('ga-track').toUpperCase();
                _gaq.push(['_trackEvent', 'Download', extension, href]);
                if ($(this).attr('target') != undefined && $(this).attr('target').toLowerCase() != '_blank') {
                    setTimeout(function() { location.href = href; }, 200);
                    return false;
                }
            });
        }
    });
});
