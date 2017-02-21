var IndicatorsGraph;

(function ($) {
    IndicatorsGraph = function(containerID, minLocations, maxLocations) {
        var _locations = null,
            _topics = null,
            _indicators = null,
            _locationIDs = null,
            _indicatorID = null,
            _chart_instance = null,
            _series = {};

        var _getLocationID = function (name) {
            for (var key in _locations) {
                if (_locations.hasOwnProperty(key)) {
                    if (_locations[key]['name'] == name) {
                        return key;
                    }
                }
            }
            return -1;
        };

        var _filterSeries = function (series, locationIDs) {
            return $.grep(series, function (elem) {
                return $.inArray(elem['locationID'], locationIDs) > -1;
            });
        };

        var _initChart = function (indicatorID) {
            _indicatorID = indicatorID;

            if (_indicatorID in _series) {
                _printChart();
            } else {
                $.getJSON('/charts/indicatori-regionali/' + _indicatorID + '/', function (data) {
                    _series[_indicatorID] = [];

                    $.each(data, function (locationID, locationValues) {
                        _series[_indicatorID].push({
                            name: _locations[locationID]['name'],
                            data: locationValues.map(function (x) { return [Date.UTC(x['year'], 0, 1), x['value']] }),
                            locationID: locationID
                        });
                    });

                    _printChart();
                });
            }
        };

        var _printChart = function () {
            _chart_instance && _chart_instance.destroy();

            _chart_instance = new Highcharts.Chart({
                chart: {
                    renderTo: 'topic_chart',
                    type: 'spline',
                    backgroundColor: null
                },
                title: {
                    text: _indicators[_indicatorID]['title']
                },
                subtitle: {
                    text: _indicators[_indicatorID]['subtitle']
                },
                series: _filterSeries(_series[_indicatorID], _locationIDs),
                xAxis: {
                    showLastLabel: true,
                    type: 'datetime',
                    units: [
                        ['year', null]
                    ]
                },
                yAxis: {
                    title: {
                        align: 'high',
                        offset: 0,
                        text: '',
                        rotation: 0
                    }
                },
                tooltip: {
                    valueDecimals: 2,
                    valueSuffix: '',
                    xDateFormat: '%Y'
                },
                credits: {
                    text: 'Fonte: ISTAT',
                    href:'/opendata'
                }
            });
        };

        var _initChartBlock = function (topicID, indicatorID, locationID) {
            _indicators = _topics[topicID]['indicators'];

            _locationIDs = [];
            _locationIDs.push(_getLocationID('Italia'));
            if (locationID) {
                _locationIDs.push(locationID);
            }

            var indicator_selector = $('#indicator-selector');
            if (indicator_selector.length) {
                indicator_selector.children().remove();
                $.each(_indicators, function (idx, indicator) {
                    indicator_selector[0].options.add(new Option(indicator['title'], idx));
                });
            }

            var location_selector = $('#location-selector');
            if (location_selector.length) {
                location_selector.children(':not(:first)').remove();
                $.each(_locations, function (idx, location) {
                    if ($.inArray(idx, _locationIDs) == -1) {
                        location_selector[0].options.add(new Option(location['name'], idx));
                    }
                });
            }

            _initChart(indicatorID || indicator_selector.val());
        };

        var _initCharts = function (containerID, minLocations, maxLocations) {
            var chartContainer = $('#topic_chart');
            var selectors = chartContainer.next('form');
            var elems = $(containerID).find('.collapse');

            elems.on('show', function () {
                elems.filter('.in').collapse('hide');

                var self = $(this);

                self.css('height', 'auto');

                chartContainer.empty().appendTo(self.children().first()).after(selectors);
            }).on('shown', function () {
                var self = $(this);

                _initChartBlock(self.attr('data-topic'), self.attr('data-indicator'), self.attr('data-location'));
            });

            // the location select handler
            $('#location-selector').on('change', function () {
                while (_chart_instance.series.length >= maxLocations) {
                    _chart_instance.series.pop().remove();
                }

                var locationID = $(this).val();

                if (locationID) {
                    var serie = $.grep(_chart_instance.series, function (elem) { return locationID == _getLocationID(elem.name); });
                    if (serie.length) {
                        serie[0].setVisible();
                    } else {
                        _chart_instance.addSeries(_filterSeries(_series[_indicatorID], [locationID])[0]);
                    }
                }
            });

            // the location reset handler
            $('#location-reset').on('click', function (e) {
                while (_chart_instance.series.length > minLocations) {
                    _chart_instance.series.pop().remove();
                }

                $('#location-selector').val('');

                e.preventDefault();
            });

            // the indicator select handler
            $('#indicator-selector').on('change', function () {
                var indicatorID = $(this).val();

                if (indicatorID) {
                    $('#location-selector').val('');
                    _initChart(indicatorID);
                }
            });

            $.getJSON('/charts/indicatori/', function (data) {
                _locations = data['locations'];
                _topics = data['topics'];

                $(containerID).find('.accordion-toggle').first().trigger('click');
            });
        };

        _initCharts(containerID, minLocations, maxLocations);
    };
})(jQuery);
