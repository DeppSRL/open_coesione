var OPCOGraph;

(function ($) {

    /**
     * The main OPCOGraph interface class.
     *
     * @class OPCOGraph
     * @static
     */
    OPCOGraph = function(containerID, url) {

        /**
         * @param _data_spesa
         * @private
         */
        var _data_spesa = null,

        /**
         * @param _data_obiettivo_IT
         * @private
         */
        _data_obiettivo_IT = null,

        /**
         * @param _data_obiettivo_EU
         * @private
         */
        _data_obiettivo_EU = null,

        /**
         * @param _chart_instance
         * @private
         */
        _chart_instance = null,

        /**
         * @param _element
         * @private
         */
        _element = null,

        /**
         * @param _monthsNames
         * @private
         */
        _monthsNames = ['Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno', 'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre'],

        /**
         * Italian Localization for Highcharts
         * @method _initChartLang
         * @private
         */
        _initChartLang = function () {
            Highcharts.setOptions({
                lang: {
                    loading: 'Sto caricando...',
                    months: ['Gennaio', 'Febbraio', 'Marzo', 'Aprile', 'Maggio', 'Giugno', 'Luglio', 'Agosto', 'Settembre', 'Ottobre', 'Novembre', 'Dicembre'],
                    weekdays: ['Domenica', 'Lunedì', 'Martedì', 'Mercoledì', 'Venerdì', 'Sabato', 'Domenica'],
                    shortMonths: ['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu', 'Lug', 'Ago', 'Set', 'Ott', 'Nov', 'Dic'],
                    exportButtonTitle: "Esporta",
                    printButtonTitle: "Importa",
                    rangeSelectorFrom: "Da",
                    rangeSelectorTo: "A",
                    rangeSelectorZoom: "Periodo",
                    downloadPNG: 'Download immagine PNG',
                    downloadJPEG: 'Download immagine JPEG',
                    downloadPDF: 'Download documento PDF',
                    downloadSVG: 'Download immagine SVG',
                    printChart: 'Stampa grafico',
                    thousandsSep: ".",
                    decimalPoint: ','
                }
            });
        },

        /**
         * Begin fetching the data
         *
         * @method _initDataLoad
         * @private
         */
        _initDataLoad = function (url) {
            Papa.parse(url, {
                download: true,
                header: false,
                error: _dataLoadError,
                complete: _dataLoadSuccess
            })
        },

        /**
         * Handle data loading error event
         *
         * @method _dataLoadError
         * @private
         */
        _dataLoadError = function () {
            console.log('data load error');
        },

        /**
         * Handle data loading success event
         *
         * @method _dataLoadSuccess
         * @private
         */
        _dataLoadSuccess = function (results, file) {
            var groupedCategories = [],
                yearGroup,
                currentYear,
                year,
                month,
                spesa,
                obiettivo_IT,
                obiettivo_EU;

            results.data.shift(); // get rid of the header

            _data_spesa = [];
            _data_obiettivo_IT = [];
            _data_obiettivo_EU = [];

            $.each(results.data, function (idx, item) {

                // retrive current item period
                year = item[0];
                month = item[1];

                // skip dirty CSV rows
                if (!$.isNumeric(year)) return true;

                // retrive and filter current item values
                spesa = item[4].replace(/,/g, '.');
                obiettivo_IT = item[5].replace(/,/g, '.');
                obiettivo_EU = item[6].replace(/,/g, '.');

                // create a new yearGroup if the current year has not been processed yet
                if (yearGroup != year) {
                    currentYear = {name: year, categories: []};
                    groupedCategories.push(currentYear);
                    yearGroup = year;
                }
                // insert the current month in currentYear
                currentYear.categories.push(month);

                // Data values are not available for every X axis interval
                // a null value is pushed for any missing value
                _data_spesa.push($.isNumeric(spesa) ? Number(spesa) : null);
                _data_obiettivo_IT.push($.isNumeric(obiettivo_IT) ? Number(obiettivo_IT) : null);
                _data_obiettivo_EU.push($.isNumeric(obiettivo_EU) ? Number(obiettivo_EU) : null);

            });

            /*
             * Prepare additional vertical separators
             * as a visual guide to distinguish years
             */
            var plotLinesXpos = -0.5;
            var plotLinesX = [];
            for (var i = 0; i <= groupedCategories.length; i++) {
                plotLinesX.push({color: '#cccccc', value: plotLinesXpos, width: 1});
                plotLinesXpos += 12;
            }

            /*
             * Draw
             */
            _chart_instance = _element.highcharts({

                title: {
                    text: null
                },
                chart: {
                  defaultSeriesType: 'line'
                },
                tooltip: {
                    shared: true,
                    useHTML: true,
                    formatter: function () {

                        // TRICK TO CALCULATE THE MONTH NAME, DUE TO "SOAPY" DATA SOURCE
                        // IMPLIES THAT THE CSV SERIES STARTS FROM JANUARY
                        // AND THERE'S NO MISSING MONTH IN AN YEAR
                        var month = _monthsNames[this.points[0].point.x % 12];


                        var year = this.x.parent.name;
                        var s = '<b>' + month + ' ' + year + '</b>';
                        s += '<table>';
                        $.each(this.points, function () {
                            s += '<tr><td style="color:' + this.color + '">\u25CF ' + this.series.name + ': </td>' +
                                '<td style="text-align: right"><b>' + this.y + '%' + '</b></td></tr>';
                        });
                        s += '</table>';

                        return s;
                    }
                },

                legend: {
                    align: 'left',
                    verticalAlign: 'top',
                    layout: 'vertical',
                    itemMarginTop: 5,
                    itemMarginBottom: 5,
                    y: 80,
                    x: 100,
                    floating: true,
                    enabled: true,
                    borderWidth: 0,
                    backgroundColor: '#FFFFFF'
                },

                yAxis: {
                    floor: 0,
                    ceiling: 100,
                    tickInterval: 10,
                    title: {
                        text: 'Valori %',
                        margin: 0
                    }
                },

                xAxis: {
                    plotLines: plotLinesX,
                    labels: {
                        rotation: 0,
                        style: {
                            fontSize: '8px'
                        }
                    },
                    categories: groupedCategories
                },

                series: [
                    {
                        name: 'Spesa su dotazione',
                        //allowPointSelect: true,
                        color: '#C45355',
                        data: _data_spesa,
                        marker: {
                            enabled: null, // auto
                            radius: 3,
                            lineWidth: 0
                        },
                        lineWidth: 3,
                        tooltip: {
                            valueDecimals: 2
                        }
                    },
                    {
                        name: 'Obiettivo nazionale',
                        //allowPointSelect: true,
                        color: '#751ED8',
                        data: _data_obiettivo_IT,
                        marker: {
                            enabled: null, // auto
                            radius: 3

                        },
                        lineWidth: 0,
                        tooltip: {
                            valueDecimals: 2
                        }
                    },
                    {
                        name: 'Obiettivo comunitario',
                        //allowPointSelect: true,
                        color: '#003399',
                        data: _data_obiettivo_EU,
                        marker: {
                            enabled: null, // auto
                            radius: 3
                        },
                        lineWidth: 0,
                        tooltip: {
                            valueDecimals: 2
                        }
                    }
                ]
            });

        };

        /**
         * init
         *
         */

         //_initChartLang();
         _element = $(containerID);
         _initDataLoad(url);

    };


})(jQuery);
