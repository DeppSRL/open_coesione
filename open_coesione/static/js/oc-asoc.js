$(document).ready(function() {
    $('table.display').dataTable({
        language: {
            url: '//cdn.datatables.net/plug-ins/1.10.15/i18n/Italian.json'
        },
        order: []
    }).find('td:last-of-type a').css('white-space', 'nowrap');
});
