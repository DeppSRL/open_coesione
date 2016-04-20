# -*- coding: utf-8 -*-
from decimal import Decimal
import json
import logging
from collections import OrderedDict
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import transaction
from django.db.utils import DatabaseError, IntegrityError
from django.core.management.base import BaseCommand

from optparse import make_option

import re
import pandas as pd
import datetime
import zipfile
from cStringIO import StringIO

from progetti.models import Progetto, ProgettoDeliberaCIPE, DeliberaCIPE, Ruolo, Localizzazione, PagamentoProgetto,\
    ProgrammaAsseObiettivo, ProgrammaLineaAzione, ClassificazioneAzione, ClassificazioneOggetto, ClassificazioneQSN,\
    Tema, Fonte
from soggetti.models import Soggetto
from territori.models import Territorio


def convert_progetto_cup_cod_natura(val):
    if val.strip():
        try:
            val = int(val)
            if val == 2:
                val = 1
            val = '{:02d}'.format(val)
        except ValueError:
            pass
    else:
        val = ' '
    return val


def convert_progetto_cup_cod_tipologia(val):
    if val.strip():
        try:
            val = '{:02d}'.format(int(val))
        except ValueError:
            pass
    else:
        val = ' '
    return val


def convert_progetto_cup_cod_settore(val):
    if val.strip():
        try:
            val = '{:02d}'.format(int(val))
        except ValueError:
            pass
    return val


def convert_progetto_cup_cod_sottosettore(val):
    if val.strip():
        try:
            val = '{:02d}'.format(int(val))
        except ValueError:
            pass
    return val


def convert_progetto_cup_cod_categoria(val):
    if val.strip():
        try:
            val = '{:03d}'.format(int(val))
        except ValueError:
            pass
    return val


def convert_oc_tema_sintetico(val):
    topic_map = {
        u'Rinnovamento urbano e rurale': u'Rinnovamento urbano  e rurale',
        u'Rafforzamento delle capacità della PA': u'Rafforzamento capacità della PA',
    }

    val = val.strip()
    return topic_map.get(val, val)


def convert_progetto_qsn_cod_tema_prioritario_ue(val):
    if val.strip():
        try:
            val = '{:02d}'.format(int(val))
        except ValueError:
            pass
    else:
        val = '00'
    return val


def convert_soggetto_oc_denominazione_sogg(val):
    return re.sub('\s{2,}', u' ', val).strip()
    # return val.encode('ascii', 'ignore').strip()


def convert_progettocipe_cup(val):
    val = re.sub('[\s\n\r]+', '', val)
    return tuple(val.split(':::')) if val else ()


class Command(BaseCommand):
    """
    Data are imported from their CSV sources.
    """
    help = 'Import data from csv'

    import_types = {
        'progetti': {
            'files': ['totale/progetti_FSC0006_{}.zip', 'totale/progetti_FSC0713_{}.zip', 'totale/progetti_FS0713_{}.zip', 'totale/progetti_PAC_{}.zip', 'prog_inattivi_{}.zip'],
            'import_method': '_import_progetti',
            'converters': {
                'CUP_COD_NATURA': convert_progetto_cup_cod_natura,
                'CUP_COD_TIPOLOGIA': convert_progetto_cup_cod_tipologia,
                'CUP_COD_SETTORE': convert_progetto_cup_cod_settore,
                'CUP_COD_SOTTOSETTORE': convert_progetto_cup_cod_sottosettore,
                'CUP_COD_CATEGORIA': convert_progetto_cup_cod_categoria,
                'OC_TEMA_SINTETICO': convert_oc_tema_sintetico,
                'QSN_COD_TEMA_PRIORITARIO_UE': convert_progetto_qsn_cod_tema_prioritario_ue,
            },
        },
        'progetti-cipe': {
            'files': ['totale/assegnazioni_CIPE.zip'],
            'import_method': '_import_progetticipe',
            'converters': {
                'CUP_COD_NATURA': convert_progetto_cup_cod_natura,
                'CUP_COD_SETTORE': convert_progetto_cup_cod_settore,
                'CUP_COD_SOTTOSETTORE': convert_progetto_cup_cod_sottosettore,
                'CUP': convert_progettocipe_cup,
            },
        },
        'soggetti': {
            'files': ['totale/soggetti_FSC0006_{}.zip', 'totale/soggetti_FSC0713_{}.zip', 'totale/soggetti_FS0713_{}.zip', 'totale/soggetti_PAC_{}.zip', 'totale/soggetti_CIPE.zip'],
            'import_method': '_import_soggetti',
            'converters': {
                'OC_DENOMINAZIONE_SOGG': convert_soggetto_oc_denominazione_sogg,
            },
        },
        'localizzazioni': {
            'files': ['totale/localizzazioni_FSC0006_{}.zip', 'totale/localizzazioni_FSC0713_{}.zip', 'totale/localizzazioni_FS0713_{}.zip', 'totale/localizzazioni_PAC_{}.zip', 'totale/localizzazioni_CIPE.zip', 'loc_inattivi_{}.zip'],
            'import_method': '_import_localizzazioni',
            'converters': None,
        },
        'pagamenti': {
            'files': ['totale/pagamenti_FSC0006_{}.zip', 'totale/pagamenti_FSC0713_{}.zip', 'totale/pagamenti_FS0713_{}.zip', 'totale/pagamenti_PAC_{}.zip', 'pag_inattivi_{}.zip'],
            'import_method': '_import_pagamenti',
            'converters': None,
        },
        'update-privacy-progetti': {
            'files': ['prog_privacy_{}.csv', 'prog_inattivi_privacy_{}.csv'],
            'import_method': '_update_privacy_progetti',
            'converters': None,
        },
        'update-privacy-soggetti': {
            'files': ['sogg_privacy_{}.csv', 'sogg_inattivi_privacy_{}.csv'],
            'import_method': '_update_privacy_soggetti',
            'converters': None,
        },
    }

    option_list = BaseCommand.option_list + (
        make_option('--csv-path',
                    dest='csv_path',
                    default=None,
                    help='Select csv files path.'),
        make_option('--csv-date',
                    dest='csv_date',
                    default=None,
                    help='Date of data.'),
        make_option('--import-type',
                    dest='import_type',
                    default=None,
                    help='Type of import; select among {}.'.format(', '.join(['"' + t + '"' for t in import_types]))),
        make_option('--encoding',
                    dest='encoding',
                    default='utf-8-sig',
                    help='Set character encoding of input file.'),
    )

    logger = logging.getLogger('csvimport')

    def handle(self, *args, **options):
        verbosity = options['verbosity']
        if verbosity == '0':
            self.logger.setLevel(logging.ERROR)
        elif verbosity == '1':
            self.logger.setLevel(logging.WARNING)
        elif verbosity == '2':
            self.logger.setLevel(logging.INFO)
        elif verbosity == '3':
            self.logger.setLevel(logging.DEBUG)

        csvpath = options['csv_path']
        csvdate = options['csv_date']
        importtype = options['import_type']
        encoding = options['encoding']

        if not importtype in self.import_types:
            self.logger.error(u'Wrong type "{}". Select among {}.'.format(importtype, ', '.join(['"' + t + '"' for t in self.import_types])))
            exit(1)

        df = pd.DataFrame()

        # read csv files
        for file in self.import_types[importtype]['files']:
            csvfile = csvpath.rstrip('/') + '/' + file.format(csvdate)

            self.logger.info(u'Reading file {} ....'.format(csvfile))

            try:
                if csvfile.endswith('.zip'):
                    with zipfile.ZipFile(csvfile) as zfile:
                        csv = zfile.read(zfile.namelist().pop(0))
                else:
                    with open(csvfile, 'rb') as cfile:
                        csv = cfile.read()

                df_tmp = pd.read_csv(
                    StringIO(csv.decode(encoding).encode('utf-8')),
                    sep=';',
                    header=0,
                    low_memory=True,
                    dtype=object,
                    encoding='utf-8',
                    keep_default_na=False,
                    converters=self.import_types[importtype]['converters'],
                )
            except IOError:
                self.logger.error(u'It was impossible to open file {}'.format(csvfile))
                continue
            else:
                df_tmp[u'FLAG_ATTIVO'] = not ('inattivi' in file)

                df = df.append(df_tmp, ignore_index=True)

                del df_tmp

                self.logger.info(u'Done.')

        if len(df) == 0:
            self.logger.error(u'Nessun dato da processare.')
            exit(1)

        df.fillna('', inplace=True)
        df.drop_duplicates(inplace=True)

        self.logger.info(u'Inizio import "{}" ({}).'.format(importtype, csvdate))

        start_time = datetime.datetime.now()

        method = getattr(self, str(self.import_types[importtype]['import_method']))
        method(df)

        duration = datetime.datetime.now() - start_time
        seconds = round(duration.total_seconds())

        self.logger.info(u'Fine. Tempo di esecuzione: {:02d}:{:02d}:{:02d}.'.format(int(seconds // 3600), int((seconds % 3600) // 60), int(seconds % 60)))

    @transaction.commit_on_success
    def _import_progetti_programmaasseobiettivo(self, df):
        keywords = [
            'OC_CODICE_PROGRAMMA', 'PO_CODICE_ASSE', 'PO_COD_OBIETTIVO_OPERATIVO',
            'OC_DESCRIZIONE_PROGRAMMA', 'PO_DENOMINAZIONE_ASSE', 'PO_OBIETTIVO_OPERATIVO'
        ]

        # only complete and non-empty classifications are created
        if all(k in df.columns.values for k in keywords):
            df_filtered = df[(df['OC_CODICE_PROGRAMMA'].str.strip() != '') & (df['PO_CODICE_ASSE'].str.strip() != '') & (df['PO_COD_OBIETTIVO_OPERATIVO'].str.strip() != '')]

            df1 = df_filtered[['OC_CODICE_PROGRAMMA', 'OC_DESCRIZIONE_PROGRAMMA']].drop_duplicates()
            for index, row in df1.iterrows():
                programma, created = ProgrammaAsseObiettivo.objects.get_or_create(
                    codice=row['OC_CODICE_PROGRAMMA'],
                    defaults={
                        'descrizione': row['OC_DESCRIZIONE_PROGRAMMA'],
                        'tipo_classificazione': ProgrammaAsseObiettivo.TIPO.programma,
                    }
                )
                self._log(created, u'Creato programma (asse-obiettivo): {}'.format(programma))

            df1 = df_filtered[['OC_CODICE_PROGRAMMA', 'PO_CODICE_ASSE', 'PO_DENOMINAZIONE_ASSE']].drop_duplicates()
            for index, row in df1.iterrows():
                programma, created = ProgrammaAsseObiettivo.objects.get_or_create(
                    codice='{}/{}'.format(row['OC_CODICE_PROGRAMMA'], row['PO_CODICE_ASSE']),
                    defaults={
                        'descrizione': row['PO_DENOMINAZIONE_ASSE'],
                        'tipo_classificazione': ProgrammaAsseObiettivo.TIPO.asse,
                        'classificazione_superiore_id': row['OC_CODICE_PROGRAMMA'],
                    }
                )
                self._log(created, u'Creato asse: {}'.format(programma))

            df1 = df_filtered[['OC_CODICE_PROGRAMMA', 'PO_CODICE_ASSE', 'PO_COD_OBIETTIVO_OPERATIVO', 'PO_OBIETTIVO_OPERATIVO']].drop_duplicates()
            for index, row in df1.iterrows():
                programma, created = ProgrammaAsseObiettivo.objects.get_or_create(
                    codice='{}/{}/{}'.format(row['OC_CODICE_PROGRAMMA'], row['PO_CODICE_ASSE'], row['PO_COD_OBIETTIVO_OPERATIVO']),
                    defaults={
                        'descrizione': row['PO_OBIETTIVO_OPERATIVO'],
                        'tipo_classificazione': ProgrammaAsseObiettivo.TIPO.obiettivo,
                        'classificazione_superiore_id': '{}/{}'.format(row['OC_CODICE_PROGRAMMA'], row['PO_CODICE_ASSE']),
                    }
                )
                self._log(created, u'Creato obiettivo: {}'.format(programma))

    @transaction.commit_on_success
    def _import_progetti_programmalineaazione(self, df):
        keywords = [
            'OC_CODICE_PROGRAMMA', 'COD_LINEA', 'COD_AZIONE',
            'OC_DESCRIZIONE_PROGRAMMA', 'DESCR_LINEA', 'DESCR_AZIONE'
        ]

        # only complete and non-empty classifications are created
        if all(k in df.columns.values for k in keywords):
            df_filtered = df[(df['OC_CODICE_PROGRAMMA'].str.strip() != '') & (df['COD_LINEA'].str.strip() != '') & (df['COD_AZIONE'].str.strip() != '')]

            df1 = df_filtered[['OC_CODICE_PROGRAMMA', 'OC_DESCRIZIONE_PROGRAMMA']].drop_duplicates()
            for index, row in df1.iterrows():
                programma, created = ProgrammaLineaAzione.objects.get_or_create(
                    codice=row['OC_CODICE_PROGRAMMA'],
                    defaults={
                        'descrizione': row['OC_DESCRIZIONE_PROGRAMMA'],
                        'tipo_classificazione': ProgrammaLineaAzione.TIPO.programma,
                    }
                )
                self._log(created, u'Creato programma (linea-azione): {}'.format(programma))

            df1 = df_filtered[['OC_CODICE_PROGRAMMA', 'COD_LINEA', 'DESCR_LINEA']].drop_duplicates()
            for index, row in df1.iterrows():
                programma, created = ProgrammaLineaAzione.objects.get_or_create(
                    codice='{}/{}'.format(row['OC_CODICE_PROGRAMMA'], row['COD_LINEA']),
                    defaults={
                        'descrizione': row['DESCR_LINEA'],
                        'tipo_classificazione': ProgrammaLineaAzione.TIPO.linea,
                        'classificazione_superiore_id': row['OC_CODICE_PROGRAMMA'],
                    }
                )
                self._log(created, u'Creata linea: {}'.format(programma))

            df1 = df_filtered[['OC_CODICE_PROGRAMMA', 'COD_LINEA', 'COD_AZIONE', 'DESCR_AZIONE']].drop_duplicates()
            for index, row in df1.iterrows():
                programma, created = ProgrammaLineaAzione.objects.get_or_create(
                    codice='{}/{}/{}'.format(row['OC_CODICE_PROGRAMMA'], row['COD_LINEA'], row['COD_AZIONE']),
                    defaults={
                        'descrizione': row['DESCR_AZIONE'],
                        'tipo_classificazione': ProgrammaLineaAzione.TIPO.azione,
                        'classificazione_superiore_id': '{}/{}'.format(row['OC_CODICE_PROGRAMMA'], row['COD_LINEA']),
                    }
                )
                self._log(created, u'Creata azione: {}'.format(programma))

    @transaction.commit_on_success
    def _import_progetti_classificazioneazione(self, df):
        keywords = [
            'CUP_COD_NATURA', 'CUP_COD_TIPOLOGIA',
            'CUP_DESCR_NATURA', 'CUP_DESCR_TIPOLOGIA'
        ]

        # only complete and non-empty classifications are created
        if all(k in df.columns.values for k in keywords):
            # df_filtered = df[(df['CUP_COD_NATURA'].str.strip() != '') & (df['CUP_COD_TIPOLOGIA'].str.strip() != '')]
            df_filtered = df

            df1 = df_filtered[['CUP_COD_NATURA', 'CUP_DESCR_NATURA']].drop_duplicates()
            for index, row in df1.iterrows():
                classificazione, created = ClassificazioneAzione.objects.get_or_create(
                    codice=row['CUP_COD_NATURA'],
                    defaults={
                        'descrizione': 'ACQUISTO DI BENI E SERVIZI' if row['CUP_COD_NATURA'] == '01' else row['CUP_DESCR_NATURA'],
                        'tipo_classificazione': ClassificazioneAzione.TIPO.natura,
                    }
                )
                self._log(created, u'Creata classificazione azione natura: {}'.format(classificazione))

            df1 = df_filtered[['CUP_COD_NATURA', 'CUP_COD_TIPOLOGIA', 'CUP_DESCR_TIPOLOGIA']].drop_duplicates()
            for index, row in df1.iterrows():
                classificazione, created = ClassificazioneAzione.objects.get_or_create(
                    codice='{}.{}'.format(row['CUP_COD_NATURA'], '00' if row['CUP_COD_NATURA'] == '03' and row['CUP_COD_TIPOLOGIA'] == ' ' else row['CUP_COD_TIPOLOGIA']),
                    defaults={
                        'descrizione': row['CUP_DESCR_TIPOLOGIA'],
                        'tipo_classificazione': ClassificazioneAzione.TIPO.tipologia,
                        'classificazione_superiore_id': row['CUP_COD_NATURA'],
                    }
                )
                self._log(created, u'Creata classificazione azione natura_tipologia: {}'.format(classificazione))

    @transaction.commit_on_success
    def _import_progetti_classificazioneoggetto(self, df):
        keywords = [
            'CUP_COD_SETTORE', 'CUP_COD_SOTTOSETTORE', 'CUP_COD_CATEGORIA',
            'CUP_DESCR_SETTORE', 'CUP_DESCR_SOTTOSETTORE', 'CUP_DESCR_CATEGORIA'
        ]

        # only complete and non-empty classifications are created
        if all(k in df.columns.values for k in keywords):
            df_filtered = df[(df['CUP_COD_SETTORE'].str.strip() != '') & (df['CUP_COD_SOTTOSETTORE'].str.strip() != '') & (df['CUP_COD_CATEGORIA'].str.strip() != '')]

            df1 = df_filtered[['CUP_COD_SETTORE', 'CUP_DESCR_SETTORE']].drop_duplicates()
            for index, row in df1.iterrows():
                classificazione, created = ClassificazioneOggetto.objects.get_or_create(
                    codice=row['CUP_COD_SETTORE'],
                    defaults={
                        'descrizione': row['CUP_DESCR_SETTORE'],
                        'tipo_classificazione': ClassificazioneOggetto.TIPO.settore,
                    }
                )
                self._log(created, u'Creata classificazione oggetto settore: {}'.format(classificazione))

            df1 = df_filtered[['CUP_COD_SETTORE', 'CUP_COD_SOTTOSETTORE', 'CUP_DESCR_SOTTOSETTORE']].drop_duplicates()
            for index, row in df1.iterrows():
                classificazione, created = ClassificazioneOggetto.objects.get_or_create(
                    codice='{}.{}'.format(row['CUP_COD_SETTORE'], row['CUP_COD_SOTTOSETTORE']),
                    defaults={
                        'descrizione': row['CUP_DESCR_SOTTOSETTORE'],
                        'tipo_classificazione': ClassificazioneOggetto.TIPO.sottosettore,
                        'classificazione_superiore_id': row['CUP_COD_SETTORE'],
                    }
                )
                self._log(created, u'Creata classificazione oggetto settore_sottosettore: {}'.format(classificazione))

            df1 = df_filtered[['CUP_COD_SETTORE', 'CUP_COD_SOTTOSETTORE', 'CUP_COD_CATEGORIA', 'CUP_DESCR_CATEGORIA']].drop_duplicates()
            for index, row in df1.iterrows():
                classificazione, created = ClassificazioneOggetto.objects.get_or_create(
                    codice='{}.{}.{}'.format(row['CUP_COD_SETTORE'], row['CUP_COD_SOTTOSETTORE'], row['CUP_COD_CATEGORIA']),
                    defaults={
                        'descrizione': row['CUP_DESCR_CATEGORIA'],
                        'tipo_classificazione': ClassificazioneOggetto.TIPO.categoria,
                        'classificazione_superiore_id': '{}.{}'.format(row['CUP_COD_SETTORE'], row['CUP_COD_SOTTOSETTORE']),
                    }
                )
                self._log(created, u'Creata classificazione oggetto settore_sottosettore_categoria: {}'.format(classificazione))

    @transaction.commit_on_success
    def _import_progetti_classificazioneqsn(self, df):
        keywords = [
            'QSN_COD_PRIORITA', 'QSN_COD_OBIETTIVO_GENERALE', 'QSN_CODICE_OBIETTIVO_SPECIFICO',
            'QSN_DESCRIZIONE_PRIORITA', 'QSN_DESCR_OBIETTIVO_GENERALE', 'QSN_DESCR_OBIETTIVO_SPECIFICO'
        ]

        # only complete and non-empty classifications are created
        if all(k in df.columns.values for k in keywords):
            df_filtered = df[(df['QSN_COD_PRIORITA'].str.strip() != '') & (df['QSN_COD_OBIETTIVO_GENERALE'].str.strip() != '') & (df['QSN_CODICE_OBIETTIVO_SPECIFICO'].str.strip() != '')]

            df1 = df_filtered[['QSN_COD_PRIORITA', 'QSN_DESCRIZIONE_PRIORITA']].drop_duplicates()
            for index, row in df1.iterrows():
                classificazione, created = ClassificazioneQSN.objects.get_or_create(
                    codice=row['QSN_COD_PRIORITA'],
                    defaults={
                        'descrizione': row['QSN_DESCRIZIONE_PRIORITA'],
                        'tipo_classificazione': ClassificazioneQSN.TIPO.priorita,
                    }
                )
                self._log(created, u'Creata priorità QSN: {}'.format(classificazione))

            df1 = df_filtered[['QSN_COD_PRIORITA', 'QSN_COD_OBIETTIVO_GENERALE', 'QSN_DESCR_OBIETTIVO_GENERALE']].drop_duplicates()
            for index, row in df1.iterrows():
                classificazione, created = ClassificazioneQSN.objects.get_or_create(
                    codice=row['QSN_COD_OBIETTIVO_GENERALE'],
                    defaults={
                        'descrizione': row['QSN_DESCR_OBIETTIVO_GENERALE'],
                        'tipo_classificazione': ClassificazioneQSN.TIPO.generale,
                        'classificazione_superiore_id': row['QSN_COD_PRIORITA'],
                    }
                )
                self._log(created, u'Creato obiettivo generale QSN: {}'.format(classificazione))

            df1 = df_filtered[['QSN_COD_PRIORITA', 'QSN_COD_OBIETTIVO_GENERALE', 'QSN_CODICE_OBIETTIVO_SPECIFICO', 'QSN_DESCR_OBIETTIVO_SPECIFICO']].drop_duplicates()
            for index, row in df1.iterrows():
                classificazione, created = ClassificazioneQSN.objects.get_or_create(
                    codice=row['QSN_CODICE_OBIETTIVO_SPECIFICO'],
                    defaults={
                        'descrizione': row['QSN_DESCR_OBIETTIVO_SPECIFICO'],
                        'tipo_classificazione': ClassificazioneQSN.TIPO.specifico,
                        'classificazione_superiore_id': row['QSN_COD_OBIETTIVO_GENERALE'],
                    }
                )
                self._log(created, u'Creato obiettivo specifico QSN: {}'.format(classificazione))

    @transaction.commit_on_success
    def _import_progetti_tema(self, df):
        temisintetici_desc2cod = {}

        try:
            codice = Tema.objects.principali().extra(select={'codice_int': 'CAST(codice AS INTEGER)'}).latest('codice_int').codice_int + 1
        except ObjectDoesNotExist:
            codice = 1

        df1 = df[['OC_TEMA_SINTETICO']].drop_duplicates()
        for index, row in df1.iterrows():
            tema, created = Tema.objects.get_or_create(
                descrizione=row['OC_TEMA_SINTETICO'],
                tipo_tema=Tema.TIPO.sintetico,
                defaults={
                    'codice': codice,
                }
            )
            self._log(created, u'Creato tema sintetico: {}'.format(tema))

            if created:
                codice += 1

            temisintetici_desc2cod[tema.descrizione] = tema.codice

        df1 = df[['OC_TEMA_SINTETICO', 'QSN_COD_TEMA_PRIORITARIO_UE', 'QSN_DESCR_TEMA_PRIORITARIO_UE']].drop_duplicates()
        for index, row in df1.iterrows():
            tema, created = Tema.objects.get_or_create(
                codice='{}.{}'.format(temisintetici_desc2cod[row['OC_TEMA_SINTETICO']], row['QSN_COD_TEMA_PRIORITARIO_UE']),
                defaults={
                    'descrizione': row['QSN_DESCR_TEMA_PRIORITARIO_UE'],
                    'tipo_tema': Tema.TIPO.prioritario,
                    'tema_superiore_id': temisintetici_desc2cod[row['OC_TEMA_SINTETICO']],
                }
            )
            self._log(created, u'Creato tema: {}'.format(tema))

    @transaction.commit_on_success
    def _import_progetti_fonte(self, df):
        df1 = df[['OC_COD_FONTE', 'OC_DESCR_FONTE']].drop_duplicates()
        for index, row in df1.iterrows():
            if 'FSC' in row['OC_COD_FONTE']:
                tipo_fonte = Fonte.TIPO.fsc
            elif 'FS' in row['OC_COD_FONTE']:
                tipo_fonte = Fonte.TIPO.fs
            elif row['OC_COD_FONTE'] == 'PAC':
                tipo_fonte = Fonte.TIPO.pac
            else:
                tipo_fonte = None

            fonte, created = Fonte.objects.get_or_create(
                codice=row['OC_COD_FONTE'],
                defaults={
                    'descrizione': row['OC_DESCR_FONTE'],
                    'tipo_fonte': tipo_fonte,
                }
            )
            self._log(created, u'Creata fonte: {}'.format(fonte))

    @transaction.commit_manually
    def _import_progetti(self, df):
        self._import_progetti_programmaasseobiettivo(df)
        self._import_progetti_programmalineaazione(df)
        self._import_progetti_classificazioneazione(df)
        self._import_progetti_classificazioneoggetto(df)
        self._import_progetti_classificazioneqsn(df)
        self._import_progetti_tema(df)
        self._import_progetti_fonte(df)

        temisintetici_desc2cod = {tema.descrizione: tema.codice for tema in Tema.objects.principali()}
        fonti_cod2obj = {fonte.codice: fonte for fonte in Fonte.objects.all()}
        stato_desc2cod = {x[1]: x[0] for x in Progetto.STATO}

        # df1 = df.groupby('COD_LOCALE_PROGETTO', as_index=False).first()
        df1 = df

        df_count = len(df1)

        for n, (index, row) in enumerate(df1.iterrows(), 1):
            # codice locale (ID del record)
            codice_locale = row['COD_LOCALE_PROGETTO']

            # obiettivo sviluppo
            obiettivo_sviluppo = None
            if 'QSN_AREA_OBIETTIVO_UE' in row and row['QSN_AREA_OBIETTIVO_UE'].strip():
                field = re.sub(' +', ' ', row['QSN_AREA_OBIETTIVO_UE'].encode('ascii', 'ignore')).strip()
                if field:
                    try:
                        obiettivo_sviluppo = [k for k, v in dict(Progetto.OBIETTIVO_SVILUPPO).iteritems() if v.encode('ascii', 'ignore') == field][0]
                        self.logger.debug(u'Trovato obiettivo sviluppo: {}'.format(obiettivo_sviluppo))
                    except IndexError:
                        self.logger.error(u'Could not find obiettivo sviluppo {} in {}.'.format(field, codice_locale))
                        continue

            # fondo comunitario
            fondo_comunitario = None
            if 'QSN_FONDO_COMUNITARIO' in row and row['QSN_FONDO_COMUNITARIO'].strip():
                try:
                    fondo_comunitario = [k for k, v in dict(Progetto.FONDO_COMUNITARIO).iteritems() if v == row['QSN_FONDO_COMUNITARIO']][0]
                    self.logger.debug(u'Trovato fondo comunitario: {}'.format(fondo_comunitario))
                except IndexError as e:
                    self.logger.error(u'While reading fondo comunitario {} in {}. {}'.format(row['QSN_FONDO_COMUNITARIO'], codice_locale, e))
                    continue

            try:
                values = {}

                values['codice_locale'] = codice_locale

                values['titolo_progetto'] = row['OC_TITOLO_PROGETTO']

                values['active_flag'] = row['FLAG_ATTIVO']
                values['cipe_flag'] = False

                values['obiettivo_sviluppo'] = obiettivo_sviluppo
                values['fondo_comunitario'] = fondo_comunitario

                if all(k in row and row[k].strip() for k in ['OC_CODICE_PROGRAMMA', 'PO_CODICE_ASSE', 'PO_COD_OBIETTIVO_OPERATIVO']):
                    values['programma_asse_obiettivo_id'] = '{}/{}/{}'.format(row['OC_CODICE_PROGRAMMA'], row['PO_CODICE_ASSE'], row['PO_COD_OBIETTIVO_OPERATIVO'])

                if all(k in row and row[k].strip() for k in ['OC_CODICE_PROGRAMMA', 'COD_LINEA', 'COD_AZIONE']):
                    values['programma_linea_azione_id'] = '{}/{}/{}'.format(row['OC_CODICE_PROGRAMMA'], row['COD_LINEA'], row['COD_AZIONE'])

                values['classificazione_azione_id'] = '{}.{}'.format(row['CUP_COD_NATURA'], '00' if row['CUP_COD_NATURA'] == '03' and row['CUP_COD_TIPOLOGIA'] == ' ' else row['CUP_COD_TIPOLOGIA'])

                if all(k in row and row[k].strip() for k in ['CUP_COD_SETTORE', 'CUP_COD_SOTTOSETTORE', 'CUP_COD_CATEGORIA']):
                    values['classificazione_oggetto_id'] = '{}.{}.{}'.format(row['CUP_COD_SETTORE'], row['CUP_COD_SOTTOSETTORE'], row['CUP_COD_CATEGORIA'])

                if all(k in row and row[k].strip() for k in ['QSN_CODICE_OBIETTIVO_SPECIFICO']):
                    values['classificazione_qsn_id'] = row['QSN_CODICE_OBIETTIVO_SPECIFICO']

                values['tema_id'] = '{}.{}'.format(temisintetici_desc2cod[row['OC_TEMA_SINTETICO']], row['QSN_COD_TEMA_PRIORITARIO_UE'])

                values['cup'] = row['CUP'].strip()

                # totale finanziamento
                values['fin_totale_pubblico'] = self._get_value(row, 'FINANZ_TOTALE_PUBBLICO', 'decimal')

                # aggiustamenti dovuti alle economie
                values['fin_totale_pubblico_netto'] = self._get_value(row, 'OC_FINANZ_TOT_PUB_NETTO', 'decimal')
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
                values['pagamento_fsc'] = self._get_value(row, 'OC_TOT_PAGAMENTI_FSC', 'decimal')
                values['pagamento_pac'] = self._get_value(row, 'OC_TOT_PAGAMENTI_PAC', 'decimal')

                values['costo_rendicontabile_ue'] = self._get_value(row, 'COSTO_RENDICONTABILE_UE', 'decimal')
                values['pagamento_rendicontabile_ue'] = self._get_value(row, 'OC_TOT_PAGAMENTI_RENDICONTAB_UE', 'decimal')

                # date
                values['data_inizio_prevista'] = self._get_value(row, 'OC_DATA_INIZIO_PREVISTA', 'date')
                values['data_fine_prevista'] = self._get_value(row, 'OC_DATA_FINE_PREVISTA', 'date')
                values['data_inizio_effettiva'] = self._get_value(row, 'OC_DATA_INIZIO_EFFETTIVA', 'date')
                values['data_fine_effettiva'] = self._get_value(row, 'OC_DATA_FINE_EFFETTIVA', 'date')

                # data ultimo aggiornamento progetto
                values['data_aggiornamento'] = self._get_value(row, 'DATA_AGGIORNAMENTO', 'date')

                values['dps_flag_presenza_date'] = row['OC_FLAG_PRESENZA_DATE']
                values['dps_flag_date_previste'] = row['OC_FLAG_COERENZA_DATE_PREV']
                values['dps_flag_date_effettive'] = row['OC_FLAG_COERENZA_DATE_EFF']
                values['dps_flag_cup'] = row['OC_FLAG_CUP']
                values['dps_flag_pac'] = row['OC_FLAG_PAC']

                values['stato_progetto'] = stato_desc2cod.get(row['OC_STATO_PROGETTO'])
                values['stato_finanziario'] = stato_desc2cod.get(row['OC_STATO_FINANZIARIO'])

                values['csv_data'] = json.dumps(OrderedDict(row), ensure_ascii=False, sort_keys=True)

            except ValueError as e:
                self.logger.error(u'{}/{} - {}: {}. Skipping'.format(n, df_count, codice_locale, e))

            else:
                try:
                    sid = transaction.savepoint()

                    Progetto.fullobjects.create(**values)\
                        .fonte_set.add(fonti_cod2obj[row['OC_COD_FONTE']])

                    transaction.savepoint_commit(sid)

                    self.logger.info(u'{}/{} - Creato progetto: {}'.format(n, df_count, codice_locale))

                except IntegrityError:
                    transaction.savepoint_rollback(sid)

                    values = {k: values[k] for k in values if k in ['programma_asse_obiettivo_id', 'programma_linea_azione_id']}

                    Progetto.fullobjects.get(codice_locale=codice_locale).update(**values)

                    self.logger.warning(u'{}/{} - Trovato e aggiornato progetto: {}'.format(n, df_count, codice_locale))

                except DatabaseError as e:
                    transaction.savepoint_rollback(sid)

                    self.logger.error(u'{}/{} - ERRORE progetto {}: {}. Skipping.'.format(n, df_count, codice_locale, e))

            if (n % 5000 == 0) or (n == df_count):
                self.logger.info(u'{} -----------------> Committing.' .format(n))
                transaction.commit()

    @transaction.commit_on_success
    def _import_progetticipe_deliberacipe(self, df):
        df1 = df[df['NUM_DELIBERA'].str.strip() != ''][['NUM_DELIBERA', 'ANNO_DELIBERA', 'DATA_ADOZIONE', 'DATA_PUBBLICAZIONE']].drop_duplicates()
        for index, row in df1.iterrows():
            delibera, created = DeliberaCIPE.objects.get_or_create(
                num=int(row['NUM_DELIBERA']),
                defaults={
                    'anno': self._get_value(row, 'ANNO_DELIBERA'),
                    'data_adozione': self._get_value(row, 'DATA_ADOZIONE', 'date'),
                    'data_pubblicazione': self._get_value(row, 'DATA_PUBBLICAZIONE', 'date'),
                }
            )
            self._log(created, u'Creata delibera: {}'.format(delibera))

    @transaction.commit_manually
    def _import_progetticipe(self, df):
        """
        Procedura per importare dati di progetto, e soggetti, a partire dal tracciato del CIPE
        """

        # df.rename(columns={u'PROGRAMMAZIONE': u'OC_CODICE_PROGRAMMA'}, inplace=True)
        df.rename(columns={u'OC_TIPO_PROGRAMMAZIONE': u'OC_CODICE_PROGRAMMA'}, inplace=True)
        df[u'OC_DESCRIZIONE_PROGRAMMA'] = df[u'OC_CODICE_PROGRAMMA']
        df[u'PO_CODICE_ASSE'] = '00'
        df[u'PO_DENOMINAZIONE_ASSE'] = ''
        df[u'PO_COD_OBIETTIVO_OPERATIVO'] = '00'
        df[u'PO_OBIETTIVO_OPERATIVO'] = ''

        # df[u'CUP_COD_NATURA'] = convert_progetto_cup_cod_natura('3')
        # df[u'CUP_DESCR_NATURA'] = u'REALIZZAZIONE DI LAVORI PUBBLICI (OPERE ED IMPIANTISTICA)'
        df[u'CUP_COD_TIPOLOGIA'] = convert_progetto_cup_cod_tipologia('0')
        df[u'CUP_DESCR_TIPOLOGIA'] = ''

        row_selection = df['COD_DIPE'].isin(['IPS_00099', 'IPS_00100', 'IPS_00109', 'UPS_00014', 'UPS_00024', 'UPS_00026', 'UPS_00027', 'UPS_00028', 'UPS_00047', 'UPS_00069'])
        # df.loc[row_selection, 'CUP_COD_NATURA'] = convert_progetto_cup_cod_natura('1')
        # df.loc[row_selection, 'CUP_DESCR_NATURA'] = u'ACQUISTO DI BENI E SERVIZI'
        df.loc[row_selection, 'CUP_COD_TIPOLOGIA'] = convert_progetto_cup_cod_tipologia('99')
        df.loc[row_selection, 'CUP_DESCR_TIPOLOGIA'] = u'ALTRO'

        df[u'CUP_COD_CATEGORIA'] = convert_progetto_cup_cod_categoria('0')
        df[u'CUP_DESCR_CATEGORIA'] = ''

        df[u'QSN_COD_TEMA_PRIORITARIO_UE'] = convert_progetto_qsn_cod_tema_prioritario_ue('0')
        df[u'QSN_DESCR_TEMA_PRIORITARIO_UE'] = ''

        # df.rename(columns={u'FONDO': u'OC_DESCR_FONTE'}, inplace=True)
        # df[u'OC_COD_FONTE'] = df.apply(lambda row: 'FSC0006' if row['OC_DESCR_FONTE'][-2:] == '06' else ('FSC0713' if row['OC_DESCR_FONTE'][-2:] == '13' else ''), axis=1)

        self._import_progetticipe_deliberacipe(df)
        self._import_progetti_programmaasseobiettivo(df)
        self._import_progetti_classificazioneazione(df)
        self._import_progetti_classificazioneoggetto(df)
        self._import_progetti_tema(df)
        self._import_progetti_fonte(df)

        temisintetici_desc2cod = {tema.descrizione: tema.codice for tema in Tema.objects.principali()}
        fonti_cod2obj = {fonte.codice: fonte for fonte in Fonte.objects.all()}
        stato_desc2cod = {x[1]: x[0] for x in Progetto.STATO}

        # creazione progetti

        gb = df.groupby('COD_DIPE', as_index=False)
        df1 = pd.merge(
            gb.first(),
            gb.aggregate({
                'DATA_PUBBLICAZIONE': 'max',
                'ASSEGNAZIONE_CIPE': lambda x: x.str.replace(',', '.').astype(float).sum(),
                'NOTE': lambda x: '\n'.join(x.tolist()),
            }),
            left_on='COD_DIPE',
            right_on='COD_DIPE',
            suffixes=('', '_AGG'),
        )

        df_count = len(df1)

        for n, (index, row) in enumerate(df1.iterrows(), 1):
            # codice locale (ID del record)
            codice_locale = row['COD_DIPE']

            try:
                values = {}

                values['codice_locale'] = codice_locale

                values['titolo_progetto'] = row['OC_TITOLO_PROGETTO']

                #values['active_flag'] = row['FLAG_ATTIVO']
                values['cipe_flag'] = True

                values['programma_asse_obiettivo_id'] = '{}/{}/{}'.format(row['OC_CODICE_PROGRAMMA'], row['PO_CODICE_ASSE'], row['PO_COD_OBIETTIVO_OPERATIVO'])

                values['classificazione_azione_id'] = '{}.{}'.format(row['CUP_COD_NATURA'], row['CUP_COD_TIPOLOGIA'])

                values['classificazione_oggetto_id'] = '{}.{}.{}'.format(row['CUP_COD_SETTORE'], row['CUP_COD_SOTTOSETTORE'], row['CUP_COD_CATEGORIA'])

                values['tema_id'] = '{}.{}'.format(temisintetici_desc2cod[row['OC_TEMA_SINTETICO']], row['QSN_COD_TEMA_PRIORITARIO_UE'])

                values['cup'] = row['CUP'][0] if row['CUP'] else ''

                # totale finanziamento
                values['fin_totale_pubblico'] = self._get_value(row, 'ASSEGNAZIONE_CIPE_AGG', 'decimal')

                values['note'] = self._get_value(row, 'NOTE_AGG')

                values['costo'] = self._get_value(row, 'COSTO', 'decimal')

                # data ultimo aggiornamento progetto
                values['data_aggiornamento'] = self._get_value(row, 'DATA_PUBBLICAZIONE_AGG', 'date')

                values['stato_progetto'] = stato_desc2cod.get(row['OC_STATO_PROGETTO'])
                values['stato_finanziario'] = stato_desc2cod.get(row['OC_STATO_FINANZIARIO'])

                values['dps_flag_cup'] = 1

                values['csv_data'] = json.dumps(OrderedDict(row), ensure_ascii=False, sort_keys=True)

            except ValueError as e:
                self.logger.error(u'{}/{} - {}: {}. Skipping'.format(n, df_count, codice_locale, e))

            else:
                try:
                    sid = transaction.savepoint()

                    progetto = Progetto.fullobjects.create(**values)

                    progetto.fonte_set.add(fonti_cod2obj[row['OC_COD_FONTE']])

                    for cup in row['CUP']:
                        progetto.cups_progetto.create(cup=cup)

                    transaction.savepoint_commit(sid)

                    del progetto

                    self.logger.info(u'{}/{} - Creato progetto: {}'.format(n, df_count, codice_locale))

                except DatabaseError as e:
                    transaction.savepoint_rollback(sid)

                    self.logger.error(u'{}/{} - ERRORE progetto {}: {}. Skipping.'.format(n, df_count, codice_locale, e))

            if (n % 5000 == 0) or (n == df_count):
                self.logger.info(u'{} -----------------> Committing.' .format(n))
                transaction.commit()

        # associazione di delibere a progetti

        progetticipe_cod2obj = {o.codice_locale: o for o in Progetto.fullobjects.filter(cipe_flag=True)}
        delibere_num2obj = {o.num: o for o in DeliberaCIPE.objects.all()}

        df_count = len(df)

        for n, (index, row) in enumerate(df.iterrows(), 1):
            progetto = progetticipe_cod2obj[row['COD_DIPE']]
            delibera = delibere_num2obj[int(row['NUM_DELIBERA'])]

            ProgettoDeliberaCIPE.objects.create(
                progetto=progetto,
                delibera=delibera,
                finanziamento=self._get_value(row, 'ASSEGNAZIONE_CIPE', 'decimal'),
                note=self._get_value(row, 'NOTE') or '',
            )

            self.logger.info(u'{}/{} - Delibera {} associata a progetto: {}'.format(n, df_count, delibera, progetto))

            if (n % 5000 == 0) or (n == df_count):
                self.logger.info(u'{} -----------------> Committing.' .format(n))
                transaction.commit()

        # # soggetti e ruoli
        #
        # for col, role in {'SOGGETTO_RESPONSABILE': Ruolo.RUOLO.programmatore, 'SOGGETTO_ATTUATORE': Ruolo.RUOLO.attuatore}.iteritems():
        #     df1 = df[df[col].str.strip() != ''][[col, 'COD_DIPE']].drop_duplicates().groupby(col, as_index=False)['COD_DIPE'].aggregate(lambda x: x.tolist())
        #
        #     df_count = len(df1)
        #
        #     for n, (index, row) in enumerate(df1.iterrows(), 1):
        #         denominazione = row[col].strip()
        #
        #         soggetto, created = Soggetto.objects.get_or_create(
        #             denominazione__iexact=denominazione,
        #             codice_fiscale='',
        #             defaults={'denominazione': denominazione}
        #         )
        #         self._log(created, u'{}/{} - Creato soggetto: {}'.format(n, df_count, soggetto))
        #
        #         role_count = len(row['COD_DIPE'])
        #
        #         for nn, codice_locale in enumerate(row['COD_DIPE'], 1):
        #             ruolo = Ruolo.objects.create(
        #                 progetto_id=codice_locale,
        #                 soggetto=soggetto,
        #                 ruolo=role,
        #             )
        #             self.logger.info(u'{}/{} ({}/{}) - Creato ruolo: {}'.format(n, df_count, nn, role_count, ruolo))
        #
        #     self.logger.info(u'{} -----------------> Committing.' .format(col))
        #     transaction.commit()

    # @transaction.commit_on_success
    # def _import_soggetti_formagiuridica(self, df):
    #     df1 = df[['COD_FORMA_GIURIDICA_SOGG', 'DESCR_FORMA_GIURIDICA_SOGG']].drop_duplicates()
    #     for index, row in df1.iterrows():
    #         forma_giuridica, created = FormaGiuridica.objects.get_or_create(
    #             codice=self._get_value(row, 'COD_FORMA_GIURIDICA_SOGG'),
    #             defaults={
    #                 'denominazione': self._get_value(row, 'DESCR_FORMA_GIURIDICA_SOGG'),
    #             }
    #         )
    #         self._log(created, u'Creata forma giuridica: {} ({})'.format(forma_giuridica.denominazione, forma_giuridica.codice))

    # @transaction.commit_on_success
    # def _import_soggetti_codiceateco(self, df):
    #     df1 = df[['COD_ATECO_SOGG', 'DESCRIZIONE_ATECO_SOGG']].drop_duplicates()
    #     for index, row in df1.iterrows():
    #         codice_ateco, created = CodiceAteco.objects.get_or_create(
    #             codice=self._get_value(row, 'COD_ATECO_SOGG'),
    #             defaults={
    #                 'descrizione': self._get_value(row, 'DESCRIZIONE_ATECO_SOGG'),
    #             }
    #         )
    #         self._log(created, u'Creato codice ateco: {} ({})'.format(codice_ateco.descrizione, codice_ateco.codice))

    @transaction.commit_manually
    def _import_soggetti(self, df):
        df['COD_LOCALE_PROGETTO'] = df.apply(lambda r: r['COD_LOCALE_PROGETTO'] or r['COD_DIPE'], axis=1)

        # self._import_soggetti_formagiuridica(df)
        # self._import_soggetti_codiceateco(df)

        # creazione soggetti

        # df1 = df[['OC_DENOMINAZIONE_SOGG', 'OC_CODICE_FISCALE_SOGG', 'COD_FORMA_GIURIDICA_SOGG', 'COD_ATECO_SOGG', 'COD_COMUNE_SEDE_SOGG', 'INDIRIZZO_SOGG', 'CAP_SOGG']].drop_duplicates()
        # df1 = df[['OC_DENOMINAZIONE_SOGG', 'OC_CODICE_FISCALE_SOGG', 'COD_COMUNE_SEDE_SOGG', 'INDIRIZZO_SOGG', 'CAP_SOGG']].drop_duplicates()
        df1 = df.groupby(['OC_DENOMINAZIONE_SOGG', 'OC_CODICE_FISCALE_SOGG'], as_index=False).first()

        df_count = len(df1)

        for n, (index, row) in enumerate(df1.iterrows(), 1):
            denominazione = row['OC_DENOMINAZIONE_SOGG'].strip()
            codice_fiscale = row['OC_CODICE_FISCALE_SOGG'].strip()

            try:
                territorio = Territorio.objects.get_from_istat_code(row['COD_COMUNE_SEDE_SOGG'])
            except ObjectDoesNotExist:
                territorio = None

            try:
                sid = transaction.savepoint()

                Soggetto.objects.create(
                    denominazione=denominazione,
                    codice_fiscale=codice_fiscale,
                    # forma_giuridica_id=self._get_value(row, 'COD_FORMA_GIURIDICA_SOGG'),
                    # codice_ateco_id=self._get_value(row, 'COD_ATECO_SOGG'),
                    indirizzo=self._get_value(row, 'INDIRIZZO_SOGG'),
                    cap=self._get_value(row, 'CAP_SOGG'),
                    territorio=territorio,
                )

                transaction.savepoint_commit(sid)

                self.logger.info(u'{}/{} - Creato soggetto: {} ({})'.format(n, df_count, denominazione, codice_fiscale))

            except DatabaseError as e:
                transaction.savepoint_rollback(sid)

                self.logger.error(u'{}/{} - ERRORE soggetto {} ({}): {}. Skipping.'.format(n, df_count, denominazione, codice_fiscale, e))

            if (n % 5000 == 0) or (n == df_count):
                self.logger.info(u'{} -----------------> Committing.'.format(n))
                transaction.commit()

        # creazione ruoli

        # df1 = df[['COD_LOCALE_PROGETTO', 'OC_DENOMINAZIONE_SOGG', 'OC_CODICE_FISCALE_SOGG', 'SOGG_COD_RUOLO', 'SOGG_PROGR_RUOLO']].drop_duplicates()
        df1 = df.groupby(['COD_LOCALE_PROGETTO', 'OC_DENOMINAZIONE_SOGG', 'OC_CODICE_FISCALE_SOGG', 'SOGG_COD_RUOLO'], as_index=False).first()

        df_count = len(df1)

        for n, (index, row) in enumerate(df1.iterrows(), 1):
            try:
                progetto = Progetto.fullobjects.get(codice_locale=row['COD_LOCALE_PROGETTO'])
                self.logger.debug(u'{}/{} - Progetto: {}'.format(n, df_count, progetto))

            except ObjectDoesNotExist:
                self.logger.warning(u'{}/{} - Progetto non trovato: {}. Skipping.'.format(n, df_count, row['COD_LOCALE_PROGETTO']))

            else:
                denominazione = row['OC_DENOMINAZIONE_SOGG'].strip()
                codice_fiscale = row['OC_CODICE_FISCALE_SOGG'].strip()

                try:
                    soggetto = Soggetto.objects.get(denominazione=denominazione, codice_fiscale=codice_fiscale)
                    self.logger.debug(u'{}/{} - Soggetto: {} ({})'.format(n, df_count, soggetto.denominazione, soggetto.codice_fiscale))

                except ObjectDoesNotExist:
                    self.logger.warning(u'{}/{} - Soggetto non trovato: {} ({}). Skipping.'.format(n, df_count, denominazione, codice_fiscale))

                else:
                    ruolo = Ruolo(
                        progetto=progetto,
                        soggetto=soggetto,
                        ruolo=row['SOGG_COD_RUOLO'],
                        progressivo_ruolo=row['SOGG_PROGR_RUOLO'],
                    )

                    try:
                        sid = transaction.savepoint()
                        ruolo.save()
                        transaction.savepoint_commit(sid)

                        self.logger.info(u'{}/{} - Creato ruolo: {}'.format(n, df_count, ruolo))
                    except DatabaseError as e:
                        transaction.savepoint_rollback(sid)

                        self.logger.error(u'{}/{} - ERRORE ruolo {}: {}. Skipping.'.format(n, df_count, ruolo, e))

                    del progetto
                    del soggetto
                    del ruolo

            if (n % 5000 == 0) or (n == df_count):
                self.logger.info(u'{} -----------------> Committing.'.format(n))
                transaction.commit()

    @transaction.commit_on_success
    def _import_localizzazioni_territori(self, df):
        keywords = ['OC_TERRITORIO_PROG', 'COD_REGIONE', 'DEN_REGIONE']

        # only complete and non-empty classifications are created
        if all(k in df.columns.values for k in keywords):
            df1 = df[df['OC_TERRITORIO_PROG'].isin([Territorio.TERRITORIO.E, Territorio.TERRITORIO.N])][keywords].drop_duplicates()
            for index, row in df1.iterrows():
                territorio, created = Territorio.objects.get_or_create(
                    cod_reg=int(row['COD_REGIONE']),
                    cod_prov=0,
                    cod_com=0,
                    territorio=row['OC_TERRITORIO_PROG'],
                    defaults={
                        'denominazione': row['DEN_REGIONE']
                    }
                )
                self._log(created, u'Creato territorio: {} ({})'.format(territorio, territorio.territorio))

    def _import_localizzazioni(self, df):
        # i territori esteri o nazionali non sono in Territorio di default
        self._import_localizzazioni_territori(df)

        df_count = len(df)

        insert_list = []

        for n, (index, row) in enumerate(df.iterrows(), 1):
            codice_locale_progetto = row['COD_LOCALE_PROGETTO'] or row['COD_DIPE']

            try:
                progetto = Progetto.fullobjects.get(codice_locale=codice_locale_progetto)

                self.logger.debug(u'{}/{} - Progetto: {}'.format(n, df_count, progetto))

            except ObjectDoesNotExist:
                self.logger.warning(u'{}/{} - Progetto non trovato: {}. Skipping.'.format(n, df_count, codice_locale_progetto))

            else:
                territorio = None

                tipo_territorio = self._get_value(row, 'OC_TERRITORIO_PROG')

                # # per i progetti CIPE non c'è il campo OC_TERRITORIO_PROG
                # if not tipo_territorio:
                #     if row['COD_PROVINCIA'] in ('000', '900'):
                #         tipo_territorio = Territorio.TERRITORIO.R
                #     elif row['COD_COMUNE'] in ('000', '900'):
                #         tipo_territorio = Territorio.TERRITORIO.P
                #     else:
                #         tipo_territorio = Territorio.TERRITORIO.C

                if not tipo_territorio in (Territorio.TERRITORIO.E, Territorio.TERRITORIO.N):
                    if row['COD_PROVINCIA'] in ('000', '900'):
                        tipo_territorio = Territorio.TERRITORIO.R
                    elif row['COD_COMUNE'] in ('000', '900'):
                        tipo_territorio = Territorio.TERRITORIO.P

                if not tipo_territorio in dict(Territorio.TERRITORIO):
                    self.logger.warning(u'{}/{} - Tipo di territorio sconosciuto o errato: {}. Skipping.'.format(n, df_count, tipo_territorio))

                else:
                    lookup = {}
                    lookup['territorio'] = tipo_territorio
                    lookup['cod_reg'] = int(row['COD_REGIONE'])

                    if tipo_territorio == Territorio.TERRITORIO.R:
                        pass
                    elif tipo_territorio == Territorio.TERRITORIO.P:
                        lookup['cod_prov'] = int(row['COD_PROVINCIA'])
                    elif tipo_territorio == Territorio.TERRITORIO.C:
                        lookup['cod_prov'] = int(row['COD_PROVINCIA'])
                        lookup['cod_com'] = '{}{}'.format(int(row['COD_PROVINCIA']), row['COD_COMUNE'])
                    else:
                        lookup['cod_prov'] = 0
                        lookup['cod_com'] = 0

                    try:
                        territorio = Territorio.objects.get(**lookup)

                        self.logger.debug(u'{}/{} - Territorio: {}'.format(n, df_count, territorio))

                    except ObjectDoesNotExist:
                        if tipo_territorio == Territorio.TERRITORIO.C:
                            del lookup['cod_prov']
                            del lookup['cod_com']

                            lookup['denominazione'] = row['DEN_COMUNE']

                            try:
                                territorio = Territorio.objects.get(**lookup)
                                self.logger.debug(u'{}/{} - Territorio di tipo "Comune" individuato attraverso la denominazione: {}.'.format(n, df_count, territorio))
                            except ObjectDoesNotExist:
                                pass

                    if not territorio:
                        self.logger.warning(u'{}/{} - Territorio non trovato: {} [{}]/{} [{}]/{} [{}] ({}). Skipping.'.format(n, df_count, row['DEN_COMUNE'], row['COD_COMUNE'], row['DEN_PROVINCIA'], row['COD_PROVINCIA'], row['DEN_REGIONE'], row['COD_REGIONE'], tipo_territorio))

                if territorio:
                    insert_list.append(
                        Localizzazione(
                            progetto=progetto,
                            territorio=territorio,
                            indirizzo=self._get_value(row, 'INDIRIZZO_PROG'),
                            cap=self._get_value(row, 'CAP_PROG'),
                            dps_flag_cap=int(self._get_value(row, 'OC_FLAG_CAP_PROG') or 0),
                        )
                    )
                    self.logger.info(u'{}/{} - Creata localizzazione progetto: {}'.format(n, df_count, insert_list[-1]))

                    del progetto
                    del territorio

            if (n % 5000 == 0) or (n == df_count):
                self.logger.info(u'{}/{} -----------------> Salvataggio in corso.'.format(n, df_count))
                Localizzazione.objects.bulk_create(insert_list)
                insert_list = []

    def _import_pagamenti(self, df):
        df = df[df['TOT_PAGAMENTI'].str.strip() != '']

        df_count = len(df)

        insert_list = []

        created = 0

        for n, (index, row) in enumerate(df.iterrows(), 1):
            try:
                progetto = Progetto.fullobjects.get(codice_locale=row['COD_LOCALE_PROGETTO'])

                self.logger.debug(u'{}/{} - Progetto: {}'.format(n, df_count, progetto))

            except ObjectDoesNotExist:
                self.logger.warning(u'{}/{} - Progetto non trovato: {}. Skipping.'.format(n, df_count, row['COD_LOCALE_PROGETTO']))

            else:
                insert_list.append(
                    PagamentoProgetto(
                        progetto=progetto,
                        data=self._get_value(row, 'DATA_AGGIORNAMENTO', 'date'),
                        ammontare=self._get_value(row, 'TOT_PAGAMENTI', 'decimal'),
                        ammontare_fsc=self._get_value(row, 'OC_TOT_PAGAMENTI_FSC', 'decimal'),
                        ammontare_pac=self._get_value(row, 'OC_TOT_PAGAMENTI_PAC', 'decimal'),
                        ammontare_rendicontabile_ue=self._get_value(row, 'OC_TOT_PAGAMENTI_RENDICONTAB_UE', 'decimal'),
                    )
                )
                self.logger.info(u'{}/{} - Creato pagamento: {}'.format(n, df_count, insert_list[-1]))

                del progetto

                created += 1

            if (n % 5000 == 0) or (n == df_count):
                self.logger.info(u'{}/{} -----------------> Salvataggio in corso.'.format(n, df_count))
                PagamentoProgetto.objects.bulk_create(insert_list)
                insert_list = []

        self.logger.info(u'Sono stati creati {} pagamenti su {}.'.format(created, df_count))

    def _update_privacy_progetti(self, df):
        df_count = len(df)

        ids = []
        tot_updated = 0

        for n, (index, row) in enumerate(df.iterrows(), 1):
            ids.append(row['COD_LOCALE_PROGETTO'])

            if (n % 5000 == 0) or (n == df_count):
                self.logger.info(u'{}/{} - Aggiornamento del flag privacy in corso ....' .format(n, df_count))
                updated = Progetto.fullobjects.filter(codice_locale__in=ids).update(privacy_flag=True)
                self.logger.info(u'{}/{} - Fatto. Record aggiornati: {}.'.format(n, df_count, updated))

                ids = []
                tot_updated += updated

        self.logger.info(u'Totale record aggiornati: {}.'.format(tot_updated))

    @transaction.commit_on_success
    def _update_privacy_soggetti(self, df):
        df_count = len(df)

        tot_updated = 0

        for n, (index, row) in enumerate(df.iterrows(), 1):
            try:
                soggetto = Soggetto.objects.get(ruolo__progetto__codice_locale=row['COD_LOCALE_PROGETTO'], ruolo__ruolo=row['SOGG_COD_RUOLO'], ruolo__progressivo_ruolo=row['SOGG_PROGR_RUOLO'])
                self.logger.debug(u'{}/{} - Soggetto: {}'.format(n, df_count, soggetto))
            except ObjectDoesNotExist:
                self.logger.warning(u'{}/{} - Soggetto non trovato: {}/{}/{}. Skipping.'.format(n, df_count, row['COD_LOCALE_PROGETTO'], row['SOGG_COD_RUOLO'], row['SOGG_PROGR_RUOLO']))
            except MultipleObjectsReturned:
                self.logger.warning(u'{}/{} - Più di un soggetto trovato: {}/{}/{}. Skipping.'.format(n, df_count, row['COD_LOCALE_PROGETTO'], row['SOGG_COD_RUOLO'], row['SOGG_PROGR_RUOLO']))
            else:
                soggetto.privacy_flag = True
                soggetto.save()
                tot_updated += 1

        self.logger.info(u'Totale record aggiornati: {}.'.format(tot_updated))

    def _log(self, created, msg):
        if created:
            self.logger.info(msg)
        else:
            self.logger.debug(msg.replace('Creat', 'Trovat'))

    @staticmethod
    def _get_value(dict, key, type='string'):
        if key in dict:
            value = unicode(dict[key]).strip()
            if value:
                if type == 'decimal':
                    value = Decimal(value.replace(',', '.'))
                elif type == 'date':
                    value = datetime.datetime.strptime(value, '%Y%m%d')

                return value

        return None
