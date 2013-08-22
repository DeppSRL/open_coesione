# -*- coding: utf-8 -*-
import codecs
import os
from django.core.management.base import BaseCommand

from open_coesione import utils
from optparse import make_option
import csv
import logging
from datetime import datetime

class Command(BaseCommand):
    """
    Import CSV data from the Spesa Certificata source (previously exported from XLS into CSV format)

    Transform the data into 4 different CSV files, that will feed the spesa-certificata page.

    Data will always be re-written, so, be sure to backup old csv files, if you need them.
    """
    help = "Transform spesa-certificata csv file"

    option_list = BaseCommand.option_list + (
        make_option('--csv-file',
                    dest='csvfile',
                    default='./2_Target_Risultati_20130531.csv',
                    help='Select csv input file, with abs or rel path'),
        make_option('--dest-path',
                    dest='destpath',
                    default='.',
                    help='Destination path, where the 4 csv files will be written. Defaults to current path.'),
        make_option('--encoding',
                    dest='encoding',
                    default='utf-8',
                    help='Set character encoding of input and output csv file. Defaults to utf-8.')
    )

    logger = logging.getLogger('console')
    unicode_reader = None
    unicode_writer = None

    # dates when the results are checked
    # add dates here to increase points in graphs
    dates = ['20101231', '20111031', '20111231',
             '20120531', '20121031', '20121231',
             '20130531', '20131031', '20131231',
             '20141231',
             '20151231']

    # main data structure:
    #  contains data read from the input csv file,
    #  is read to produce the 4 csv's
    data = {
        'convergenza_fse': {
            'programmi': [
                { 'descr': 'POR CONV FSE CAMPANIA', 'label': 'Por Campania'},
                { 'descr': 'POR CONV FSE CALABRIA', 'label': 'Por Calabria' },
                { 'descr': 'POR CONV FSE SICILIA', 'label': 'Por Sicilia' },
                { 'descr': 'POR CONV FSE BASILICATA', 'label': 'Por Basilicata' },
                { 'descr': 'POR CONV FSE PUGLIA', 'label': 'Por Puglia' },
                { 'descr': 'PON CONV FSE GOVERNANCE E AZIONI DI SISTEMA', 'label': 'Pon GAS' },
                { 'descr': 'PON CONV FSE COMPETENZE PER LO SVILUPPO', 'label': 'Pon Istruzione' },
            ]
        },
        'convergenza_fesr': {
            'programmi': [
                { 'descr': 'POIN CONV FESR ATTRATTORI CULTURALI, NATURALI E TURISMO', 'label': 'Poin Attrattori' },
                { 'descr': 'POIN CONV FESR ENERGIE RINNOVABILI E RISPARMIO ENERGETICO', 'label': 'Poin Energie' },
                { 'descr': 'PON CONV FESR GOVERNANCE E ASSISTENZA TECNICA', 'label': 'Pon GAT' },
                { 'descr': "PON CONV FESR ISTRUZIONE - AMBIENTI PER L'APPRENDIMENTO", 'label': 'Pon Istruzione' },
                { 'descr': u'PON CONV FESR RETI E MOBILITÀ', 'label': 'Pon Reti' },
                { 'descr': u'PON CONV FESR RICERCA E COMPETITIVITÀ', 'label': 'Pon Ricerca' },
                { 'descr': 'PON CONV FESR SICUREZZA', 'label': 'Pon Sicurezza' },
                { 'descr': 'POR CONV FESR CALABRIA', 'label': 'Por Calabria' },
                { 'descr': 'POR CONV FESR CAMPANIA', 'label': 'Por Campania' },
                { 'descr': 'POR CONV FESR PUGLIA', 'label': 'Por Puglia' },
                { 'descr': 'POR CONV FESR SICILIA', 'label': 'Por Sicilia' },
                { 'descr': 'POR CONV FESR BASILICATA', 'label': 'Por Basilicata' },
            ]
        },
        'competitivita_fse': {
            'programmi': [
                { 'descr': 'POR CRO FSE ABRUZZO', 'label': 'Por Abruzzo' },
                { 'descr': 'POR CRO FSE EMILIA ROMAGNA', 'label': 'Por Emilia Romagna' },
                { 'descr': 'POR CRO FSE FRIULI VENEZIA GIULIA', 'label': 'Por Friuli enezia Giulia' },
                { 'descr': 'POR CRO FSE LAZIO', 'label': 'Por Lazio' },
                { 'descr': 'POR CRO FSE LIGURIA', 'label': 'Por Liguria' },
                { 'descr': 'POR CRO FSE LOMBARDIA', 'label': 'Por Lombardia' },
                { 'descr': 'POR CRO FSE MARCHE', 'label': 'Por Marche' },
                { 'descr': 'POR CRO FSE MOLISE', 'label': 'Por Molise' },
                { 'descr': 'POR CRO FSE PA BOLZANO', 'label': 'Por PA Bolzano' },
                { 'descr': 'POR CRO FSE PA TRENTO', 'label': 'Por PA Trento' },
                { 'descr': 'POR CRO FSE PIEMONTE', 'label': 'Por Piemonte' },
                { 'descr': 'POR CRO FSE TOSCANA', 'label': 'Por Toscana' },
                { 'descr': 'POR CRO FSE UMBRIA', 'label': 'Por Umbria' },
                { 'descr': "POR CRO FSE VALLE D'AOSTA", 'label': 'Por VdA' },
                { 'descr': 'POR CRO FSE VENETO', 'label': 'Por Veneto' },
                { 'descr': 'POR CRO FSE SARDEGNA', 'label': 'Por Sardegna' },
                { 'descr': 'PON CRO FSE AZIONI DI SISTEMA', 'label': 'Pon AS' },
            ]
        },
        'competitivita_fesr': {
            'programmi': [
                { 'descr': 'POR CRO FESR ABRUZZO', 'label': 'Por Abruzzo' },
                { 'descr': 'POR CRO FESR EMILIA ROMAGNA', 'label': 'Por Emilia Romagna' },
                { 'descr': 'POR CRO FESR FRIULI VENEZIA GIULIA', 'label': 'Por Friuli Venezia Giulia' },
                { 'descr': 'POR CRO FESR LAZIO', 'label': 'Por Lazio' },
                { 'descr': 'POR CRO FESR LIGURIA', 'label': 'Por Liguria' },
                { 'descr': 'POR CRO FESR LOMBARDIA', 'label': 'Por Lombardia' },
                { 'descr': 'POR CRO FESR MARCHE', 'label': 'Por Marche' },
                { 'descr': 'POR CRO FESR MOLISE', 'label': 'Por Molise' },
                { 'descr': 'POR CRO FESR PA BOLZANO', 'label': 'Por PA Bolzano' },
                { 'descr': 'POR CRO FESR PA TRENTO', 'label': 'Por PA Trento' },
                { 'descr': 'POR CRO FESR PIEMONTE', 'label': 'Por Piemonte' },
                { 'descr': 'POR CRO FESR TOSCANA', 'label': 'Por Toscana' },
                { 'descr': 'POR CRO FESR UMBRIA', 'label': 'Por Umbria' },
                { 'descr': "POR CRO FESR VALLE D'AOSTA", 'label': 'Por VdA' },
                { 'descr': 'POR CRO FESR VENETO', 'label': 'Por Veneto' },
                { 'descr': 'POR CRO FESR SARDEGNA', 'label': 'Por Sardegna' },
            ]
        },

    }

    def handle(self, *args, **options):
        self.csv_file = options['csvfile']
        self.encoding = options['encoding']

        # read first csv file
        try:
            self.unicode_reader = utils.UnicodeDictReader(
                open(self.csv_file, 'r'), delimiter=',', encoding=self.encoding
            )
        except IOError:
            self.logger.error("It was impossible to open file %s" % self.csv_file)
            exit(1)
        except csv.Error, e:
            self.logger.error("CSV error while reading %s: %s" % (self.csv_file, e.message))

        self.encoding = options['encoding']

        verbosity = options['verbosity']
        if verbosity == '0':
            self.logger.setLevel(logging.ERROR)
        elif verbosity == '1':
            self.logger.setLevel(logging.WARNING)
        elif verbosity == '2':
            self.logger.setLevel(logging.INFO)
        elif verbosity == '3':
            self.logger.setLevel(logging.DEBUG)


        ##
        ## reading phase
        ##
        self.logger.info("### READING ###")
        c = 0
        for row in self.unicode_reader:
            # select a set of rows
            # with offset
            c += 1

            descr = u" ".join([i for i in row['DPS_DESCRIZIONE_PROGRAMMA'].split(" ") if i])

            if descr != 'TOTALE':
                self.logger.debug(u"  {0} - {1}".format(c, descr))

                obiettivo = row['QSN_AREA_OBIETTIVO_UE'].strip()
                fondo = row['QSN_FONDO_COMUNITARIO '].strip()

                if obiettivo == 'CONV':
                    obiettivo = 'Convergenza'
                    ob = 'convergenza'
                elif obiettivo == 'CRO':
                    obiettivo = u'Competitività'
                    ob = "competitivita"
                else:
                    raise Exception("Wrong obiettivo: {0}".format(obiettivo))

                key = "{0}_{1}".format(ob, fondo.lower())

                data_item = self.data[key]
                data_item['obiettivo'] = obiettivo
                data_item['fondo'] = fondo

                for p in data_item['programmi']:
                    if p['descr'] == descr:
                        p['dati'] = self._fetch_data_from_row(row)
                        break


        ##
        ## writing phase
        ##

        self.logger.info("### WRITING ###")

        # uncomment to debug
        import pprint
        # pprint.pprint(self.data)

        dest_path = options['destpath']
        csv_header = [
            "Obiettivo", "Programma operativo", "Fondo", "Tipo dato"
        ]
        for d in self.dates:
            csv_header.append(datetime.strptime(d, '%Y%m%d').strftime('%d/%m/%Y'))

        for f, data_item in self.data.iteritems():
            csv_out_file = "{0}.csv".format(os.path.join(dest_path, f))
            self.logger.info("  {0}".format(csv_out_file))

            csv_out_file_handler = open(csv_out_file, 'w')
            csv_writer = utils.UnicodeWriter(csv_out_file_handler, encoding="utf-8")
            csv_writer.writerow(csv_header)

            for p in data_item['programmi']:
                csv_target_row = [
                    data_item['obiettivo'], p['label'], data_item['fondo'], 'Target'
                ]
                csv_result_row = [
                    data_item['obiettivo'], p['label'], data_item['fondo'], 'Risultato'
                ]
                for d in p['dati']:
                    csv_target_row.append(d['target'])
                    if 'result' in d:
                        csv_result_row.append(d['result'])
                    else:
                        csv_result_row.append('')
                csv_writer.writerow(csv_target_row)
                csv_writer.writerow(csv_result_row)








    def _fetch_data_from_row(self, row):
        """
        Read from CSV row and return a structured array

        """
        data = []
        for d in self.dates:
            datum = {
                'date': datetime.strptime(d, '%Y%m%d').strftime('%d/%m/%Y')
            }

            target_key = 'TARGET {0}'.format(d)
            target_estimate_key = 'STIMA TARGET {0}'.format(d)
            if target_key in row:
                datum['target'] = row[target_key].strip()
            elif target_estimate_key in row:
                datum['target'] = row[target_estimate_key].strip()

            result_key = 'RISULTATO {0}'.format(d)
            if result_key in row:
                datum['result'] = row[result_key].strip()

            data.append(datum)

        return data