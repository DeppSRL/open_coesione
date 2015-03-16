var print_spline_chart = function(container, data, title) {
    new Highcharts.Chart({
        chart: {
            renderTo: container,
            type: 'spline',
            backgroundColor: null
        },
        title: {
            text: title
        },
        xAxis: {
            type: 'datetime',
            units: [
                ['year', null]
            ]
        },
        yAxis: {
            min: 0,
            title: {
                text: '% pagamenti'
            }
        },
        series: data,
        tooltip: {
            valueDecimals: 2,
            valueSuffix: '%',
            xDateFormat: '%Y'
        },
        credits: {
            href: 'http://www.dps.tesoro.it/',
            text: 'Fonte: DPS'
        }
    });
}

var print_column_chart = function(container, data, title) {
    var data_reg = [];
    var data_naz = [];
    var categories = [];
    var serie_spesi = [];
    var serie_da_spendere = [];
    var item, i;

    var num_format = function(num) {
        return number_format(num / 1000000, 0, ',', '.')
    };

    for (i = 0; i < data.length; i++) {
        item = data[i];

        if (item['program'].search('POR ') > -1) {
            data_reg.push(item);
        } else {
            data_naz.push(item);
        }
    }
    data = data_reg;
    if (data_naz.length) {
        data.push({
            'program': '',
            'total': 0,
            'amount': 0
        });
        data = data.concat(data_naz);
    }

    for (i = 0; i < data.length; i++) {
        item = data[i];

        categories.push(item['program']);
        serie_spesi.push(item['amount']);
        serie_da_spendere.push(item['total'] - item['amount']);
    }

    return new Highcharts.Chart({
        chart: {
            renderTo: container,
            type : 'column',
            backgroundColor: null
        },
        title: {
            text: title
        },
        xAxis: {
            categories: categories,
            labels: {
                rotation: -90,
                align: 'right',
                style: {
                    font: 'normal 13px Verdana, sans-serif'
                }
            }
        },
        yAxis: {
            min: 0,
            title: {
                text: 'Milioni di €'
            },
            labels:{
                formatter: function() {
                    return num_format(this.value)
                }
            }
        },
        plotOptions: {
            column: {
                borderWidth: 0,
                stacking: 'normal'
            }
        },
        series: [
            {
                name: 'Da spendere',
                data: serie_da_spendere,
                stack: 0
            },
            {
                name: 'Spesi',
                data: serie_spesi,
                stack: 0
            }
        ],
        tooltip: {
            formatter: function() {
                if (this.x)
                    return '<b>' + this.x + '</b><br/>' + this.series.name + ': ' + num_format(this.y) + ' milioni di €<br/>' + 'Costo pubblico: ' + num_format(this.point.stackTotal) + ' milioni di €';
                else
                    return false;
            }
        },
        credits: {
            href: 'http://www.dps.tesoro.it/',
            text: 'Fonte: DPS'
        },
        colors: ['#b5b299', '#707005']
    });
}
