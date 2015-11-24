$(function () {
    var charts = {};
    var chart_series = {};

    function trimtext(el) {
        return $(el).text().trim();
    }

    function readTextValues(list) {
        return $(list).map(function() { return trimtext(this) });
    }

    function readFloatValues(list) {
        return $(filterValues(list)).map(function() { var value = parseFloat(trimtext(this).replace(',', '.')); return isNaN(value) ? 0.0 : value });
    }

    function filterValues(list) {
        return $.grep(list, function(el, i) { return i >= 4  });
    }

    function buildChart(container, table) {
        var first_row = table.find('tbody tr:first-child td');
        var title = $(first_row[0]).text().trim();
        var fondo = $(first_row[2]).text().trim();
        var headers = readTextValues(table.find('thead th'));
        var date_list = filterValues(headers);

        return new Highcharts.Chart({
            chart: {
                renderTo: container[0],
                type: 'column',
                marginTop: 60,
                backgroundColor: null
            },
            title: {
                text: title + ' : ' + fondo
            },
            xAxis: {
                categories: date_list,
                labels: {
                    rotation: -45,
                    align: 'right'
                }
            },
            yAxis: {
                min: 0,
                max: 100,
                title: {
                    text: 'Valori %'
                }
            },
            legend: {
                layout: 'vertical',
                backgroundColor: '#FFFFFF',
                align: 'left',
                verticalAlign: 'top',
                x: 100,
                y: 70,
                floating: true,
                shadow: true
            },
            tooltip: {
                formatter: function() {
                    return this.series.name + ' ' + this.x + ': ' + this.y;
                }
            },
            plotOptions: {
                column: {
                    pointPadding: 0.2,
                    borderWidth: 0
                }
            },
            series: [],
            credits: {
                enabled: false
            }
        });
    }

    $(document).ready(function() {
        $('div.chart_container').each(function(ix, el) {
            var $el = $(el);
            var chart_name = $el.attr('id').replace(/^chart_/, '');
            var container = $el.find('.chart_canvas');
            var table = $el.find('table.chart_table');
            var selector = $el.find('select.chart_selector');

            charts[chart_name] = buildChart(container, table);

            chart_series[chart_name] = {};
            var programma_op, primo_programma_op;
            table.find('tbody tr, tfoot tr').each(function() {
                var row = $(this).find('td');
                var tipo = trimtext(row[3]);
                programma_op = trimtext(row[1]);
                if (!primo_programma_op) {
                    primo_programma_op = programma_op;
                }
                if (!(programma_op in chart_series[chart_name])) {
                    chart_series[chart_name][programma_op] = {}
                }
                chart_series[chart_name][programma_op][tipo] = readFloatValues(row);
            });

            $.each(chart_series[chart_name],function(key, v) {
                selector.append($('<option>', { value : key }).text(key));
            });

            selector.change(function() {
                var programma_op = $('option:selected', this).val();

                if (charts[chart_name].series.length == 2) {
                    charts[chart_name].series[0].setData(chart_series[chart_name][programma_op][charts[chart_name].series[0].name], false);
                    charts[chart_name].series[1].setData(chart_series[chart_name][programma_op][charts[chart_name].series[1].name]);
                } else {
                    $.each(chart_series[chart_name][programma_op], function(key, value) {
                        charts[chart_name].addSeries({
                            name: key,
                            data: value
                        })
                    });
                }
                charts[chart_name].setTitle({}, { text: programma_op });
            });

            selector.val(primo_programma_op).change();
        });
    });
});
