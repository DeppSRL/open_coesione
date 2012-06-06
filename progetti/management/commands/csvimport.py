# -*- coding: utf-8 -*-
from decimal import Decimal
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import DatabaseError
from os import path
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from optparse import make_option

import csv
import logging


from progetti.models import *
from localita.models import Localita


class Command(BaseCommand):
    """
    Poiticians anagraphical data and their current and past charges are imported from the
    openpolitici database.

    An openpolis location id MUST be passed along to specify the location.

    Data may be compared or re-written. By default they're compared,
    to overwrite use the --overwrite option.
    """
    help = "Import data from csv"

    option_list = BaseCommand.option_list + (
        make_option('--csv-file',
                    dest='csvfile',
                    default='./progetti.csv',
                    help='Select csv file'),
        make_option('--type',
                    dest='type',
                    default='proj',
                    help='Type of import: proj|loc|rec'),
        make_option('--limit',
                    dest='limit',
                    default=0,
                    help='Limit of records to import'),
        make_option('--offset',
                    dest='offset',
                    default=0,
                    help='Offset of records to import'),
        make_option('--delete',
                    dest='delete',
                    action='store_true',
                    help='Delete project records, before importing'),
    )

    csv_file = ''
    logger = logging.getLogger('csvimport')
    reader = None

    def handle(self, *args, **options):
        self.csv_file = options['csvfile']

        # read first csv file
        try:
            self.reader = csv.DictReader(open(self.csv_file, 'U'), delimiter=';', )
        except IOError:
            self.logger.error("It was impossible to open file %s" % self.csv_file)
            exit(1)
        except csv.Error, e:
            self.logger.error("CSV error while reading %s: %s" % (self.csv_file, e.message))

        if options['type'] == 'proj':
            self.handle_proj(*args, **options)
        elif options['type'] == 'loc':
            self.handle_loc(*args, **options)
        elif options['type'] == 'rec':
            self.handle_rec(*args, **options)
        else:
            self.logger.error("Wrong type %s. Select among proj, loc and rec." % options['type'])
            exit(1)



    def handle_rec(self, *args, **options):
        self.logger.info("Inizio import da %s" % self.csv_file)
        self.logger.info("Limit: %s" % options['limit'])
        self.logger.info("Offset: %s" % options['offset'])

        # check whether to remove records
        if options['delete']:
            Soggetto.objects.all().delete()
            self.logger.info("Oggetti rimossi")


        for c, r in enumerate(self.reader):
            if c < int(options['offset']):
                continue

            # codice locale progetto (ID del record)
            try:
                progetto = Progetto.objects.get(pk=r['COD_LOCALE_PROGETTO'])
                self.logger.debug("%s - Progetto: %s" % (c, progetto.codice_locale))
            except ObjectDoesNotExist:
                progetto = None
                self.logger.warning("%s - Progetto non trovato: %s" % (c, r['COD_LOCALE_PROGETTO']))

            if progetto:
                created = False
                soggetto, created = Soggetto.objects.get_or_create(
                    codice_fiscale=r['DPS_CODICE_FISCALE_SOG'],
                    defaults={
                        'denominazione': r['DPS_DENOMINAZIONE_SOG'].strip(),
                        'ruolo': r['COD_RUOLO_SOG']
                    }
                )
                if created:
                    self.logger.info("Aggiunto soggetto: %s" % (soggetto.denominazione,))

                progetto.soggetto_set.add(soggetto)


            if int(options['limit']) and\
               (c - int(options['offset']) > int(options['limit'])):
                break

        self.logger.info("Fine")


    def handle_loc(self, *args, **options):
        self.logger.info("Inizio import da %s" % self.csv_file)
        self.logger.info("Limit: %s" % options['limit'])
        self.logger.info("Offset: %s" % options['offset'])

        # check whether to remove records
        if options['delete']:
            Localizzazione.objects.all().delete()
            self.logger.info("Oggetti rimossi")


        for c, r in enumerate(self.reader):
            if c < int(options['offset']):
                continue

            tipo_territorio = r['dps_territorio']

            if tipo_territorio == Localita.TERRITORIO.R:
                localita = Localita.objects.get(
                    cod_reg=r['CODICE_REGIONE'],
                    territorio=Localita.TERRITORIO.R,
                )
            elif tipo_territorio == 'P':
                localita = Localita.objects.get(
                    cod_reg=r['CODICE_REGIONE'],
                    cod_prov=r['CODICE_PROVINCIA'],
                    territorio=Localita.TERRITORIO.P,
                )
            elif tipo_territorio == 'C':
                localita = Localita.objects.get(
                    cod_reg=r['CODICE_REGIONE'],
                    cod_prov=r['CODICE_PROVINCIA'],
                    cod_com=r['CODICE_COMUNE'],
                    territorio=Localita.TERRITORIO.P,
                )
            elif tipo_territorio in ('E', 'N'):
                # territorio estero o nazionale
                # get_or_create, perché non sono in Localita di default
                created = False
                codice_localita = r['CODICE_REGIONE']
                localita, created = Localita.objects.get_or_create(
                    cod_reg=codice_localita,
                    cod_prov='000',
                    cod_com='000',
                    territorio=tipo_territorio,
                    defaults={
                        'denominazione': r['DENOMINAZIONE_REGIONE']
                    }
                )
                if created:
                    self.logger.info("Aggiunto territorio di tipo %s: %s" % (tipo_territorio, localita.denominazione))
            else:
                self.logger.warning('Tipo di territorio sconosciuto o errato %s. Skip.' % (tipo_territorio,))
                continue

            # codice locale progetto (ID del record)
            try:
                progetto = Progetto.objects.get(pk=r['COD_LOCALE_PROGETTO'])
                self.logger.debug("%s - Progetto: %s" % (c, progetto.codice_locale))
            except ObjectDoesNotExist:
                progetto = None
                self.logger.warning("%s - Progetto non trovato: %s" % (c, r['COD_LOCALE_PROGETTO']))

            if progetto:
                created = False
                localizzazione, created = progetto.localizzazione_set.get_or_create(
                    localita=localita,
                    progetto = progetto,
                    defaults={
                        'indirizzo': r['INDIRIZZO'].strip(),
                        'cap': r['COD_CAP'].strip(),
                        'dps_flag_cap': r['dps_flag_cap']
                    }
                )
                if created:
                    self.logger.info("Aggiunta localizzazione progetto: %s" % (localizzazione,))

            if int(options['limit']) and\
               (c - int(options['offset']) > int(options['limit'])):
                break

        self.logger.info("Fine")


    def handle_proj(self, *args, **options):
        self.logger.info("Inizio import da %s" % self.csv_file)
        self.logger.info("Limit: %s" % options['limit'])
        self.logger.info("Offset: %s" % options['offset'])

        # check whether to remove records
        if options['delete']:
            Progetto.objects.all().delete()
            ProgrammaAsseObiettivo.objects.all().delete()
            ClassificazioneQSN.objects.all().delete()
            ClassificazioneAzione.objects.all().delete()
            ClassificazioneOggetto.objects.all().delete()
            Tema.objects.exclude(tipo_tema='sintetico').delete()
            self.logger.info("Oggetti rimossi")


        for c, r in enumerate(self.reader):
            if c < int(options['offset']):
                continue

            # codice locale (ID del record)
            codice_locale = r['COD_LOCALE_PROGETTO']


            # classificazione QSN
            if r['COD_PRIORITA_QSN'].strip():
                created = False
                codice_priorita_qsn = r['COD_PRIORITA_QSN']
                priorita_qsn, created = ClassificazioneQSN.objects.get_or_create(
                    codice=codice_priorita_qsn,
                    tipo_classificazione=ClassificazioneQSN.TIPO.priorita,
                    defaults={
                        'descrizione': r['DESCRIZIONE_PRIORITA_QSN']
                    }
                )
                if created:
                    self.logger.info("Aggiunta priorità QSN: %s" % priorita_qsn.codice)

                created = False
                obiettivo_generale_qsn, created = ClassificazioneQSN.objects.get_or_create(
                    codice=r['COD_OBIETTIVO_GENERALE_QSN'],
                    tipo_classificazione=ClassificazioneQSN.TIPO.generale,
                    defaults={
                        'descrizione': r['DESCR_OBIETTIVO_GENERALE_QSN'],
                        'classificazione_superiore': priorita_qsn
                    }
                )
                if created:
                    self.logger.info("Aggiunto obiettivo generale QSN: %s (%s)" %
                                      (obiettivo_generale_qsn.codice, priorita_qsn.codice))

                created = False
                obiettivo_specifico_qsn, created = ClassificazioneQSN.objects.get_or_create(
                    codice=r['CODICE_OBIETTIVO_SPECIFICO_QSN'],
                    tipo_classificazione=ClassificazioneQSN.TIPO.specifico,
                    defaults={
                        'descrizione': r['DESCR_OBIETTIVO_SPECIFICO_QSN'],
                        'classificazione_superiore': obiettivo_generale_qsn
                    }
                )
                if created:
                    self.logger.info("Aggiunto obiettivo specifico QSN: %s (%s - %s)" %
                                      (obiettivo_specifico_qsn.codice, obiettivo_generale_qsn.codice, priorita_qsn.codice))
            else:
                obiettivo_specifico_qsn = None

            # status
            stato_fs = r['STATO_FS'] if r['STATO_FS'].strip() else None
            stato_fsc = r['STATO_FSC'] if r['STATO_FSC'].strip() else None
            stato_dps = r['DPS_STATO'] if r['DPS_STATO'].strip() else None

            # obiettivo sviluppo
            if r['OBIETTIVO_SVILUPPO'].strip():
                try:
                    obiettivo_sviluppo = [k for k, v in dict(Progetto.OBIETTIVO_SVILUPPO).iteritems() if v == r['OBIETTIVO_SVILUPPO']][0]
                except IndexError as e:
                    self.logger.error("While reading obiettivo sviluppo %s in %s. %s" % (r['OBIETTIVO_SVILUPPO'], codice_locale, e))
                    continue
            else:
                obiettivo_sviluppo = ''

            # fondo comunitario
            if r['FONDO_COMUNITARIO'].strip():
                try:
                    fondo_comunitario = [k for k, v in dict(Progetto.FONDO_COMUNITARIO).iteritems() if v == r['FONDO_COMUNITARIO']][0]
                except IndexError as e:
                    self.logger.error("While reading fondo comunitario %s in %s. %s" % (r['FONDO_COMUNITARIO'], codice_locale, e))
                    continue
            else:
                fondo_comunitario = None

            # programma, asse, obiettivo
            try:
                created = False
                programma, created = ProgrammaAsseObiettivo.objects.get_or_create(
                    codice=r['COD_PROGRAMMA_FS'],
                    tipo_classificazione=ProgrammaAsseObiettivo.TIPO.programma,
                    defaults={
                        'descrizione':r['DPS_DESCRIZIONE_PROGRAMMA'].decode('iso-8859-1')
                    }
                )
                if created:
                    self.logger.info("Aggiunto programma FS: %s" % (programma.codice,))

                created = False
                programma_asse, created = ProgrammaAsseObiettivo.objects.get_or_create(
                    codice="%s/%s" % (r['COD_PROGRAMMA_FS'], r['CODICE_ASSE']),
                    tipo_classificazione=ProgrammaAsseObiettivo.TIPO.asse,
                    defaults={
                        'descrizione':r['DENOMINAZIONE_ASSE'],
                        'classificazione_superiore': programma
                    }
                )
                if created:
                    self.logger.info("Aggiunto asse: %s" % (programma_asse.codice,))

                created = False
                programma_asse_obiettivo, created = ProgrammaAsseObiettivo.objects.get_or_create(
                    codice="%s/%s/%s" % (r['COD_PROGRAMMA_FS'], r['CODICE_ASSE'], r['COD_OBIETTIVO_OPERATIVO']),
                    tipo_classificazione=ProgrammaAsseObiettivo.TIPO.obiettivo,
                    defaults={
                        'descrizione':r['OBIETTIVO_OPERATIVO'],
                        'classificazione_superiore': programma_asse
                    }
                )
                if created:
                    self.logger.debug("Aggiunto obiettivo: %s" % (programma_asse_obiettivo.codice,))

            except DatabaseError as e:
                self.logger.error("In fetch di programma-asse-obiettivo per codice locale:%s. %s" % (codice_locale, e))
                continue

            # data ultimo aggiornamento progetto
            if r['DATA_AGGIORNAMENTO'].strip():
                data_aggiornamento = datetime.datetime.strptime(r['DATA_AGGIORNAMENTO'], '%m/%Y')
            else:
                data_aggiornamento = None

            # tipo operazione
            if r['COD_TIPO_OPERAZIONE'].strip():
                tipo_operazione = r['COD_TIPO_OPERAZIONE']
            else:
                self.logger.warning("Empty tipo operazione in %s" % (codice_locale,))
                tipo_operazione = None

            # tema
            try:
                tema_sintetico = Tema.objects.get(
                    descrizione=r['DPS_TEMA_SINTETICO'],
                    tipo_tema=Tema.TIPO.sintetico,
                )
            except ObjectDoesNotExist as e:
                self.logger.error("While reading tema sintetico %s in %s. %s" % (r['DPS_TEMA_SINTETICO'], codice_locale, e))
                continue

            try:
                created = False
                tema_prioritario, created = Tema.objects.get_or_create(
                    codice="%s.%s" % (tema_sintetico.codice, r['COD_TEMA_PRIORITARIO']),
                    tipo_tema=Tema.TIPO.prioritario,
                    defaults={
                        'descrizione': r['DESCR_TEMA_PRIORITARIO'],
                        'tema_superiore': tema_sintetico,
                    }
                )
                if created:
                    self.logger.info("Aggiunto tema: %s" % (tema_prioritario.codice,))

            except DatabaseError as e:
                self.logger.error("In fetch di tema prioritario %s per codice locale:%s. %s" %
                             (r['COD_TEMA_PRIORITARIO'], codice_locale, e))
                continue


            # intesa (strumento attuatore per fondi FSC ex-FAS)
            try:
                created = False
                intesa, created = Intesa.objects.get_or_create(
                    codice="%s" % (r['COD_INTESA']),
                    defaults={
                        'descrizione': r['DESCRIZIONE_INTESA'],
                        }
                )
                if created:
                    self.logger.info("Aggiunta intesa: %s" % (intesa,))

            except DatabaseError as e:
                self.logger.error("In fetch di intesa %s per codice locale:%s. %s" %
                             (r['COD_INTESA'], codice_locale, e))
                continue


            # classificazione azione
            try:
                created = False
                natura, created = ClassificazioneAzione.objects.get_or_create(
                    codice=r['COD_NATURA'],
                    tipo_classificazione=ClassificazioneAzione.TIPO.natura,
                    defaults={
                        'descrizione':r['DESCR_NATURA']
                    }
                )
                if created:
                    self.logger.info("Aggiunta classificazione azione natura: %s" % (natura.codice,))

                created = False
                natura_tipologia, created = ClassificazioneAzione.objects.get_or_create(
                    codice="%s.%s" % (r['COD_NATURA'], r['COD_TIPOLOGIA']),
                    tipo_classificazione=ClassificazioneAzione.TIPO.tipologia,
                    defaults={
                        'descrizione':r['DESCR_TIPOLOGIA'],
                        'classificazione_superiore': natura
                    }
                )
                if created:
                    self.logger.info("Aggiunta classificazione azione natura_tipologia: %s" % (natura_tipologia.codice,))


            except DatabaseError as e:
                self.logger.error("In fetch di natura-tipologia per codice locale:%s. %s" % (codice_locale, e))
                continue

            # classificazione oggetto
            try:
                created = False
                settore, created = ClassificazioneOggetto.objects.get_or_create(
                    codice=r['COD_SETTORE'],
                    tipo_classificazione=ClassificazioneOggetto.TIPO.settore,
                    defaults={
                        'descrizione':r['DESCR_SETTORE']
                    }
                )
                if created:
                    self.logger.info("Aggiunta classificazione oggetto settore: %s" % (settore.codice,))

                created = False
                settore_sottosettore, created = ClassificazioneOggetto.objects.get_or_create(
                    codice="%s.%s" % (r['COD_SETTORE'], r['COD_SOTTOSETTORE']),
                    tipo_classificazione=ClassificazioneOggetto.TIPO.sottosettore,
                    defaults={
                        'descrizione':r['DESCR_SOTTOSETTORE'],
                        'classificazione_superiore': settore
                    }
                )
                if created:
                    self.logger.info("Aggiunta classificazione oggetto settore_sottosettore: %s" %
                                (settore_sottosettore.codice,))

                created = False
                settore_sottosettore_categoria, created = ClassificazioneOggetto.objects.get_or_create(
                    codice="%s.%s.%s" % (r['COD_SETTORE'], r['COD_SOTTOSETTORE'], r['COD_CATEGORIA']),
                    tipo_classificazione=ClassificazioneOggetto.TIPO.categoria,
                    defaults={
                        'descrizione':r['DESCR_CATEGORIA'],
                        'classificazione_superiore': settore_sottosettore
                    }
                )
                if created:
                    self.logger.info("Aggiunta classificazione oggetto settore_sottosettore_categoria: %s" %
                                (settore_sottosettore_categoria.codice,))

            except DatabaseError as e:
                self.logger.error("In fetch di settore-sottosettore-categoria per codice locale:%s. %s" %
                             (codice_locale, e))
                continue

            # totale finanziamento
            fin_totale = Decimal(r['FINANZ_TOTALE'].replace(',','.')) if r['FINANZ_TOTALE'].strip() else None
            fin_totale_pubblico = Decimal(r['FINANZ_TOTALE_PUBBLICO'].replace(',','.')) if r['FINANZ_TOTALE_PUBBLICO'].strip() else None

            fin_ue = Decimal(r['FINANZ_UE'].replace(',','.')) if r['FINANZ_UE'].strip() else None
            fin_stato_fondo_rotazione = Decimal(r['FINANZ_Stato_Fondo_di_Rotazione'].replace(',','.')) if r['FINANZ_Stato_Fondo_di_Rotazione'].strip() else None
            fin_stato_fsc = Decimal(r['FINANZ_Stato_FSC'].replace(',','.')) if r['FINANZ_Stato_FSC'].strip() else None
            fin_stato_altri_provvedimenti = Decimal(r['FINANZ_Stato_altri_provvedimenti'].replace(',','.')) if r['FINANZ_Stato_altri_provvedimenti'].strip() else None
            fin_regione = Decimal(r['FINANZ_Regione'].replace(',','.')) if r['FINANZ_Regione'].strip() else None
            fin_provincia = Decimal(r['FINANZ_Provincia'].replace(',','.')) if r['FINANZ_Provincia'].strip() else None
            fin_comune = Decimal(r['FINANZ_Comune'].replace(',','.')) if r['FINANZ_Comune'].strip() else None
            fin_altro_pubblico = Decimal(r['FINANZ_Altro_pubblico'].replace(',','.')) if r['FINANZ_Altro_pubblico'].strip() else None
            fin_stato_estero = Decimal(r['FINANZ_Stato_estero'].replace(',','.')) if r['FINANZ_Stato_estero'].strip() else None
            fin_privato = Decimal(r['FINANZ_Privato'].replace(',','.')) if r['FINANZ_Privato'].strip() else None
            fin_da_reperire = Decimal(r['FINANZ_Da_reperire'].replace(',','.')) if r['FINANZ_Da_reperire'].strip() else None

            costo = Decimal(r['COSTO'].replace(',','.')) if r['COSTO'].strip() else None
            costo_ammesso = Decimal(r['COSTO_AMMESSO'].replace(',','.')) if r['COSTO_AMMESSO'].strip() else None
            pagamento = Decimal(r['PAGAMENTO'].replace(',','.')) if r['PAGAMENTO'].strip() else None
            pagamento_fsc = Decimal(r['PAGAMENTO_FSC'].replace(',','.')) if r['PAGAMENTO_FSC'].strip() else None
            pagamento_ammesso = Decimal(r['PAGAMENTO_AMMESSO'].replace(',','.')) if r['PAGAMENTO_AMMESSO'].strip() else None

            # date
            data_inizio_prevista = datetime.datetime.strptime(r['DATA_INIZIO_PREVISTA'], '%Y%m%d') if r['DATA_INIZIO_PREVISTA'].strip() else None
            data_fine_prevista = datetime.datetime.strptime(r['DATA_FINE_PREVISTA'], '%Y%m%d') if r['DATA_FINE_PREVISTA'].strip() else None
            data_inizio_effettiva = datetime.datetime.strptime(r['DATA_INIZIO_EFFETTIVA'], '%Y%m%d') if r['DATA_INIZIO_EFFETTIVA'].strip() else None
            data_fine_effettiva = datetime.datetime.strptime(r['DATA_FINE_EFFETTIVA'], '%Y%m%d') if r['DATA_FINE_EFFETTIVA'].strip() else None


            # progetto
            try:
                p, created = Progetto.objects.get_or_create(
                    codice_locale=codice_locale,
                    defaults={
                        'classificazione_qsn': obiettivo_specifico_qsn,
                        'titolo_progetto': r['TITOLO_PROGETTO'],
                        'cup': r['CUP'],
                        'stato_fs': stato_fs,
                        'stato_fsc': stato_fsc,
                        'stato_dps': stato_dps,
                        'programma_asse_obiettivo': programma_asse_obiettivo,
                        'data_aggiornamento': data_aggiornamento,
                        'obiettivo_sviluppo': obiettivo_sviluppo,
                        'tipo_operazione': tipo_operazione,
                        'fondo_comunitario': fondo_comunitario,
                        'tema': tema_prioritario,
                        'intesa_istituzionale': intesa,
                        'classificazione_azione': natura_tipologia,
                        'classificazione_oggetto': settore_sottosettore_categoria,
                        'fin_totale': fin_totale,
                        'fin_totale_pubblico': fin_totale_pubblico,
                        'fin_ue': fin_ue,
                        'fin_stato_fondo_rotazione': fin_stato_fondo_rotazione,
                        'fin_stato_fsc': fin_stato_fsc,
                        'fin_stato_altri_provvedimenti': fin_stato_altri_provvedimenti,
                        'fin_regione': fin_regione,
                        'fin_provincia': fin_provincia,
                        'fin_comune': fin_comune,
                        'fin_altro_pubblico': fin_altro_pubblico,
                        'fin_stato_estero': fin_stato_estero,
                        'fin_privato': fin_privato,
                        'fin_da_reperire': fin_da_reperire,
                        'costo': costo,
                        'costo_ammesso': costo_ammesso,
                        'pagamento': pagamento,
                        'pagamento_fsc': pagamento_fsc,
                        'pagamento_ammesso': pagamento_ammesso,
                        'data_inizio_prevista': data_inizio_prevista,
                        'data_fine_prevista': data_fine_prevista,
                        'data_inizio_effettiva': data_inizio_effettiva,
                        'data_fine_effettiva': data_fine_effettiva,
                        'data_inizio_info': r['DATA_INIZIO_INFO'],
                        'dps_date': r['DPS_DATE'],
                        'dps_flag_date_previste': r['DPS_FLAG_DATE_PREVISTE'],
                        'dps_flag_date_effettive': r['DPS_FLAG_DATE_EFFETTIVE'],
                        'dps_flag_cup': r['DPS_FLAG_CUP'],
                    }
                )

                if created:
                    self.logger.debug("%s: Creazione progetto nuovo: %s" % (c, p.codice_locale))

            except DatabaseError as e:
                self.logger.error("Progetto %s: %s" % (r['COD_LOCALE_PROGETTO'], e))
                continue

            if int(options['limit']) and \
               (c - int(options['offset']) > int(options['limit'])):
                break

        self.logger.info("Fine")




