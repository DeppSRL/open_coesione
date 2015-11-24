var print_spline_chart = function(container, data, title) {
    for (var i = 0; i < data.length; i++) {
        for (var j = 0; j < data[i]['data'].length; j++) {
            data[i]['data'][j] = [Date.UTC(data[i]['data'][j]['year'], 0, 1), 100 * data[i]['data'][j]['paid_amount'] / data[i]['data'][j]['total_amount']];
        }
    }

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
//            text: 'Fonte: DPS',
//            href: 'http://www.dps.tesoro.it/',
            enabled: false
        }
    });
}

var print_column_chart = function(container, data, title) {
    var data_reg = [];
    var data_naz = [];
    var categories = [];
    var series_spesi = [];
    var series_da_spendere = [];
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
            'total_amount': 0,
            'paid_amount': 0
        });
        data = data.concat(data_naz);
    }

    for (i = 0; i < data.length; i++) {
        item = data[i];

        categories.push(item['program']);
        series_spesi.push(item['paid_amount']);
        series_da_spendere.push(item['total_amount'] - item['paid_amount']);
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
                formatter: function() {
                    var words = this.value.replace(/ FESR|FSE|CONV|CRO /g, ' ').split(/[\s]+/);
                    var numWordsPerLine = 2;
                    var str = [];

                    for (var i = 0; i < words.length; i++) {
                        if (i > 0 && i % numWordsPerLine == 0)
                            str.push('<br/>');

                        str.push(words[i]);
                    }

                    return str.join(' ').replace(/ <br\/> /g, '<br/>');
                },
                rotation: -45,
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
            labels: {
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
                data: series_da_spendere,
                stack: 0
            },
            {
                name: 'Spesi',
                data: series_spesi,
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
