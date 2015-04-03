$(document).ready(function() {
    if (location.hash == '#delibere-cipe') {
        $('[href=#fondi-nazionali]').tab('show');
        $('#delibere-cipe').scroll();
    } else {
        var active_tab = $('[href=' + location.hash + ']');
        active_tab && active_tab.tab('show');
    }

    $('#chart_table').find('a[href^="#"]').on('click', function() {
        $('.nav-tabs [href=' + $(this).attr('href') + ']').tab('show');
    });
});
