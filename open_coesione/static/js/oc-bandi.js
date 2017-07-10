$(document).ready(function() {
    function initDataTable() {
        $('table.display').not('.dataTable').filter(':visible').dataTable({
            language: {
                url: '//cdn.datatables.net/plug-ins/1.10.15/i18n/Italian.json'
            },
            orderMulti: false,
            order: [[2, 'asc']],
            columns: [
                null,
                {searchable: false, className: 'dt-body-center'},
                {searchable: false, className: 'dt-body-center', orderData: [2, 1]},
                null,
                {searchable: false, className: 'dt-body-right'},
                null
            ]
        });
    }

    $('#bandi').on('shown.bs.tab', 'a', function () {
        initDataTable();
    });

    initDataTable();
});
