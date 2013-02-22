# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import connection
from django.db.utils import DatabaseError
from django.core.management.base import BaseCommand

from open_coesione import utils
from optparse import make_option
from decimal import Decimal
import re
import csv
import logging
import datetime

from progetti.models import *
from soggetti.models import *
from territori.models import Territorio

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
                    default=None,
                    help='Type of import: proj|loc|rec|cups|desc|pay'),
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
                    help='Delete records, before importing new'),
        make_option('--encoding',
                    dest='encoding',
                    default='iso-8859-1',
                    help='set character encoding of input file')
    )

    csv_file = ''
    encoding = 'iso-8859-1'
    logger = logging.getLogger('csvimport')
    unicode_reader = None

    def handle(self, *args, **options):
        self.csv_file = options['csvfile']
        self.encoding = options['encoding']

        # read first csv file
        try:
            self.unicode_reader = utils.UnicodeDictReader(open(self.csv_file, 'r'), delimiter=';', encoding=self.encoding)
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

        if options['type'] == 'proj':
            self.handle_proj(*args, **options)
        elif options['type'] == 'cipeproj':
            self.handle_cipeproj(*args, **options)
        elif options['type'] == 'loc':
            self.handle_loc(*args, **options)
        elif options['type'] == 'rec':
            self.handle_rec(*args, **options)
        elif options['type'] == 'cups':
            self.handle_cups(*args, **options)
        elif options['type'] == 'desc':
            self.handle_desc(*args, **options)
        elif options['type'] == 'pay':
            self.handle_payments(*args, **options)
        else:
            self.logger.error("Wrong type %s. Select among proj, loc and rec." % options['type'])
            exit(1)

    def handle_payments(self, *args, **options):
        """
        Parse a payments file, with historical records of payments for projects, and store
        records into PagamentoProgetto model
        """
        self.logger.info("Inizio import da %s" % self.csv_file)
        self.logger.info("Encoding: %s" % self.encoding)
        self.logger.info("Limit: %s" % options['limit'])
        self.logger.info("Offset: %s" % options['offset'])

        if options['delete']:
            PagamentoProgetto.objects.all().delete()
            self.logger.info("Tutti i pagamenti sono stati cancellati")
            exit(1)

        stats = {
            'Progetti trovati nel db': 0,
            'Progetti NON trovati nel db': 0,
            'Progetti con COD_LOCALE_PROGETTO da modificare (iexacted)': 0,
            'Progetti con Pagamenti negativi': 0,
            'Progetti con pagamenti maggiori del fin_totale_pubblico': 0,
            'Progetti con fin_totale_pubblico non presente nei pagamenti': 0,
            'Numero pagamenti inseriti': 0,
        }

        for row in self.unicode_reader:
            # select a set of rows
            # with offset
            c = self.unicode_reader.reader.line_num - 1
            if c < int(options['offset']):
                continue
                # and limit
            if int(options['limit']) and\
               (c - int(options['offset']) > int(options['limit'])):
                break
            # ... i'm working...
            if c % 2500 == 0: self.logger.info( ".. read line %d .." % c )


            project_code = row['COD_LOCALE_PROGETTO'].strip()

            # fetch progetto from cod_locale_progetto
            try:
                progetto = Progetto.objects.get( pk=project_code )
                self.logger.debug("%s] - Progetto: %s" % (c, progetto.codice_locale))
                stats['Progetti trovati nel db'] += 1
            except Progetto.DoesNotExist:
                self.logger.warning("%s] - Progetto non trovato: %s, SKIP" % (c, project_code))
                stats['Progetti NON trovati nel db'] += 1
                continue


            if row['DATA_AGGIORNAMENTO'].strip() is None:
                self.logger.warning("%s] - Data aggiornamento non trovata (%s)" % (c, progetto.codice_locale))
            dt = datetime.datetime.strptime(row['DATA_AGGIORNAMENTO'], '%Y%m%d')

            tot = row['TOT_PAGAMENTI'].strip() if row['TOT_PAGAMENTI'].strip() else None
            # skip empty payment
            if tot is None:
                self.logger.debug("%s] Progetto '%s' ha un pagamento nullo in data %s, SKIP" % (c, project_code, dt))
                continue

            # transform amount into Decimal
            tot = Decimal(tot.replace(',','.'))

            created = False
            pp, created = PagamentoProgetto.objects.get_or_create(
                progetto= progetto,
                data= dt,
                ammontare= tot if tot >= 0.0 else 0.0,
            )
            if created:
                self.logger.info("%s: pagamento inserito: %s" % (c, pp))
            else:
                self.logger.debug("%s: pagamento trovato e non duplicato: %s" % (c, pp))

            stats['Numero pagamenti inseriti'] +=1



        self.logger.info('-------------- STATS --------------')
        self.logger.info('')
        for k in stats:
            self.logger.info( "%s : %s" % (k, stats[k]) )
        self.logger.info('')

    def handle_cups(self, *args, **options):
        self.logger.info("Inizio import da %s" % self.csv_file)
        self.logger.info("Encoding: %s" % self.encoding)
        self.logger.info("Limit: %s" % options['limit'])
        self.logger.info("Offset: %s" % options['offset'])

        if options['delete']:
            self.logger.error("Could not revert cup updates.")
            exit(1)

        updates = 0
        already_ok = 0
        not_found = 0
        for r in self.unicode_reader:
            c = self.unicode_reader.reader.line_num - 1
            if c < int(options['offset']):
                continue

            if int(options['limit']) and\
               (c - int(options['offset']) > int(options['limit'])):
                break

            # codice locale progetto (ID del record)
            try:
                progetto = Progetto.objects.get(pk=r['COD_LOCALE_PROGETTO'].strip())
                self.logger.debug("%s - Progetto: %s" % (c, progetto.codice_locale))
            except ObjectDoesNotExist:
                self.logger.warning("%s - Progetto non trovato: %s, skipping" % (c, r['COD_LOCALE_PROGETTO']))
                not_found += 1
                continue

            if progetto.cup != r['CUP']:
                self.logger.info("Update CUP for progetto %s from '%s' to '%s'" % (progetto, progetto.cup, r['CUP'].strip()))
                progetto.cup = r['CUP'].strip()
                progetto.save()
                updates += 1
            else:
                self.logger.info("Progetto %s already has right cup '%s'" % (progetto, r['CUP'].strip()))
                already_ok += 1

        self.logger.info("Fine: %s cup aggiornati, %s non necessitavano aggiornamento e %s progetti non sono stati trovati" % (updates, already_ok, not_found))

    def handle_desc(self, *args, **options):
        self.logger.info("Inizio import da %s" % self.csv_file)
        self.logger.info("Encoding: %s" % self.encoding)
        self.logger.info("Limit: %s" % options['limit'])
        self.logger.info("Offset: %s" % options['offset'])


        # read first csv file
        try:
            self.unicode_reader = utils.UnicodeDictReader(open(self.csv_file, 'r'), delimiter='|', encoding=self.encoding)
        except IOError:
            self.logger.error("It was impossible to open file %s" % self.csv_file)
            exit(1)
        except csv.Error, e:
            self.logger.error("CSV error while reading %s: %s" % (self.csv_file, e.message))

        if options['delete']:
            self.logger.error("Could not revert descriptions updates.")
            exit(1)

        updates = 0
        already_ok = 0
        not_found = 0
        duplicate = 0
        for r in self.unicode_reader:
            c = self.unicode_reader.reader.line_num - 1
            if c < int(options['offset']):
                continue

            if int(options['limit']) and\
               (c - int(options['offset']) > int(options['limit'])):
                break

            # prendo il progetto con per CUP
            try:
                progetto = Progetto.objects.get(pk=r['CodiceLocaleProgetto'].strip())
                self.logger.debug("%s - Progetto: %s" % (c, progetto.pk))
            except ObjectDoesNotExist:
                self.logger.warning("%s - Progetto non trovato: %s, skip" % (c, r['CodiceLocaleProgetto']))
                not_found += 1
                continue
            except MultipleObjectsReturned:
                self.logger.warning(u"%s - Più progetti con Codice: %s, skip" % (c, r['CodiceLocaleProgetto']))
                duplicate += 1
                continue


            sintesi = r['Sintesi'].strip()

            if sintesi:
                self.logger.info("Aggiornamento descrizione per il progetto %s" % progetto)
                progetto.descrizione = sintesi
                progetto.save()
                updates += 1
            else:
                self.logger.info("Sintesi vuota per il progetto %s" % progetto)
                already_ok += 1

        self.logger.info(
            "Fine: %s descrizioni aggiornate, %s sintesi da importare erano vuote, %s progetti non sono stati trovati tramite il codice progetto locale, %s progetti si riferiscono a un CUP non univoco" %
            (updates, already_ok, not_found, duplicate)
        )

    def handle_rec(self, *args, **options):
        self.logger.info("Inizio import da %s" % self.csv_file)
        self.logger.info("Encoding: %s" % self.encoding)
        self.logger.info("Limit: %s" % options['limit'])
        self.logger.info("Offset: %s" % options['offset'])

        # check whether to remove records
        if options['delete']:
            Soggetto.objects.all().delete()
            FormaGiuridica.objects.all().delete()
            self.logger.info("Oggetti rimossi")


        for r in self.unicode_reader:
            c = self.unicode_reader.reader.line_num - 1
            if c < int(options['offset']):
                continue

            if int(options['limit']) and\
               (c - int(options['offset']) > int(options['limit'])):
                break

            # codice locale progetto (ID del record)
            try:
                progetto = Progetto.objects.get(pk=r['COD_LOCALE_PROGETTO'])
                self.logger.debug("%s - Progetto: %s" % (c, progetto.codice_locale))
            except ObjectDoesNotExist:
                self.logger.warning("%s - Progetto non trovato: %s, skipping" % (c, r['COD_LOCALE_PROGETTO']))
                continue

            # lookup o creazione forma giuridica
            created = False
            forma_giuridica, created = FormaGiuridica.objects.get_or_create(
                codice=r['COD_FORMA_GIURIDICA_SOGG'],
                defaults={
                    'denominazione': r['DESCR_FORMA_GIURIDICA_SOGG'],
                    }
            )
            if created:
                self.logger.info(u"Aggiunta forma giuridica: %s (%s)" %
                                 (forma_giuridica, forma_giuridica.codice))
            else:
                self.logger.debug(u"Trovata forma giuridica: %s (%s)" %
                                  (forma_giuridica, forma_giuridica.codice))

            # localizzazione
            try:
                territorio = Territorio.objects.get_from_istat_code(r['COD_COMUNE_SEDE_SOGG'])
            except ObjectDoesNotExist:
                territorio = None

            indirizzo = r['INDIRIZZO_SOGG'].strip() if r['INDIRIZZO_SOGG'].strip() else None
            cap = r['CAP_SOGG'].strip() if r['CAP_SOGG'].strip() else None

            # creazione soggetto
            soggetto = None
            denominazione = re.sub('\s{2,}', ' ', r['DPS_DENOMINAZIONE_SOGG']).strip()
            try:
                soggetto = Soggetto.objects.get(denominazione__iexact=denominazione)
                self.logger.debug(u"%s: Soggetto trovato e non modificato: %s" % (c, soggetto.denominazione))
            except ObjectDoesNotExist:
                try:
                    soggetto = Soggetto.objects.create(
                        denominazione=denominazione,
                        codice_fiscale=r['DPS_CODICE_FISCALE_SOGG'].strip(),
                        forma_giuridica=forma_giuridica,
                        indirizzo=indirizzo,
                        cap=cap,
                        territorio=territorio
                    )
                    self.logger.info(u"%s: Aggiunto soggetto: %s" % (c, soggetto.denominazione,))
                except DatabaseError as e:
                    self.logger.warning("{0} - Database error: {1}. Skipping.".format(c, e))
                    connection._rollback()

            if soggetto:
                # add role of subject in project
                created = False
                role, created = Ruolo.objects.get_or_create(
                    progetto = progetto,
                    soggetto = soggetto,
                    ruolo = r['SOGG_COD_RUOLO']
                )
                if created:
                    self.logger.info(u"%s: Ruolo creato: %s" % (c, role,))
                else:
                    self.logger.debug(u"%s: Ruolo trovato: %s" % (c, role,))

                del soggetto
                del progetto



        self.logger.info("Fine")

    def handle_loc(self, *args, **options):
        self.logger.info("Inizio import da %s" % self.csv_file)
        self.logger.info("Limit: %s" % options['limit'])
        self.logger.info("Offset: %s" % options['offset'])

        # check whether to remove records
        if options['delete']:
            Localizzazione.objects.all().delete()
            self.logger.info("Oggetti rimossi")


        for r in self.unicode_reader:

            c = self.unicode_reader.reader.line_num
            if c < int(options['offset']):
                continue


            if int(options['limit']) and\
               (c - int(options['offset']) > int(options['limit'])):
                break

            if 'DPS_TERRITORIO_PROG' in r.keys():
                tipo_territorio = r['DPS_TERRITORIO_PROG']
            else:
                # caso localizzazioni progetti CIPE (non c'è il campo DPS_TERRITORIO_PROG)
                tipo_territorio = Territorio.TERRITORIO.C
                if r['COD_PROVINCIA'] in ('000', '900'):
                    tipo_territorio = Territorio.TERRITORIO.R
                else:
                    if r['COD_COMUNE'] in ('000', '900'):
                        tipo_territorio = Territorio.TERRITORIO.P

            if tipo_territorio == Territorio.TERRITORIO.R:
                territorio = Territorio.objects.get(
                    cod_reg=int(r['COD_REGIONE']),
                    territorio=Territorio.TERRITORIO.R,
                )
            elif tipo_territorio == Territorio.TERRITORIO.P:
                territorio = Territorio.objects.get(
                    cod_reg=int(r['COD_REGIONE']),
                    cod_prov=int(r['COD_PROVINCIA']),
                    territorio=Territorio.TERRITORIO.P,
                )
            elif tipo_territorio == Territorio.TERRITORIO.C:
                try:
                    territorio = Territorio.objects.get(
                        cod_reg=int(r['COD_REGIONE']),
                        cod_prov=int(r['COD_PROVINCIA']),
                        cod_com="%s%s" % (int(r['COD_PROVINCIA']), r['COD_COMUNE']),
                        territorio=Territorio.TERRITORIO.C,
                    )
                except Territorio.DoesNotExist as e:
                    try:
                        territorio = Territorio.objects.get(
                            cod_reg=int(r['COD_REGIONE']),
                            denominazione=r['DEN_COMUNE'],
                            territorio=Territorio.TERRITORIO.C,
                        )
                        self.logger.debug("Comune '%s' individuato attraverso la denominazione" % r['DEN_COMUNE'])
                    except Territorio.DoesNotExist as e:
                        self.logger.warning("Comune non trovato. %s: %s-%s-%s [%s]" % (r['DEN_COMUNE'],r['DEN_REGIONE'],r['COD_PROVINCIA'],r['COD_COMUNE'],r['COD_LOCALE_PROGETTO']))
                        continue
            elif tipo_territorio in ('E', 'N'):
                # territorio estero o nazionale
                # get_or_create, perché non sono in Territorio di default
                created = False
                codice_territorio = int(r['COD_REGIONE'])
                territorio, created = Territorio.objects.get_or_create(
                    cod_reg=codice_territorio,
                    cod_prov=0,
                    cod_com=0,
                    territorio=tipo_territorio,
                    defaults={
                        'denominazione': r['DEN_REGIONE']
                    }
                )
                if created:
                    self.logger.info("Aggiunto territorio di tipo %s: %s" % (tipo_territorio, territorio.denominazione))
                else:
                    self.logger.debug("Trovato territorio di tipo %s: %s" % (tipo_territorio, territorio.denominazione))
            else:
                self.logger.warning('Tipo di territorio sconosciuto o errato %s. Skip.' % (tipo_territorio,))
                continue


            indirizzo = r['INDIRIZZO_PROG'].strip()if 'INDIRIZZO_PROG' in r.keys() and r['INDIRIZZO_PROG'] else None
            cap = r['CAP_PROG'].strip() if 'CAP_PROG' in r.keys() and r['CAP_PROG'] else None
            dps_flag_cap = r['DPS_FLAG_CAP_PROG'] if 'DPS_FLAG_CAP_PROG' in r.keys() and r['DPS_FLAG_CAP_PROG'] else 0


            # codice locale progetto (ID del record)
            try:
                if 'COD_LOCALE_PROGETTO' in r.keys():
                    pk_progetto = r['COD_LOCALE_PROGETTO']
                elif 'COD_DIPE' in r.keys():
                    pk_progetto = r['COD_DIPE']
                else:
                    self.logger.fatal("Chiave primaria mancante")
                    quit()

                progetto = Progetto.objects.get(pk=pk_progetto)
            except ObjectDoesNotExist:
                progetto = None
                self.logger.warning("%d - Progetto non trovato: %s" % (c, pk_progetto))

            if progetto:
                created = False
                localizzazione, created = progetto.localizzazione_set.get_or_create(
                    territorio=territorio,
                    progetto = progetto,
                    defaults={
                        'indirizzo': indirizzo,
                        'cap': cap,
                        'dps_flag_cap': dps_flag_cap,
                    }
                )
                if created:
                    self.logger.info("%d - Aggiunta localizzazione progetto: %s" % (c, localizzazione,))
                else:
                    self.logger.debug("%d - Trovata localizzazione progetto: %s" % (c, localizzazione,))


                del localizzazione
                del progetto

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
            Tema.objects.all().delete()
            self.logger.info("Oggetti rimossi")


        for r in self.unicode_reader:
            c = self.unicode_reader.reader.line_num - 1
            if c < int(options['offset']):
                continue

            if int(options['limit']) and\
               (c - int(options['offset']) > int(options['limit'])):
                break

            # codice locale (ID del record)
            codice_locale = r['COD_LOCALE_PROGETTO']

            # classificazione QSN
            if r['QSN_COD_PRIORITA'].strip():
                created = False
                qsn_codice_priorita = r['QSN_COD_PRIORITA']
                qsn_priorita, created = ClassificazioneQSN.objects.get_or_create(
                    codice=qsn_codice_priorita,
                    tipo_classificazione=ClassificazioneQSN.TIPO.priorita,
                    defaults={
                        'descrizione': r['QSN_DESCRIZIONE_PRIORITA']
                    }
                )
                if created:
                    self.logger.info(u"Aggiunta priorità QSN: %s" % qsn_priorita.codice)

                created = False
                qsn_obiettivo_generale, created = ClassificazioneQSN.objects.get_or_create(
                    codice=r['QSN_COD_OBIETTIVO_GENERALE'],
                    tipo_classificazione=ClassificazioneQSN.TIPO.generale,
                    defaults={
                        'descrizione': r['QSN_DESCR_OBIETTIVO_GENERALE'],
                        'classificazione_superiore': qsn_priorita
                    }
                )
                if created:
                    self.logger.info("Aggiunto obiettivo generale QSN: %s (%s)" %
                                      (qsn_obiettivo_generale.codice, qsn_priorita.codice))

                created = False
                qsn_obiettivo_specifico, created = ClassificazioneQSN.objects.get_or_create(
                    codice=r['QSN_CODICE_OBIETTIVO_SPECIFICO'],
                    tipo_classificazione=ClassificazioneQSN.TIPO.specifico,
                    defaults={
                        'descrizione': r['QSN_DESCR_OBIETTIVO_SPECIFICO'],
                        'classificazione_superiore': qsn_obiettivo_generale
                    }
                )
                if created:
                    self.logger.info("Aggiunto obiettivo specifico QSN: %s (%s - %s)" %
                                      (qsn_obiettivo_specifico.codice, qsn_obiettivo_generale.codice, qsn_priorita.codice))
                else:
                    self.logger.debug("Trovato obiettivo specifico QSN: %s (%s - %s)" %
                                     (qsn_obiettivo_specifico.codice, qsn_obiettivo_generale.codice, qsn_priorita.codice))
            else:
                qsn_obiettivo_specifico = None


            # obiettivo sviluppo
            field = re.sub(' +',' ',r['QSN_AREA_OBIETTIVO_UE'].encode('ascii', 'ignore')).strip()
            if field :
                try:
                    obiettivo_sviluppo = [k for k, v in dict(Progetto.OBIETTIVO_SVILUPPO).iteritems() if v.encode('ascii', 'ignore') == field][0]
                    self.logger.debug("Trovato obiettivo sviluppo: %s" % obiettivo_sviluppo)
                except IndexError as e:
                    self.logger.error("Could not find  obiettivo sviluppo %s in %s." % (field, codice_locale))
                    continue
            else:
                obiettivo_sviluppo = ''


            # fondo comunitario
            if r['QSN_FONDO_COMUNITARIO'].strip():
                try:
                    fondo_comunitario = [k for k, v in dict(Progetto.FONDO_COMUNITARIO).iteritems() if v == r['QSN_FONDO_COMUNITARIO']][0]
                    self.logger.debug("Trovato fondo comunitario: %s" % fondo_comunitario)
                except IndexError as e:
                    self.logger.error("While reading fondo comunitario %s in %s. %s" % (r['QSN_FONDO_COMUNITARIO'], codice_locale, e))
                    continue
            else:
                fondo_comunitario = None


            # programma, asse, obiettivo
            try:
                created = False
                programma, created = ProgrammaAsseObiettivo.objects.get_or_create(
                    codice=r['DPS_CODICE_PROGRAMMA'],
                    tipo_classificazione=ProgrammaAsseObiettivo.TIPO.programma,
                    defaults={
                        'descrizione':r['DPS_DESCRIZIONE_PROGRAMMA']
                    }
                )
                if created:
                    self.logger.info("Aggiunto programma: %s" % (programma,))
                else:
                    self.logger.debug("Trovato programma: %s" % (programma,))

                created = False
                programma_asse, created = ProgrammaAsseObiettivo.objects.get_or_create(
                    codice="%s/%s" % (r['DPS_CODICE_PROGRAMMA'], r['PO_CODICE_ASSE']),
                    tipo_classificazione=ProgrammaAsseObiettivo.TIPO.asse,
                    defaults={
                        'descrizione':r['PO_DENOMINAZIONE_ASSE'],
                        'classificazione_superiore': programma
                    }
                )
                if created:
                    self.logger.info("Aggiunto asse: %s" % (programma_asse,))
                else:
                    self.logger.debug("Trovato asse: %s" % (programma_asse,))

                created = False
                programma_asse_obiettivo, created = ProgrammaAsseObiettivo.objects.get_or_create(
                    codice="%s/%s/%s" % (r['DPS_CODICE_PROGRAMMA'], r['PO_CODICE_ASSE'], r['PO_COD_OBIETTIVO_OPERATIVO']),
                    tipo_classificazione=ProgrammaAsseObiettivo.TIPO.obiettivo,
                    defaults={
                        'descrizione':r['PO_OBIETTIVO_OPERATIVO'],
                        'classificazione_superiore': programma_asse
                    }
                )
                if created:
                    self.logger.debug("Aggiunto obiettivo: %s" % (programma_asse_obiettivo,))
                else:
                    self.logger.debug("Trovato obiettivo: %s" % (programma_asse_obiettivo,))


            except DatabaseError as e:
                self.logger.error("In fetch di programma-asse-obiettivo per codice locale:%s. %s" % (codice_locale, e))
                continue

            # tema
            try:
                created = False
                tema_sintetico, created = Tema.objects.get_or_create(
                    descrizione=r['DPS_TEMA_SINTETICO'],
                    tipo_tema=Tema.TIPO.sintetico,
                    defaults={
                        'codice': 1 + Tema.objects.filter(tema_superiore__isnull=True).count(),
                    }
                )

                if created:
                    self.logger.info("Aggiunto tema sintetico: %s" % (tema_sintetico,))
                else:
                    self.logger.debug("Trovato tema sintetico: %s" % (tema_sintetico,))

            except ObjectDoesNotExist as e:
                self.logger.error("While reading tema sintetico %s in %s. %s" % (r['DPS_TEMA_SINTETICO'], codice_locale, e))
                continue

            try:
                created = False
                cod_tema_prioritario = r['QSN_COD_TEMA_PRIORITARIO_UE']
                tema_prioritario, created = Tema.objects.get_or_create(
                    codice="%s.%s" % (tema_sintetico.codice, cod_tema_prioritario),
                    tipo_tema=Tema.TIPO.prioritario,
                    defaults={
                        'descrizione': r['QSN_DESCR_TEMA_PRIORITARIO_UE'],
                        'tema_superiore': tema_sintetico,
                    }
                )
                if created:
                    self.logger.info("Aggiunto tema: %s" % (tema_prioritario.codice,))
                else:
                    self.logger.debug("Trovato tema: %s" % (tema_prioritario.codice,))

            except DatabaseError as e:
                self.logger.error("In fetch di tema prioritario %s per codice locale:%s. %s" %
                             (cod_tema_prioritario, codice_locale, e))
                continue


            # fonte
            try:
                created = False
                fonte, created = Fonte.objects.get_or_create(
                    codice="%s" % (r['DPS_COD_FONTE']),
                    defaults={
                        'descrizione': r['DPS_DESCR_FONTE'],
                        }
                )
                if created:
                    self.logger.info("Aggiunta fonte: %s" % (fonte,))
                else:
                    self.logger.debug("Trovata fonte: %s" % (fonte,))

            except DatabaseError as e:
                self.logger.error("In fetch della fonte %s per codice locale:%s. %s" %
                             (r['DPS_COD_FONTE'], codice_locale, e))
                continue

            # classificazione azione (natura e tipologia)
            try:
                created = False

                # eccezione accorpamento beni e servizi
                cup_cod_natura = r['CUP_COD_NATURA']
                cup_descr_natura = r['CUP_DESCR_NATURA']
                if cup_cod_natura == '02':
                    cup_cod_natura = '01'

                if cup_cod_natura == '01':
                    cup_descr_natura = 'ACQUISTO DI BENI E SERVIZI'


                natura, created = ClassificazioneAzione.objects.get_or_create(
                    codice=cup_cod_natura,
                    tipo_classificazione=ClassificazioneAzione.TIPO.natura,
                    defaults={
                        'descrizione':cup_descr_natura
                    }
                )
                if created:
                    self.logger.info("Aggiunta classificazione azione natura: %s" % (natura.codice,))
                else:
                    self.logger.debug("Trovata classificazione azione natura: %s" % (natura.codice,))

                created = False
                natura_tipologia, created = ClassificazioneAzione.objects.get_or_create(
                    codice="%s.%s" % (cup_cod_natura, r['CUP_COD_TIPOLOGIA']),
                    tipo_classificazione=ClassificazioneAzione.TIPO.tipologia,
                    defaults={
                        'descrizione':r['CUP_DESCR_TIPOLOGIA'],
                        'classificazione_superiore': natura
                    }
                )
                if created:
                    self.logger.info("Aggiunta classificazione azione natura_tipologia: %s" % (natura_tipologia.codice,))
                else:
                    self.logger.debug("Trovata classificazione azione natura_tipologia: %s" % (natura_tipologia.codice,))


            except DatabaseError as e:
                self.logger.error("In fetch di natura-tipologia per codice locale:%s. %s" % (codice_locale, e))
                continue

            # classificazione oggetto
            try:
                created = False
                settore, created = ClassificazioneOggetto.objects.get_or_create(
                    codice=r['CUP_COD_SETTORE'],
                    tipo_classificazione=ClassificazioneOggetto.TIPO.settore,
                    defaults={
                        'descrizione':r['CUP_DESCR_SETTORE']
                    }
                )
                if created:
                    self.logger.info("Aggiunta classificazione oggetto settore: %s" % (settore.codice,))

                created = False
                settore_sottosettore, created = ClassificazioneOggetto.objects.get_or_create(
                    codice="%s.%s" % (r['CUP_COD_SETTORE'], r['CUP_COD_SOTTOSETTORE']),
                    tipo_classificazione=ClassificazioneOggetto.TIPO.sottosettore,
                    defaults={
                        'descrizione':r['CUP_DESCR_SOTTOSETTORE'],
                        'classificazione_superiore': settore
                    }
                )
                if created:
                    self.logger.info("Aggiunta classificazione oggetto settore_sottosettore: %s" %
                                (settore_sottosettore.codice,))
                else:
                    self.logger.debug("Trovata classificazione oggetto settore_sottosettore: %s" %
                                     (settore_sottosettore.codice,))

                created = False
                settore_sottosettore_categoria, created = ClassificazioneOggetto.objects.get_or_create(
                    codice="%s.%s.%s" % (r['CUP_COD_SETTORE'], r['CUP_COD_SOTTOSETTORE'], r['CUP_COD_CATEGORIA']),
                    tipo_classificazione=ClassificazioneOggetto.TIPO.categoria,
                    defaults={
                        'descrizione':r['CUP_DESCR_CATEGORIA'],
                        'classificazione_superiore': settore_sottosettore
                    }
                )
                if created:
                    self.logger.info("Aggiunta classificazione oggetto settore_sottosettore_categoria: %s" %
                                (settore_sottosettore_categoria.codice,))
                else:
                    self.logger.debug("Trovata classificazione oggetto settore_sottosettore_categoria: %s" %
                                     (settore_sottosettore_categoria.codice,))

            except DatabaseError as e:
                self.logger.error("In fetch di settore-sottosettore-categoria per codice locale:%s. %s" %
                             (codice_locale, e))
                continue

            cipe_flag = False
            if 'NUM_DELIBERA' in r.keys():
                cipe_num_delibera = int(r['NUM_DELIBERA']) if r['NUM_DELIBERA'].strip() else None
                cipe_anno_delibera = r['ANNO_DELIBERA'].strip() if r['ANNO_DELIBERA'].strip() else None
                cipe_data_adozione = datetime.datetime.strptime(r['DATA_ADOZIONE'], '%Y%m%d') if r['DATA_ADOZIONE'].strip() else None
                cipe_data_pubblicazione = datetime.datetime.strptime(r['DATA_PUBBLICAZIONE'], '%Y%m%d') if r['DATA_PUBBLICAZIONE'].strip() else None
                cipe_note = r['NOTE'].strip() if r['NOTE'].strip() else None
                if cipe_num_delibera is not None:
                    cipe_flag = True
            else:
                cipe_num_delibera = None
                cipe_anno_delibera = None
                cipe_data_adozione = None
                cipe_data_pubblicazione = None
                cipe_note = None
                
            # totale finanziamento
            fin_totale_pubblico = Decimal(r['FINANZ_TOTALE_PUBBLICO'].replace(',','.')) if r['FINANZ_TOTALE_PUBBLICO'].strip() else None

            fin_ue = Decimal(r['FINANZ_UE'].replace(',','.')) if r['FINANZ_UE'].strip() else None
            fin_stato_fondo_rotazione = Decimal(r['FINANZ_STATO_FONDO_DI_ROTAZIONE'].replace(',','.')) if r['FINANZ_STATO_FONDO_DI_ROTAZIONE'].strip() else None
            fin_stato_fsc = Decimal(r['FINANZ_STATO_FSC'].replace(',','.')) if r['FINANZ_STATO_FSC'].strip() else None
            fin_stato_altri_provvedimenti = Decimal(r['FINANZ_STATO_ALTRI_PROVVEDIMENTI'].replace(',','.')) if r['FINANZ_STATO_ALTRI_PROVVEDIMENTI'].strip() else None
            fin_regione = Decimal(r['FINANZ_REGIONE'].replace(',','.')) if r['FINANZ_REGIONE'].strip() else None
            fin_provincia = Decimal(r['FINANZ_PROVINCIA'].replace(',','.')) if r['FINANZ_PROVINCIA'].strip() else None
            fin_comune = Decimal(r['FINANZ_COMUNE'].replace(',','.')) if r['FINANZ_COMUNE'].strip() else None
            fin_altro_pubblico = Decimal(r['FINANZ_ALTRO_PUBBLICO'].replace(',','.')) if r['FINANZ_ALTRO_PUBBLICO'].strip() else None
            fin_stato_estero = Decimal(r['FINANZ_STATO_ESTERO'].replace(',','.')) if r['FINANZ_STATO_ESTERO'].strip() else None
            fin_privato = Decimal(r['FINANZ_PRIVATO'].replace(',','.')) if r['FINANZ_PRIVATO'].strip() else None
            fin_da_reperire = Decimal(r['FINANZ_DA_REPERIRE'].replace(',','.')) if r['FINANZ_DA_REPERIRE'].strip() else None

            costo_ammesso = Decimal(r['COSTO_RENDICONTABILE_UE'].replace(',','.')) if r['COSTO_RENDICONTABILE_UE'].strip() else None
            pagamento = Decimal(r['TOT_PAGAMENTI'].replace(',','.')) if r['TOT_PAGAMENTI'].strip() else None
            pagamento_ammesso = Decimal(r['TOT_PAGAMENTI_RENDICONTABILI_UE'].replace(',','.')) if r['TOT_PAGAMENTI_RENDICONTABILI_UE'].strip() else None

            # date
            data_inizio_prevista = datetime.datetime.strptime(r['DATA_INIZIO_PREVISTA'], '%Y%m%d') if r['DATA_INIZIO_PREVISTA'].strip() else None
            data_fine_prevista = datetime.datetime.strptime(r['DATA_FINE_PREVISTA'], '%Y%m%d') if r['DATA_FINE_PREVISTA'].strip() else None
            data_inizio_effettiva = datetime.datetime.strptime(r['DATA_INIZIO_EFFETTIVA'], '%Y%m%d') if r['DATA_INIZIO_EFFETTIVA'].strip() else None
            data_fine_effettiva = datetime.datetime.strptime(r['DATA_FINE_EFFETTIVA'], '%Y%m%d') if r['DATA_FINE_EFFETTIVA'].strip() else None

            # data ultimo aggiornamento progetto
            data_aggiornamento = datetime.datetime.strptime(r['DATA_AGGIORNAMENTO'], '%Y%m%d') if r['DATA_AGGIORNAMENTO'].strip() else None


            # progetto
            try:
                p, created = Progetto.objects.get_or_create(
                    codice_locale=codice_locale,
                    defaults={
                        'classificazione_qsn': qsn_obiettivo_specifico,
                        'titolo_progetto': r['DPS_TITOLO_PROGETTO'],
                        'cup': r['CUP'].strip(),
                        'programma_asse_obiettivo': programma_asse_obiettivo,
                        'obiettivo_sviluppo': obiettivo_sviluppo,
                        'fondo_comunitario': fondo_comunitario,
                        'tema': tema_prioritario,
                        'fonte': fonte,
                        'classificazione_azione': natura_tipologia,
                        'classificazione_oggetto': settore_sottosettore_categoria,
                        'cipe_num_delibera': cipe_num_delibera,
                        'cipe_anno_delibera': cipe_anno_delibera,
                        'cipe_data_adozione': cipe_data_adozione,
                        'cipe_data_pubblicazione': cipe_data_pubblicazione,
                        'note': cipe_note,
                        'cipe_flag': cipe_flag,
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
                        'costo_ammesso': costo_ammesso,
                        'pagamento': pagamento,
                        'pagamento_ammesso': pagamento_ammesso,
                        'data_inizio_prevista': data_inizio_prevista,
                        'data_fine_prevista': data_fine_prevista,
                        'data_inizio_effettiva': data_inizio_effettiva,
                        'data_fine_effettiva': data_fine_effettiva,
                        'data_aggiornamento': data_aggiornamento,
                        'dps_flag_presenza_date': r['DPS_FLAG_PRESENZA_DATE'],
                        'dps_flag_date_previste': r['DPS_FLAG_COERENZA_DATE_PREV'],
                        'dps_flag_date_effettive': r['DPS_FLAG_COERENZA_DATE_EFF'],
                        'dps_flag_cup': r['DPS_FLAG_CUP'],
                    }
                )

                if created:
                    self.logger.info("%s: Creazione progetto nuovo: %s" % (c, p.codice_locale))
                else:
                    self.logger.info("%s: Progetto trovato e non modificato: %s" % (c, p.codice_locale))

                # remove local variable p from the namespace,
                #may free some memory
                del p

            except DatabaseError as e:
                self.logger.error("Progetto %s: %s" % (r['COD_LOCALE_PROGETTO'], e))
                continue

        self.logger.info("Fine")

    def handle_cipeproj(self, *args, **options):
        """
        Procedura per importare dati di progetto, e soggetti, a partire dal tracciato del CIPE
        """
        self.logger.info("Inizio import da %s" % self.csv_file)
        self.logger.info("Limit: %s" % options['limit'])
        self.logger.info("Offset: %s" % options['offset'])

        # check whether to remove records
        if options['delete']:
            Progetto.objects.filter(cipe_flag=True).delete()
            DeliberaCIPE.objects.all().delete()
            self.logger.info("Progetti CIPE rimossi")

        for r in self.unicode_reader:
            c = self.unicode_reader.reader.line_num - 1
            if c < int(options['offset']):
                continue

            if int(options['limit']) and \
                    (c - int(options['offset']) > int(options['limit'])):
                break

            # codice locale (ID del record)
            codice_locale = r['COD_DIPE']

            cipe_flag = True
            cipe_num_delibera = int(r['NUM_DELIBERA']) if r['NUM_DELIBERA'].strip() else None
            cipe_anno_delibera = r['ANNO_DELIBERA'].strip() if r['ANNO_DELIBERA'].strip() else None
            cipe_data_adozione = datetime.datetime.strptime(r['DATA_ADOZIONE_TEMP'], '%Y%m%d') if r['DATA_ADOZIONE_TEMP'].strip() else None
            cipe_data_pubblicazione = datetime.datetime.strptime(r['DATA_PUBBLICAZIONE'], '%Y%m%d') if r['DATA_PUBBLICAZIONE'].strip() else None
            cipe_finanziamento = Decimal(r['ASSEGNAZIONE_CIPE'].replace(',','.')) if r['ASSEGNAZIONE_CIPE'].strip() else None
            cipe_note = r['NOTE'].strip() if r['NOTE'].strip() else ''

            # le delibere CIPE (possono essere più di una per un progetto)
            try:
                created = False
                delibera, created = DeliberaCIPE.objects.get_or_create(
                    num=cipe_num_delibera,
                    defaults={
                        'anno': cipe_anno_delibera,
                        'data_adozione': cipe_data_adozione,
                        'data_pubblicazione': cipe_data_pubblicazione,
                        }
                )
                if created:
                    self.logger.info("Aggiunta delibera: %s" % (delibera,))
                else:
                    self.logger.debug("Trovata delibera: %s" % (delibera,))

            except DatabaseError as e:
                self.logger.error("In fetch di delibera per prog. con codice locale:%s. %s" %
                                  (codice_locale, e))
                continue


            # CUP, possono essere più di uno, separati da virgole
            cups_progetto = r['CUP'].strip().split(";") if r['CUP'] else [None,]

            titolo_progetto = r['TITOLO_PROGETTO'].strip() if r['TITOLO_PROGETTO'] else ''

            # totale finanziamento
            costo = Decimal(r['COSTO'].replace(',','.')) if 'COSTO' in r.keys() and r['COSTO'].strip() else None

            # programma, asse, obiettivo
            try:
                programmazione = r['PROGRAMMAZIONE']

                created = False
                programma, created = ProgrammaAsseObiettivo.objects.get_or_create(
                    codice=programmazione,
                    tipo_classificazione=ProgrammaAsseObiettivo.TIPO.programma,
                    defaults={
                        'descrizione':programmazione
                    }
                )
                if created:
                    self.logger.info("Aggiunto programma: %s" % (programma,))
                else:
                    self.logger.debug("Trovato programma: %s" % (programma,))

                created = False
                programma_asse, created = ProgrammaAsseObiettivo.objects.get_or_create(
                    codice="%s/00" % (programmazione,),
                    tipo_classificazione=ProgrammaAsseObiettivo.TIPO.asse,
                    defaults={
                        'descrizione':'',
                        'classificazione_superiore': programma
                    }
                )
                if created:
                    self.logger.info("Aggiunto asse: %s" % (programma_asse,))
                else:
                    self.logger.debug("Trovato asse: %s" % (programma_asse,))

                created = False
                programma_asse_obiettivo, created = ProgrammaAsseObiettivo.objects.get_or_create(
                    codice="%s/00/00" % (programmazione, ),
                    tipo_classificazione=ProgrammaAsseObiettivo.TIPO.obiettivo,
                    defaults={
                        'descrizione':'',
                        'classificazione_superiore': programma_asse
                    }
                )
                if created:
                    self.logger.debug("Aggiunto obiettivo: %s" % (programma_asse_obiettivo,))
                else:
                    self.logger.debug("Trovato obiettivo: %s" % (programma_asse_obiettivo,))


            except DatabaseError as e:
                self.logger.error("In fetch di programma-asse-obiettivo per codice locale:%s. %s" % (codice_locale, e))
                continue

            # tema
            dps_tema = self._normalizza_tema(r['DPS_TEMA_SINTETICO'])

            try:
                created = False
                tema_sintetico, created = Tema.objects.get_or_create(
                    descrizione=dps_tema,
                    tipo_tema=Tema.TIPO.sintetico,
                    defaults={
                        'codice': 1 + Tema.objects.filter(tema_superiore__isnull=True).count(),
                        }
                )

                if created:
                    self.logger.info("Aggiunto tema sintetico: %s" % (tema_sintetico,))
                else:
                    self.logger.debug("Trovato tema sintetico: %s" % (tema_sintetico,))

            except ObjectDoesNotExist as e:
                self.logger.error("While reading tema sintetico %s in %s. %s" % (r['DPS_TEMA_SINTETICO'], codice_locale, e))
                continue

            try:
                created = False
                tema_prioritario, created = Tema.objects.get_or_create(
                    codice="%s.00" % (tema_sintetico.codice,),
                    tipo_tema=Tema.TIPO.prioritario,
                    defaults={
                        'descrizione': '',
                        'tema_superiore': tema_sintetico,
                        }
                )
                if created:
                    self.logger.info("Aggiunto tema: %s" % (tema_prioritario.codice,))
                else:
                    self.logger.debug("Trovato tema: %s" % (tema_prioritario.codice,))

            except DatabaseError as e:
                self.logger.error("In fetch di tema prioritario (00) per codice locale:%s. %s" %
                                  (codice_locale, e))
                continue

            # fonte
            try:
                created = False
                fonte, created = Fonte.objects.get_or_create(
                    descrizione="%s" % (r['FONDO']),
                    defaults = {
                        'codice': 'COD_' + r['FONDO'][-2:],
                        'costo': costo,
                    }
                )
                if created:
                    self.logger.info("Aggiunta fonte: %s" % (fonte,))
                else:
                    self.logger.debug("Trovata fonte: %s" % (fonte,))

            except DatabaseError as e:
                self.logger.error("In fetch della fonte %s per codice locale:%s. %s" %
                                  (r['FONDO'], codice_locale, e))
                continue

            # classificazione azione (natura e tipologia)
            # TODO: in attesa di specifiche
            cup_cod_natura = '03'
            cup_descr_natura = 'REALIZZAZIONE DI LAVORI PUBBLICI (OPERE ED IMPIANTISTICA)'

            try:
                created = False

                # eccezione accorpamento beni e servizi
                if cup_cod_natura == '02':
                    cup_cod_natura = '01'

                if cup_cod_natura == '01':
                    cup_descr_natura = 'ACQUISTO DI BENI E SERVIZI'


                natura, created = ClassificazioneAzione.objects.get_or_create(
                    codice=cup_cod_natura,
                    tipo_classificazione=ClassificazioneAzione.TIPO.natura,
                    defaults={
                        'descrizione':cup_descr_natura
                    }
                )
                if created:
                    self.logger.info("Aggiunta classificazione azione natura: %s" % (natura.codice,))
                else:
                    self.logger.debug("Trovata classificazione azione natura: %s" % (natura.codice,))

                created = False
                natura_tipologia, created = ClassificazioneAzione.objects.get_or_create(
                    codice="%s.00" % (cup_cod_natura,),
                    tipo_classificazione=ClassificazioneAzione.TIPO.tipologia,
                    defaults={
                        'descrizione':'',
                        'classificazione_superiore': natura
                    }
                )
                if created:
                    self.logger.info("Aggiunta classificazione azione natura_tipologia: %s" % (natura_tipologia.codice,))
                else:
                    self.logger.debug("Trovata classificazione azione natura_tipologia: %s" % (natura_tipologia.codice,))

            except DatabaseError as e:
                self.logger.error("In fetch di natura-tipologia per codice locale:%s. %s" % (codice_locale, e))
                continue

            # classificazione oggetto
            try:
                created = False
                settore, created = ClassificazioneOggetto.objects.get_or_create(
                    codice=r['CUP_COD_SETTORE'],
                    tipo_classificazione=ClassificazioneOggetto.TIPO.settore,
                    defaults={
                        'descrizione':r['CUP_DESCR_SETTORE']
                    }
                )
                if created:
                    self.logger.info("Aggiunta classificazione oggetto settore: %s" % (settore.codice,))

                created = False
                settore_sottosettore, created = ClassificazioneOggetto.objects.get_or_create(
                    codice="%s.%s" % (r['CUP_COD_SETTORE'], r['CUP_COD_SOTTOSETTORE']),
                    tipo_classificazione=ClassificazioneOggetto.TIPO.sottosettore,
                    defaults={
                        'descrizione':r['CUP_DESCR_SOTTOSETTORE'],
                        'classificazione_superiore': settore
                    }
                )
                if created:
                    self.logger.info("Aggiunta classificazione oggetto settore_sottosettore: %s" %
                                     (settore_sottosettore.codice,))
                else:
                    self.logger.debug("Trovata classificazione oggetto settore_sottosettore: %s" %
                                      (settore_sottosettore.codice,))

                created = False
                settore_sottosettore_categoria, created = ClassificazioneOggetto.objects.get_or_create(
                    codice="%s.%s.000" % (r['CUP_COD_SETTORE'], r['CUP_COD_SOTTOSETTORE'], ),
                    tipo_classificazione=ClassificazioneOggetto.TIPO.categoria,
                    defaults={
                        'descrizione':'',
                        'classificazione_superiore': settore_sottosettore
                    }
                )
                if created:
                    self.logger.info("Aggiunta classificazione oggetto settore_sottosettore_categoria: %s" %
                                     (settore_sottosettore_categoria.codice,))
                else:
                    self.logger.debug("Trovata classificazione oggetto settore_sottosettore_categoria: %s" %
                                      (settore_sottosettore_categoria.codice,))

            except DatabaseError as e:
                self.logger.error("In fetch di settore-sottosettore-categoria per codice locale:%s. %s" %
                                  (codice_locale, e))
                continue




            # progetto
            try:
                p, created = Progetto.objects.get_or_create(
                    codice_locale=codice_locale,
                    defaults={
                        'cup': cups_progetto[0],
                        'titolo_progetto': titolo_progetto,
                        'programma_asse_obiettivo': programma_asse_obiettivo,
                        'tema': tema_prioritario,
                        'classificazione_azione': natura_tipologia,
                        'classificazione_oggetto': settore_sottosettore_categoria,
                        'fonte': fonte,
                        'cipe_flag': cipe_flag,
                        'costo': costo,
                        'dps_flag_cup': 1,
                    }
                )

                if created:
                    self.logger.info("%s: Creazione progetto nuovo: %s" % (c, p.codice_locale))
                else:
                    self.logger.info("%s: Progetto trovato e non modificato: %s" % (c, p.codice_locale))

                # add cups to CUP table
                if len(cups_progetto) > 0:
                    for c in cups_progetto:
                        c = c.strip()
                        if c not in p.cups_progetto.all():
                            p.cups_progetto.create(cup=c)

                # add delibera to project
                if cipe_flag and delibera:
                    created = False
                    pd, created = ProgettoDeliberaCIPE.objects.get_or_create(
                        progetto=p,
                        delibera=delibera,
                        )
                    pd.finanziamento = cipe_finanziamento
                    pd.note = cipe_note
                    pd.save() # re-computation of notes and fin in post-save signal (see progetti/models.py)


                    if created:
                        self.logger.info("%s: Delibera %s associata a progetto: %s" % (c, delibera, p.codice_locale))
                    else:
                        self.logger.info("%s: Associazione tra delibera %s e progetto %s trovata e non modificata" %
                                         (c, delibera, p.codice_locale))

                # data aggiornamento è l'ultima data pubblicazione delibera cipe,
                # solo se maggiore di quella registrata
                if p.data_aggiornamento is None or p.data_aggiornamento < cipe_data_pubblicazione:
                    p.data_aggiornamento = cipe_data_pubblicazione


                p.save()

                # soggetto responsabile
                soggetto_responsabile = self._get_soggetto(r['SOGGETTO_RESPONSABILE'], c)
                if soggetto_responsabile:
                    # add role of subject in project
                    created = False
                    role, created = Ruolo.objects.get_or_create(
                        progetto = p,
                        soggetto = soggetto_responsabile,
                        ruolo = Ruolo.RUOLO.programmatore
                    )
                    if created:
                        self.logger.info(u"%s: Ruolo creato: %s" % (c, role,))
                    else:
                        self.logger.debug(u"%s: Ruolo trovato: %s" % (c, role,))

                del soggetto_responsabile


                # soggetto attuatore
                soggetto_attuatore = self._get_soggetto(r['SOGGETTO_ATTUATORE'], c)
                if soggetto_attuatore:
                    # add role of subject in project
                    created = False
                    role, created = Ruolo.objects.get_or_create(
                        progetto = p,
                        soggetto = soggetto_attuatore,
                        ruolo = Ruolo.RUOLO.attuatore
                    )
                    if created:
                        self.logger.info(u"%s: Ruolo creato: %s" % (c, role,))
                    else:
                        self.logger.debug(u"%s: Ruolo trovato: %s" % (c, role,))

                del soggetto_attuatore


            except DatabaseError as e:
                self.logger.error("Progetto %s: %s" % (r['COD_DIPE'], e))
                continue

            finally:
                # remove local variable p from the namespace,
                #may free some memory
                del p

        self.logger.info("Fine")



    def _get_soggetto(self, soggetto_field, c):
        soggetto = None

        denominazione = soggetto_field.strip()
        try:
            soggetto = Soggetto.objects.get(denominazione__iexact=denominazione)
            self.logger.debug(u"%s: Soggetto trovato e non modificato: %s" % (c, soggetto.denominazione))
            return soggetto
        except ObjectDoesNotExist:
            try:
                soggetto = Soggetto.objects.create(
                    denominazione=denominazione,
                    codice_fiscale='',
                )
                self.logger.info(u"%s: Aggiunto soggetto: %s" % (c, soggetto.denominazione,))
                return soggetto
            except DatabaseError as e:
                self.logger.warning("{0} - Database error: {1}. Skipping {2}.".format(c, e, soggetto_field))
                connection._rollback()
                return None


    def _normalizza_tema(self, tema):
        """
        Trasforma stringhe maiuscole, con altri termini,
        nelle stringhe *canoniche*, riconosciute dal nostro sistema.
        Ci possono essere più chiavi che corrispondono a uno stesso valore.
        Questa funzione è usata solamente per l'import dei dati.
        """
        temi = {
            u'OCCUPAZIONE E MOBILITÀ DEI LAVORATORI': 'Occupazione e mobilità dei lavoratori',
            u'INCLUSIONE SOCIALE': 'Inclusione sociale',
            u'ISTRUZIONE': 'Istruzione',
            u'COMPETITIVITÀ PER LE IMPRESE': 'Competitività delle imprese',
            u'RICERCA E INNOVAZIONE': 'Ricerca e innovazione',
            u'ATTRAZIONE CULTURALE, NATURALE E TURISTICA': 'Attrazione culturale, naturale e turistica',
            u'SERVIZI DI CURA INFANZIA E ANZIANI': 'Servizi di cura infanzia e anziani',
            u'ENERGIA E EFFICIENZA ENERGETICA': 'Energia e efficienza energetica',
            u'AGENDA DIGITALE': 'Agenda digitale',
            u'AMBIENTE E PREVENZIONE DEI RISCHI': 'Ambiente e prevenzione dei rischi',
            u'RAFFORZAMENTO CAPACITÀ DELLA PA': 'Rafforzamento capacità della PA',
            u'RINNOVAMENTO URBANO E RURALE': 'Rinnovamento urbano e rurale',
            u'AEREOPORTUALI': 'Trasporti e infrastrutture a rete',
            u'TRASPORTI E INFRASTRUTTURE A RETE': 'Trasporti e infrastrutture a rete',
        }

        return temi[tema]
