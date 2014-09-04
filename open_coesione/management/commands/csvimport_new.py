# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import DatabaseError
from django.core.management.base import BaseCommand

from optparse import make_option

import re
import pandas as pd
import datetime

from progetti.models import *

def convert_cup_cod_natura(cup_cod_natura):
    if cup_cod_natura.strip() == '':
        cup_cod_natura = ' '
    elif cup_cod_natura == '02':
        cup_cod_natura = '01'
    return cup_cod_natura

class Command(BaseCommand):
    """
    Data are imported from their CSV sources.
    """
    help = 'Import data from csv'

    import_types = ['proj', 'projinactive']

    option_list = BaseCommand.option_list + (
        make_option('--csv-file',
                    dest = 'csvfile',
                    default = None,
                    help = 'Select csv file.'),
        make_option('--type',
                    dest = 'type',
                    default = None,
                    help = 'Type of import; select among %s.' % ', '.join(['"' + t + '"' for t in import_types])),
        make_option('--delete',
                    dest = 'delete',
                    action = 'store_true',
                    help = 'Delete records before importing new.'),
        make_option('--encoding',
                    dest = 'encoding',
                    default = 'utf-8',
                    help = 'Set character encoding of input file.'),
    )

    logger = logging.getLogger('csvimport')

    def handle(self, *args, **options):
        csv_file = options['csvfile']

        # read first csv file
        try:
            df = pd.read_csv(
                csv_file,
                sep = ';',
                header = 0,
                low_memory = False,
                dtype = object,
                encoding = options['encoding'],
                keep_default_na = False,
                converters = {
                    'CUP_COD_NATURA': convert_cup_cod_natura,
                }
            )
        except IOError:
            self.logger.error('It was impossible to open file %s' % csv_file)
            exit(1)

        verbosity = options['verbosity']
        if verbosity == '0':
            self.logger.setLevel(logging.ERROR)
        elif verbosity == '1':
            self.logger.setLevel(logging.WARNING)
        elif verbosity == '2':
            self.logger.setLevel(logging.INFO)
        elif verbosity == '3':
            self.logger.setLevel(logging.DEBUG)

        type = options['type']
        if type in self.import_types:
            self.logger.info('Inizio import da %s' % csv_file)

            if type == 'proj':
                self._handle_progettiattivi(df, options['delete'])
            elif type == 'projinactive':
                self._handle_progettiinattivi(df, options['delete'])

            self.logger.info('Fine')
        else:
            self.logger.error('Wrong type "%s". Select among %s.' % (type, ', '.join(['"' + t + '"' for t in self.import_types])))
            exit(1)


    def _handle_progettiattivi(self, df, delete):
        self._handle_progetti(df = df, delete = delete, active_flag = True)


    def _handle_progettiinattivi(self, df, delete):
        self._handle_progetti(df = df, delete = delete, active_flag = False)


    def _handle_progetti_programmaasseobiettivo(self, df):
        keywords = [
            'DPS_CODICE_PROGRAMMA', 'PO_CODICE_ASSE', 'PO_COD_OBIETTIVO_OPERATIVO',
            'DPS_DESCRIZIONE_PROGRAMMA', 'PO_DENOMINAZIONE_ASSE', 'PO_OBIETTIVO_OPERATIVO'
        ]

        # only complete and non-empty classifications are created or updated
        if all(k in df.columns.values for k in keywords):
            cols = ['DPS_CODICE_PROGRAMMA', 'DPS_DESCRIZIONE_PROGRAMMA']
            df1 = df[cols].drop_duplicates()
            for index, row in df1.iterrows():
                if all(row[k].strip() for k in cols):
                    programma, created = ProgrammaAsseObiettivo.objects.get_or_create(
                        codice = row['DPS_CODICE_PROGRAMMA'],
                        defaults = {
                            'descrizione': row['DPS_DESCRIZIONE_PROGRAMMA'],
                            'tipo_classificazione': ProgrammaAsseObiettivo.TIPO.programma,
                        }
                    )
                    self._log(created, 'Creato programma (asse-obiettivo): %s' % programma)

            cols = ['DPS_CODICE_PROGRAMMA', 'PO_CODICE_ASSE', 'PO_DENOMINAZIONE_ASSE']
            df1 = df[cols].drop_duplicates()
            for index, row in df1.iterrows():
                if all(row[k].strip() for k in cols):
                    programma, created = ProgrammaAsseObiettivo.objects.get_or_create(
                        codice = '%s/%s' % (row['DPS_CODICE_PROGRAMMA'], row['PO_CODICE_ASSE']),
                        defaults = {
                            'descrizione': row['PO_DENOMINAZIONE_ASSE'],
                            'tipo_classificazione': ProgrammaAsseObiettivo.TIPO.asse,
                            'classificazione_superiore_id': row['DPS_CODICE_PROGRAMMA'],
                        }
                    )
                    self._log(created, 'Creato asse: %s' % programma)

            cols = ['DPS_CODICE_PROGRAMMA', 'PO_CODICE_ASSE', 'PO_COD_OBIETTIVO_OPERATIVO', 'PO_OBIETTIVO_OPERATIVO']
            df1 = df[cols].drop_duplicates()
            for index, row in df1.iterrows():
                if all(row[k].strip() for k in cols):
                    programma, created = ProgrammaAsseObiettivo.objects.get_or_create(
                        codice = '%s/%s/%s' % (row['DPS_CODICE_PROGRAMMA'], row['PO_CODICE_ASSE'], row['PO_COD_OBIETTIVO_OPERATIVO']),
                        defaults = {
                            'descrizione': row['PO_OBIETTIVO_OPERATIVO'],
                            'tipo_classificazione': ProgrammaAsseObiettivo.TIPO.obiettivo,
                            'classificazione_superiore_id': '%s/%s' % (row['DPS_CODICE_PROGRAMMA'], row['PO_CODICE_ASSE']),
                        }
                    )
                    self._log(created, 'Creato obiettivo: %s' % programma)


    def _handle_progetti_programmalineaazione(self, df):
        keywords = [
            'DPS_CODICE_PROGRAMMA', 'COD_LINEA', 'COD_AZIONE',
            'DPS_DESCRIZIONE_PROGRAMMA', 'DESCR_LINEA', 'DESCR_AZIONE'
        ]

        # only complete and non-empty classifications are created or updated
        if all(k in df.columns.values for k in keywords):
            cols = ['DPS_CODICE_PROGRAMMA', 'DPS_DESCRIZIONE_PROGRAMMA']
            df1 = df[cols].drop_duplicates()
            for index, row in df1.iterrows():
                if all(row[k].strip() for k in cols):
                    programma, created = ProgrammaLineaAzione.objects.get_or_create(
                        codice = row['DPS_CODICE_PROGRAMMA'],
                        defaults = {
                            'descrizione': row['DPS_DESCRIZIONE_PROGRAMMA'],
                            'tipo_classificazione': ProgrammaLineaAzione.TIPO.programma,
                        }
                    )
                    self._log(created, 'Creato programma (linea-azione): %s' % programma)

            cols = ['DPS_CODICE_PROGRAMMA', 'COD_LINEA', 'DESCR_LINEA']
            df1 = df[cols].drop_duplicates()
            for index, row in df1.iterrows():
                if all(row[k].strip() for k in cols):
                    programma, created = ProgrammaLineaAzione.objects.get_or_create(
                        codice = '%s/%s' % (row['DPS_CODICE_PROGRAMMA'], row['COD_LINEA']),
                        defaults = {
                            'descrizione': row['DESCR_LINEA'],
                            'tipo_classificazione': ProgrammaLineaAzione.TIPO.linea,
                            'classificazione_superiore_id': row['DPS_CODICE_PROGRAMMA'],
                        }
                    )
                    self._log(created, 'Creata linea: %s' % programma)

            cols = ['DPS_CODICE_PROGRAMMA', 'COD_LINEA', 'COD_AZIONE', 'DESCR_AZIONE']
            df1 = df[cols].drop_duplicates()
            for index, row in df1.iterrows():
                if all(row[k].strip() for k in cols):
                    programma, created = ProgrammaLineaAzione.objects.get_or_create(
                        codice = '%s/%s/%s' % (row['DPS_CODICE_PROGRAMMA'], row['COD_LINEA'], row['COD_AZIONE']),
                        defaults = {
                            'descrizione': row['DESCR_AZIONE'],
                            'tipo_classificazione': ProgrammaLineaAzione.TIPO.azione,
                            'classificazione_superiore_id': '%s/%s' % (row['DPS_CODICE_PROGRAMMA'], row['COD_LINEA']),
                        }
                    )
                    self._log(created, 'Creata azione: %s' % programma)


    def _handle_progetti_classificazioneqsn(self, df):
        df1 = df[['QSN_COD_PRIORITA', 'QSN_DESCRIZIONE_PRIORITA']].drop_duplicates()
        for index, row in df1.iterrows():
            if row['QSN_COD_PRIORITA'].strip():
                classificazione, created = ClassificazioneQSN.objects.get_or_create(
                    codice = row['QSN_COD_PRIORITA'],
                    defaults = {
                        'descrizione': row['QSN_DESCRIZIONE_PRIORITA'],
                        'tipo_classificazione': ClassificazioneQSN.TIPO.priorita,
                    }
                )
                self._log(created, u'Creata priorità QSN: %s' % classificazione)

        df1 = df[['QSN_COD_PRIORITA', 'QSN_COD_OBIETTIVO_GENERALE', 'QSN_DESCR_OBIETTIVO_GENERALE']].drop_duplicates()
        for index, row in df1.iterrows():
            if row['QSN_COD_PRIORITA'].strip():
                classificazione, created = ClassificazioneQSN.objects.get_or_create(
                    codice = row['QSN_COD_OBIETTIVO_GENERALE'],
                    defaults = {
                        'descrizione': row['QSN_DESCR_OBIETTIVO_GENERALE'],
                        'tipo_classificazione': ClassificazioneQSN.TIPO.generale,
                        'classificazione_superiore_id': row['QSN_COD_PRIORITA'],
                    }
                )
                self._log(created, 'Creato obiettivo generale QSN: %s' % classificazione)

        df1 = df[['QSN_COD_PRIORITA', 'QSN_COD_OBIETTIVO_GENERALE', 'QSN_CODICE_OBIETTIVO_SPECIFICO', 'QSN_DESCR_OBIETTIVO_SPECIFICO']].drop_duplicates()
        for index, row in df1.iterrows():
            if row['QSN_COD_PRIORITA'].strip():
                classificazione, created = ClassificazioneQSN.objects.get_or_create(
                    codice = row['QSN_CODICE_OBIETTIVO_SPECIFICO'],
                    defaults = {
                        'descrizione': row['QSN_DESCR_OBIETTIVO_SPECIFICO'],
                        'tipo_classificazione': ClassificazioneQSN.TIPO.specifico,
                        'classificazione_superiore_id': row['QSN_COD_OBIETTIVO_GENERALE'],
                    }
                )
                self._log(created, 'Creato obiettivo specifico QSN: %s' % classificazione)


    def _handle_progetti_classificazioneazione(self, df):
        df1 = df[['CUP_COD_NATURA', 'CUP_DESCR_NATURA']].drop_duplicates()
        for index, row in df1.iterrows():
            classificazione, created = ClassificazioneAzione.objects.get_or_create(
                codice = row['CUP_COD_NATURA'],
                defaults = {
                    'descrizione': 'ACQUISTO DI BENI E SERVIZI' if row['CUP_COD_NATURA'] == '01' else row['CUP_DESCR_NATURA'],
                    'tipo_classificazione': ClassificazioneAzione.TIPO.natura,
                }
            )
            self._log(created, 'Creata classificazione azione natura: %s' % classificazione)

        df1 = df[['CUP_COD_NATURA', 'CUP_COD_TIPOLOGIA', 'CUP_DESCR_TIPOLOGIA']].drop_duplicates()
        for index, row in df1.iterrows():
            classificazione, created = ClassificazioneAzione.objects.get_or_create(
                codice = '%s.%s' % (row['CUP_COD_NATURA'], row['CUP_COD_TIPOLOGIA']),
                defaults = {
                    'descrizione': row['CUP_DESCR_TIPOLOGIA'],
                    'tipo_classificazione': ClassificazioneAzione.TIPO.tipologia,
                    'classificazione_superiore_id': row['CUP_COD_NATURA'],
                }
            )
            self._log(created, 'Creata classificazione azione natura_tipologia: %s' % classificazione)


    def _handle_progetti_classificazioneoggetto(self, df):
        df1 = df[['CUP_COD_SETTORE', 'CUP_DESCR_SETTORE']].drop_duplicates()
        for index, row in df1.iterrows():
            classificazione, created = ClassificazioneOggetto.objects.get_or_create(
                codice = row['CUP_COD_SETTORE'],
                defaults = {
                    'descrizione': row['CUP_DESCR_SETTORE'],
                    'tipo_classificazione': ClassificazioneOggetto.TIPO.settore,
                }
            )
            self._log(created, 'Creata classificazione oggetto settore: %s' % classificazione)

        df1 = df[['CUP_COD_SETTORE', 'CUP_COD_SOTTOSETTORE', 'CUP_DESCR_SOTTOSETTORE']].drop_duplicates()
        for index, row in df1.iterrows():
            classificazione, created = ClassificazioneOggetto.objects.get_or_create(
                codice = '%s.%s' % (row['CUP_COD_SETTORE'], row['CUP_COD_SOTTOSETTORE']),
                defaults = {
                    'descrizione': row['CUP_DESCR_SOTTOSETTORE'],
                    'tipo_classificazione': ClassificazioneOggetto.TIPO.sottosettore,
                    'classificazione_superiore_id': row['CUP_COD_SETTORE'],
                }
            )
            self._log(created, 'Creata classificazione oggetto settore_sottosettore: %s' % classificazione)

        df1 = df[['CUP_COD_SETTORE', 'CUP_COD_SOTTOSETTORE', 'CUP_COD_CATEGORIA', 'CUP_DESCR_CATEGORIA']].drop_duplicates()
        for index, row in df1.iterrows():
            classificazione, created = ClassificazioneOggetto.objects.get_or_create(
                codice = '%s.%s.%s' % (row['CUP_COD_SETTORE'], row['CUP_COD_SOTTOSETTORE'], row['CUP_COD_CATEGORIA']),
                defaults = {
                    'descrizione': row['CUP_DESCR_CATEGORIA'],
                    'tipo_classificazione': ClassificazioneOggetto.TIPO.categoria,
                    'classificazione_superiore_id': '%s.%s' % (row['CUP_COD_SETTORE'], row['CUP_COD_SOTTOSETTORE']),
                }
            )
            self._log(created, 'Creata classificazione oggetto settore_sottosettore_categoria: %s' % classificazione)


    def _handle_progetti_tema(self, df):
        temisintetici_desc2cod = {}

        df1 = df[['DPS_TEMA_SINTETICO']].drop_duplicates()
        for index, row in df1.iterrows():
            try:
                latest_codice = Tema.objects.principali().extra(select={'codice_int': 'CAST(codice AS INTEGER)'}).latest('codice_int').codice_int
            except Tema.DoesNotExist:
                latest_codice = 0

            tema, created = Tema.objects.get_or_create(
                descrizione = row['DPS_TEMA_SINTETICO'],
                tipo_tema = Tema.TIPO.sintetico,
                defaults = {
                    'codice': latest_codice + 1,
                }
            )
            self._log(created, 'Creato tema sintetico: %s' % tema)

            temisintetici_desc2cod[tema.descrizione] = tema.codice

        df1 = df[['DPS_TEMA_SINTETICO', 'QSN_COD_TEMA_PRIORITARIO_UE', 'QSN_DESCR_TEMA_PRIORITARIO_UE']].drop_duplicates()
        for index, row in df1.iterrows():
            tema, created = Tema.objects.get_or_create(
                codice = '%s.%s' % (temisintetici_desc2cod[row['DPS_TEMA_SINTETICO']], row['QSN_COD_TEMA_PRIORITARIO_UE']),
                defaults = {
                    'descrizione': row['QSN_DESCR_TEMA_PRIORITARIO_UE'],
                    'tipo_tema': Tema.TIPO.prioritario,
                    'tema_superiore_id': temisintetici_desc2cod[row['DPS_TEMA_SINTETICO']],
                }
            )
            self._log(created, 'Creato tema: %s' % tema)


    def _handle_progetti_fonte(self, df):
        df1 = df[['DPS_COD_FONTE', 'DPS_DESCR_FONTE']].drop_duplicates()
        for index, row in df1.iterrows():
            if 'FSC' in row['DPS_COD_FONTE']:
                tipo_fonte = Fonte.TIPO.fsc
            elif 'FS' in row['DPS_COD_FONTE']:
                tipo_fonte = Fonte.TIPO.fs
            elif row['DPS_COD_FONTE'] == 'PAC':
                tipo_fonte = Fonte.TIPO.pac
            else:
                tipo_fonte = None

            fonte, created = Fonte.objects.get_or_create(
                codice = row['DPS_COD_FONTE'],
                defaults = {
                    'descrizione': row['DPS_DESCR_FONTE'],
                    'tipo_fonte': tipo_fonte,
                }
            )
            self._log(created, 'Creata fonte: %s' % fonte)


    def _handle_progetti(self, df, delete, active_flag):
        self._handle_progetti_programmaasseobiettivo(df)
        self._handle_progetti_programmalineaazione(df)
        self._handle_progetti_classificazioneqsn(df)
        self._handle_progetti_classificazioneazione(df)
        self._handle_progetti_classificazioneoggetto(df)
        self._handle_progetti_tema(df)
        self._handle_progetti_fonte(df)

        temisintetici_desc2cod = {}
        for tema in Tema.objects.principali():
            temisintetici_desc2cod[tema.descrizione] = tema.codice

        fonti_cod2obj = {}
        for fonte in Fonte.objects.all():
            fonti_cod2obj[fonte.codice] = fonte

        if delete:
            Progetto.fullobjects.filter(active_flag=active_flag).all().delete()
            self.logger.info('Oggetti rimossi')

        n = 0
        for index, row in df.iterrows():
            n += 1

            # codice locale (ID del record)
            codice_locale = row['COD_LOCALE_PROGETTO']

            # obiettivo sviluppo
            obiettivo_sviluppo = None
            if 'QSN_AREA_OBIETTIVO_UE' in row:
                field = re.sub(' +', ' ', row['QSN_AREA_OBIETTIVO_UE'].encode('ascii', 'ignore')).strip()
                if field:
                    try:
                        obiettivo_sviluppo = [k for k, v in dict(Progetto.OBIETTIVO_SVILUPPO).iteritems() if v.encode('ascii', 'ignore') == field][0]
                        self.logger.debug('Trovato obiettivo sviluppo: %s' % obiettivo_sviluppo)
                    except IndexError as e:
                        self.logger.error('Could not find  obiettivo sviluppo %s in %s.' % (field, codice_locale))
                        continue

            # fondo comunitario
            fondo_comunitario = None
            if 'QSN_FONDO_COMUNITARIO' in row and row['QSN_FONDO_COMUNITARIO'].strip():
                try:
                    fondo_comunitario = [k for k, v in dict(Progetto.FONDO_COMUNITARIO).iteritems() if v == row['QSN_FONDO_COMUNITARIO']][0]
                    self.logger.debug('Trovato fondo comunitario: %s' % fondo_comunitario)
                except IndexError as e:
                    self.logger.error('While reading fondo comunitario %s in %s. %s' % (row['QSN_FONDO_COMUNITARIO'], codice_locale, e))
                    continue

            try:
                values = {}

                values['codice_locale'] = codice_locale

                values['titolo_progetto'] = row['DPS_TITOLO_PROGETTO']

                values['active_flag'] = active_flag
                values['cipe_flag'] = False

                values['obiettivo_sviluppo'] = obiettivo_sviluppo
                values['fondo_comunitario'] = fondo_comunitario

                if all(k in row and row[k].strip() for k in ['DPS_CODICE_PROGRAMMA', 'PO_CODICE_ASSE', 'PO_COD_OBIETTIVO_OPERATIVO', 'DPS_DESCRIZIONE_PROGRAMMA', 'PO_DENOMINAZIONE_ASSE', 'PO_OBIETTIVO_OPERATIVO']):
                    values['programma_asse_obiettivo_id'] = '%s/%s/%s' % (row['DPS_CODICE_PROGRAMMA'], row['PO_CODICE_ASSE'], row['PO_COD_OBIETTIVO_OPERATIVO'])

                if all(k in row and row[k].strip() for k in ['DPS_CODICE_PROGRAMMA', 'COD_LINEA', 'COD_AZIONE', 'DPS_DESCRIZIONE_PROGRAMMA', 'DESCR_LINEA', 'DESCR_AZIONE']):
                    values['programma_linea_azione_id'] = '%s/%s/%s' % (row['DPS_CODICE_PROGRAMMA'], row['COD_LINEA'], row['COD_AZIONE'])

                values['classificazione_qsn_id'] = row['QSN_CODICE_OBIETTIVO_SPECIFICO']
                values['classificazione_azione_id'] = '%s.%s' % (row['CUP_COD_NATURA'], row['CUP_COD_TIPOLOGIA'])
                values['classificazione_oggetto_id'] = '%s.%s.%s' % (row['CUP_COD_SETTORE'], row['CUP_COD_SOTTOSETTORE'], row['CUP_COD_CATEGORIA'])
                values['tema_id'] = '%s.%s' % (temisintetici_desc2cod[row['DPS_TEMA_SINTETICO']], row['QSN_COD_TEMA_PRIORITARIO_UE'])

                values['cup'] = row['CUP'].strip()

                # totale finanziamento
                values['fin_totale_pubblico'] = self._get_value(row, 'FINANZ_TOTALE_PUBBLICO', 'decimal')

                # aggiustamenti dovuti alle economie
                values['fin_totale_pubblico_netto'] = self._get_value(row, 'DPS_FINANZ_TOT_PUB_NETTO', 'decimal')
                values['economie_totali'] = self._get_value(row, 'ECONOMIE_TOTALI', 'decimal')
                values['economie_totali_pubbliche'] = self._get_value(row, 'ECONOMIE_TOTALI_PUBBLICHE', 'decimal')

                values['fin_ue'] = self._get_value(row, 'FINANZ_UE', 'decimal')
                values['fin_stato_fondo_rotazione'] = self._get_value(row, 'FINANZ_STATO_FONDO_DI_ROTAZIONE', 'decimal')
                values['fin_stato_pac'] = self._get_value(row, 'FINANZ_STATO_PAC', 'decimal')
                values['fin_stato_fsc'] = self._get_value(row, 'FINANZ_STATO_FSC', 'decimal')
                values['fin_stato_altri_provvedimenti'] = self._get_value(row, 'FINANZ_STATO_ALTRI_PROVVEDIMENTI', 'decimal')
                values['fin_regione'] = self._get_value(row, 'FINANZ_REGIONE', 'decimal')
                values['fin_provincia'] = self._get_value(row, 'FINANZ_PROVINCIA', 'decimal')
                values['fin_comune'] = self._get_value(row, 'FINANZ_COMUNE', 'decimal')
                values['fin_risorse_liberate'] = self._get_value(row, 'FINANZ_RISORSE_LIBERATE', 'decimal')
                values['fin_altro_pubblico'] = self._get_value(row, 'FINANZ_ALTRO_PUBBLICO', 'decimal')
                values['fin_stato_estero'] = self._get_value(row, 'FINANZ_STATO_ESTERO', 'decimal')
                values['fin_privato'] = self._get_value(row, 'FINANZ_PRIVATO', 'decimal')
                values['fin_da_reperire'] = self._get_value(row, 'FINANZ_DA_REPERIRE', 'decimal')

                values['pagamento'] = self._get_value(row, 'TOT_PAGAMENTI', 'decimal')
                values['pagamento_fsc'] = self._get_value(row, 'TOT_PAGAMENTI_FSC', 'decimal')

                values['costo_ammesso'] = self._get_value(row, 'COSTO_RENDICONTABILE_UE', 'decimal')
                values['pagamento_ammesso'] = self._get_value(row, 'TOT_PAGAMENTI_RENDICONTABILI_UE', 'decimal')

                # date
                values['data_inizio_prevista'] = self._get_value(row, 'DPS_DATA_INIZIO_PREVISTA', 'date')
                values['data_fine_prevista'] = self._get_value(row, 'DPS_DATA_FINE_PREVISTA', 'date')
                values['data_inizio_effettiva'] = self._get_value(row, 'DPS_DATA_INIZIO_EFFETTIVA', 'date')
                values['data_fine_effettiva'] = self._get_value(row, 'DPS_DATA_FINE_EFFETTIVA', 'date')

                # data ultimo aggiornamento progetto
                values['data_aggiornamento'] = self._get_value(row, 'DATA_AGGIORNAMENTO', 'date')

                values['dps_flag_presenza_date'] = row['DPS_FLAG_PRESENZA_DATE']
                values['dps_flag_date_previste'] = row['DPS_FLAG_COERENZA_DATE_PREV']
                values['dps_flag_date_effettive'] = row['DPS_FLAG_COERENZA_DATE_EFF']
                values['dps_flag_cup'] = row['DPS_FLAG_CUP']
                values['dps_flag_pac'] = row['DPS_FLAG_PAC']

            except ValueError as e:
                self.logger.error('%s: %s. Skipping' % (codice_locale, e))
                continue

            try:
                Progetto.fullobjects.create(**values)\
                    .fonte_set.add(fonti_cod2obj[row['DPS_COD_FONTE']])

                self.logger.info('%s - Creato progetto: %s' % (n, codice_locale))

            except DatabaseError as e:
                self.logger.error('%s - ERRORE progetto %s: %s. Skipping.' % (n, codice_locale, e))
                continue


    def _log(self, created, msg):
        if created:
            self.logger.info(msg)
        else:
            self.logger.debug(msg.replace('Creat', 'Trovat'))


    def _get_value(self, dict, key, type = 'string'):
        """
        """
        if key in dict:
            dict[key] = str(dict[key])
            if dict[key].strip():
                value = dict[key].strip()

                if type == 'decimal':
                    value = Decimal(value.replace(',','.'))
                elif type == 'date':
                    value = datetime.datetime.strptime(value, '%Y%m%d')

                return value

        return None
