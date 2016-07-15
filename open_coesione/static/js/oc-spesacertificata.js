/*
 * OPCOGraph
 * Usage: var graphInstanceName = new OPCOGraph( containerID, url )
 *
 * NOTE on the CSV data source
 *
 * 1) Due to the bogus date model used in the "Mese" column of the CSV data source,
 * the human readable tooltip month label is calculated with a formula including "rowindex%12".
 * For appropriate results OPCOGraph requires the data series to start from January,
 * and no missing months for the following rows.
 *
 * 2) A comma decimal separator is used in the columns "% Spesa su dotazione", "Obiettivo nazionale"
 * and "Obiettivo comunitario", that's replaced with a dot at runtime
 *
 */

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
         * @param _data_pagamenti
         * @private
         */
        _data_pagamenti = null,

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
                    exportButtonTitle: 'Esporta',
                    printButtonTitle: 'Importa',
                    rangeSelectorFrom: 'Da',
                    rangeSelectorTo: 'A',
                    rangeSelectorZoom: 'Periodo',
                    downloadPNG: 'Download immagine PNG',
                    downloadJPEG: 'Download immagine JPEG',
                    downloadPDF: 'Download documento PDF',
                    downloadSVG: 'Download immagine SVG',
                    printChart: 'Stampa grafico',
                    thousandsSep: '.',
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
            $.ajax({
                type: 'GET',
                url: url,
                dataType: 'text',
                success: function(csvdata) {
                    var results = _parseCSVdata(csvdata);
                    if(results) _dataLoadSuccess(results);
                },
                error: function() { _dataLoadError(); }
            });
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
         _parseCSVdata = function (csvdata) {
            var lines = $.trim(csvdata).split(/\r\n|\n/);
            var headerLength = lines[0].split(';').length;
            var results = { data: [] };

            for (var i=0, l=lines.length; i<l; i++) {
                var data = lines[i].split(';');

                if (data.length == headerLength) {
                    results.data.push(data);
                } else {
                    console.log('error: CSV data in row '+i+' differs from header length');
                    return false;
                }
            }
            return results;
        },

        /**
         * Handle data loading success event
         *
         * @method _dataLoadSuccess
         * @private
         */
        _dataLoadSuccess = function (results) {
            var groupedCategories = [],
                yearGroup,
                currentYear,
                year,
                month,
                spesa,
                pagamenti,
                obiettivo_IT,
                obiettivo_EU;

            results.data.shift(); // get rid of the header

            _data_spesa = [];
            _data_pagamenti = [];
            _data_obiettivo_IT = [];
            _data_obiettivo_EU = [];

            $.each(results.data, function (idx, item) {

                // retrive current item period
                year = item[0];
                month = item[1];

                // skip dirty CSV rows
                if (!$.isNumeric(year)) return true;

                // retrive and filter current item values
                spesa = item[3].replace(/,/g, '.');
                pagamenti = 100 * item[7].replace(/,/g, '.') / item[8].replace(/,/g, '.');
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
                _data_pagamenti.push($.isNumeric(pagamenti) ? Number(pagamenti) : null);
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
                credits: {
                    enabled: false
                },
                title: {
                    text: null
                },
                chart: {
                    defaultSeriesType: 'line',
                    spacingLeft: 0,
                    spacingRight: 0
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
                                '<td style="text-align: right"><b>' + Highcharts.numberFormat(this.y, 0) + '%' + '</b></td></tr>';
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
                        text: null,
//                        text: 'Valori %',
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
                        name: 'Spesa certificata su dotazione',
                        //allowPointSelect: true,
                        color: '#C45355',
                        data: _data_spesa,
                        connectNulls: true,
                        marker: {
                            symbol: 'circle',
                            radius: 3,
                            lineWidth: 0
                        },
                        lineWidth: 2
                    },
                    {
                        name: 'Pagamenti su dotazione',
                        //allowPointSelect: true,
                        color: '#228822',
                        data: _data_pagamenti,
                        connectNulls: true,
                        marker: {
                            symbol: 'square',
                            radius: 3,
                            lineWidth: 0
                        },
                        lineWidth: 2
                    },
/*
                    {
                        name: 'Obiettivo nazionale di spesa certificata',
                        //allowPointSelect: true,
                        color: '#751ED8',
                        data: _data_obiettivo_IT,
                        marker: {
                            symbol: 'diamond',
                            radius: 3,
                            lineWidth: 2,
                            fillColor: '#FFFFFF',
                            lineColor: null
                        },
                        lineWidth: 0
                    },
*/
                    {
                        name: 'Obiettivo comunitario di spesa certificata',
                        //allowPointSelect: true,
                        color: '#003399',
                        data: _data_obiettivo_EU,
                        marker: {
                            symbol: 'triangle',
                            radius: 3,
                            lineWidth: 0
                        },
                        lineWidth: 0
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