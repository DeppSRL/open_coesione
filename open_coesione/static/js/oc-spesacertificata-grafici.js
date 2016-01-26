$(function () {
    function trimtext(elem) {
        return $.trim($(elem).text());
    }

    function buildChart(container, title, categories) {
        return new Highcharts.Chart({
            chart: {
                renderTo: container,
                type: 'column',
                marginTop: 60,
                backgroundColor: null
            },
            title: {
                text: title
            },
            xAxis: {
                categories: categories,
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
                    return this.series.name + ' ' + this.x + ': ' + Highcharts.numberFormat(this.y, 0);
                }
            },
            plotOptions: {
                column: {
                    pointPadding: 0.2,
                    borderWidth: 0
                }
            },
            series: [],
            colors: ['#751ED8', '#C45355', '#228822'],
            credits: {
                enabled: false
            }
        });
    }

    $(document).ready(function() {
        $('div.chart_container').each(function() {
            var self = $(this);

            var container = self.find('div.chart_canvas')[0];
            var table = self.find('table.chart_table');
            var selector = self.find('select.chart_selector');

            var title = trimtext(table.find('caption'));
            var dates = table.find('thead th').slice(2).map(function() { return trimtext(this) });

            var chart = buildChart(container, title, dates);

            var chart_series = {};

            table.find('tbody tr').each(function() {
                var row = $(this).find('td');
                var program = trimtext(row[0]);
                var data_type = trimtext(row[1]);

                if (!(program in chart_series)) {
                    chart_series[program] = {}
                }
                chart_series[program][data_type] = row.slice(2).map(function() { var value = parseFloat(trimtext(this).replace(',', '.')); return isNaN(value) ? 0.0 : value });
            });

            $.each(chart_series, function(key, val) {
                selector.append($('<option>', { value : key }).text(key));
            });

            selector.on('change', function() {
                var program = $(this).find('option:selected').val();

                if (chart.series.length) {
                    $.each(chart.series, function(key, value) {
                        chart.series[key].setData(chart_series[program][chart.series[key].name], false);
                    });
                    chart.redraw();
                } else {
                    $.each(chart_series[program], function(key, value) {
                        chart.addSeries({
                            name: key,
                            data: value
                        })
                    });
                }
                chart.setTitle({}, { text: program });
            }).trigger('change');
        });
    });
});
