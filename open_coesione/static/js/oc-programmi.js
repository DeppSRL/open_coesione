function print_spline_chart(container, data) {
    new Highcharts.Chart({
        chart: {
            renderTo: container,
            type: 'spline',
            backgroundColor: null
        },
        title: {
            text: 'Andamento percentuale dei pagamenti rispetto al costo pubblico'
        },
        xAxis: {
            type: 'datetime',
            units: [
                ['year', null]
            ]
        },
        yAxis: {
            title: {
                text: '% pagamenti'
            },
            min: 0
        },
        series: data,
        credits: {
            href: 'http://www.dps.tesoro.it/',
            text: 'Fonte: DPS'
        },
        tooltip: {
            valueDecimals: 2,
            valueSuffix: '%',
            xDateFormat: '%Y'
        }
    });
}
