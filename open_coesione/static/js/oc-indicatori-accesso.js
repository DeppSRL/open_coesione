var AccessIndicatorsGraph;

(function ($) {
    AccessIndicatorsGraph = function(chartContainerID, lang) {
        var _chart_instance = null;

        var _printChart = function (chartContainerID, values, lang) {
            Highcharts.setOptions({
                lang: {
                    numericSymbols: null,
                    decimalPoint: lang == 'it' ? ',' : '.',
                    thousandsSep: lang == 'it' ? '.' : ','
                }
            });

            _chart_instance && _chart_instance.destroy();

//            var xaxis_max = 20;

            var data = values.map(function (x) { return x['value'] });
            var categories = values.map(function (x) { return x['date'] });

            var decimals = 0;
            for (var i = 0; i < data.length && decimals == 0; i++) {
                if (data[i] % 1) {
                    decimals = 2;
                }
            }

            _chart_instance = new Highcharts.Chart({
                chart: {
                    renderTo: chartContainerID,
                    type: 'spline',
                    backgroundColor: null
                },
                title: {
                    text: ''
                },
                xAxis: {
//                    min: 0, max: Math.min(values.length - 1, xaxis_max),
                    categories: categories
               },
                yAxis: {
                    min: 0, max: Math.max.apply(null, data),
                    title: {
                        text: ''
                    }
                },
                series: [{
                    data: data
                }],
                credits: {
                    enabled: false
                },
                legend: {
                    enabled: false
                },
//                scrollbar: {
//                    enabled: (values.length - 1 > xaxis_max)
//                },
                tooltip: {
                    formatter: function() {
                        return this.x + ': ' + Highcharts.numberFormat(this.y, decimals);
                    }
                }
            });
        };

        var _initCharts = function (chartContainerID, lang) {
            var chartContainer = $('#' + chartContainerID);
            var elems = chartContainer.closest('.charts_accordion').find('.collapse');

            elems.on('show', function () {
                elems.filter('.in').collapse('hide');

                var self = $(this);

                self.css('height', 'auto');

                chartContainer.empty().appendTo(self.children().first());
            }).on('shown', function () {
                _printChart(chartContainerID, $(this).data('values'), lang);
            }).first().collapse('show');
        };

        _initCharts(chartContainerID, lang);
    };
})(jQuery);
