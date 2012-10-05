# -*- coding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import DatabaseError
from django.core.management.base import BaseCommand, CommandError

from open_coesione import utils
from optparse import make_option
from decimal import Decimal
import re
import csv
import logging
import datetime
import codecs

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
                    default='proj',
                    help='Type of import: proj|loc|rec|cups|desc'),
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
        elif options['type'] == 'loc':
            self.handle_loc(*args, **options)
        elif options['type'] == 'rec':
            self.handle_rec(*args, **options)
        elif options['type'] == 'cups':
            self.handle_cups(*args, **options)
        elif options['type'] == 'desc':
            self.handle_desc(*args, **options)
        else:
            self.logger.error("Wrong type %s. Select among proj, loc and rec." % options['type'])
            exit(1)


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

        if options['delete']:
            self.logger.error("Could not revert descriptions updates.")
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

            # prendo il progetto con per CUP
            try:
                progetto = Progetto.objects.get(cup__iexact=r['CUP'].strip())
                self.logger.debug("%s - Progetto: %s" % (c, progetto.cup))
            except ObjectDoesNotExist:
                self.logger.warning("%s - Progetto non trovato: %s, skip" % (c, r['CUP']))
                not_found += 1
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

        self.logger.info("Fine: %s descrizioni aggiornate, %s sintesi da importare erano vuote e %s progetti non sono stati trovati tramite il cup" % (updates, already_ok, not_found))



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
            created = False
            denominazione = re.sub('\s{2,}', ' ', r['DPS_DENOMINAZIONE_SOGG']).strip()
            try:
                soggetto = Soggetto.objects.get(denominazione__iexact=denominazione)
            except ObjectDoesNotExist:
                soggetto = Soggetto.objects.create(
                    denominazione=denominazione,
                    codice_fiscale=r['DPS_CODICE_FISCALE_SOGG'].strip(),
                    forma_giuridica=forma_giuridica,
                    indirizzo=indirizzo,
                    cap=cap,
                    territorio=territorio
                )
                created = True

            if created:
                self.logger.info(u"%s: Aggiunto soggetto: %s" % (c, soggetto.denominazione,))
            else:
                self.logger.debug(u"%s: Soggetto trovato e non modificato: %s" % (c, soggetto.denominazione))

            # add role of subject in project
            Ruolo.objects.create(
                progetto = progetto,
                soggetto = soggetto,
                ruolo = r['SOGG_COD_RUOLO']
            )



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

            tipo_territorio = r['DPS_TERRITORIO_PROG']

            if tipo_territorio == Territorio.TERRITORIO.R:
                territorio = Territorio.objects.get(
                    cod_reg=int(r['COD_REGIONE']),
                    territorio=Territorio.TERRITORIO.R,
                )
            elif tipo_territorio == 'P':
                territorio = Territorio.objects.get(
                    cod_reg=int(r['COD_REGIONE']),
                    cod_prov=int(r['COD_PROVINCIA']),
                    territorio=Territorio.TERRITORIO.P,
                )
            elif tipo_territorio == 'C':
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

            # codice locale progetto (ID del record)
            try:
                progetto = Progetto.objects.get(pk=r['COD_LOCALE_PROGETTO'])
            except ObjectDoesNotExist:
                progetto = None
                self.logger.warning("Progetto non trovato: %s" % (r['COD_LOCALE_PROGETTO']))

            if progetto:
                created = False
                localizzazione, created = progetto.localizzazione_set.get_or_create(
                    territorio=territorio,
                    progetto = progetto,
                    defaults={
                        'indirizzo': r['INDIRIZZO_PROG'].strip(),
                        'cap': r['CAP_PROG'].strip(),
                        'dps_flag_cap': r['DPS_FLAG_CAP_PROG']
                    }
                )
                if created:
                    self.logger.info("%d - Aggiunta localizzazione progetto: %s" % (c, localizzazione,))
                else:
                    self.logger.debug("%d - Trovata localizzazione progetto: %s" % (c, localizzazione,))

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
            # fin_totale = Decimal(r['FINANZ_TOTALE'].replace(',','.')) if r['FINANZ_TOTALE'].strip() else None
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

            # costo = Decimal(r['COSTO'].replace(',','.')) if r['COSTO'].strip() else None
            costo_ammesso = Decimal(r['COSTO_RENDICONTABILE_UE'].replace(',','.')) if r['COSTO_RENDICONTABILE_UE'].strip() else None
            pagamento = Decimal(r['TOT_PAGAMENTI'].replace(',','.')) if r['TOT_PAGAMENTI'].strip() else None
            # pagamento_fsc = Decimal(r['PAGAMENTO_FSC'].replace(',','.')) if r['PAGAMENTO_FSC'].strip() else None
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
#                        'tipo_operazione': tipo_operazione,
                        'fondo_comunitario': fondo_comunitario,
                        'tema': tema_prioritario,
#                        'intesa_istituzionale': intesa,
                        'fonte': fonte,
                        'classificazione_azione': natura_tipologia,
                        'classificazione_oggetto': settore_sottosettore_categoria,
#
                        'cipe_num_delibera': cipe_num_delibera,
                        'cipe_anno_delibera': cipe_anno_delibera,
                        'cipe_data_adozione': cipe_data_adozione,
                        'cipe_data_pubblicazione': cipe_data_pubblicazione,
                        'note': cipe_note,
                        'cipe_flag': cipe_flag,
#
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
#                        'costo': costo,
                        'costo_ammesso': costo_ammesso,
                        'pagamento': pagamento,
#                        'pagamento_fsc': pagamento_fsc,
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


            except DatabaseError as e:
                self.logger.error("Progetto %s: %s" % (r['COD_LOCALE_PROGETTO'], e))
                continue

        self.logger.info("Fine")




