# -*- coding: utf-8 -*-
import json
from decimal import Decimal
from django.contrib.contenttypes import generic
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.functional import cached_property
from django_extensions.db.fields import AutoSlugField
from model_utils import Choices
from model_utils.models import TimeStampedModel
from open_coesione.models import File, Link
from managers import ProgettoManager, FullProgettoManager, TemaManager, ClassificazioneAzioneManager, ProgrammaManager
from soggetti.models import Soggetto
from territori.models import Territorio


class ClassificazioneBase(models.Model):
    TIPO = Choices()

    classificazione_superiore = models.ForeignKey('self', default=None, related_name='classificazione_set', db_column='classificazione_superiore', null=True, blank=True)
    codice = models.CharField(max_length=32, primary_key=True)
    descrizione = models.TextField()
    tipo_classificazione = models.CharField(max_length=32, choices=TIPO)

    @property
    def classificazioni_figlie(self):
        return self.classificazione_set

    @property
    def progetti(self):
        return self.progetto_set

    def __unicode__(self):
        return u'{} {}'.format(self.codice, self.descrizione)

    class Meta:
        abstract = True


class ProgrammaBase(ClassificazioneBase):
    descrizione_estesa = models.TextField(null=True, blank=True)
    dotazione_totale = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    documenti = generic.GenericRelation(File)
    collegamenti = generic.GenericRelation(Link)

    objects = ProgrammaManager()

    @property
    def programma(self):
        p = self
        while p.classificazione_superiore is not None:
            p = p.classificazione_superiore
        return p

    @property
    def is_root(self):
        return self.tipo_classificazione == self.TIPO.programma

    def get_absolute_url(self):
        return reverse('progetti_programma', kwargs={'codice': self.codice})

    def __unicode__(self):
        return u'{}'.format(self.descrizione[0:100])

    class Meta:
        abstract = True


class ProgrammaAsseObiettivo(ProgrammaBase):
    TIPO = Choices(
        ('PROGRAMMA_FS', 'programma', u'Programma FS'),
        ('ASSE', 'asse', u'Asse'),
        ('OBIETTIVO_OPERATIVO', 'obiettivo', u'Obiettivo operativo'),
    )

    @property
    def progetti_di_programma(self):
        """
        All progetti are classified by programmi of type obiettivo.
        This method returns all progetti that have the root program equal to the one selected.

        It only works with root programmi.
        """
        if self.is_root:
            return Progetto.objects.filter(programma_asse_obiettivo__classificazione_superiore__classificazione_superiore=self)
        else:
            raise Exception('This property is not available for Asse or Obiettivo classifications.')

    class Meta(ProgrammaBase.Meta):
        verbose_name_plural = 'Programmi - Assi - Obiettivi operativi'
        db_table = 'progetti_programma_asse_obiettivo'


class ProgrammaLineaAzione(ProgrammaBase):
    """
    Classificazione alternativa a ProgrammaAsseObiettivo, per progetti in attuazione nel contesto FSC.
    """
    TIPO = Choices(
        ('PROGRAMMA', 'programma', u'Programma'),
        ('LINEA', 'linea', u'Linea'),
        ('AZIONE', 'azione', u'Azione'),
    )

    @property
    def progetti_di_programma(self):
        """
        All progetti are classified by programmi of type azione.
        This method returns all progetti that have the root program equal to the one selected.

        It only works with root programmi.
        """
        if self.is_root:
            return Progetto.objects.filter(programma_linea_azione__classificazione_superiore__classificazione_superiore=self)
        else:
            raise Exception('This property is not available for Linea or Azione classifications.')

    class Meta(ProgrammaBase.Meta):
        verbose_name_plural = 'Programmi - Linee - Azioni'
        db_table = 'progetti_programma_linea_azione'


class ClassificazioneAzione(ClassificazioneBase):
    TIPO = Choices(
        ('natura', 'Natura'),
        ('tipologia', 'Tipologia'),
    )

    descrizione_estesa = models.TextField(null=True, blank=True)
    short_label = models.CharField(max_length=64, blank=True, null=True)
    slug = AutoSlugField(populate_from='descrizione', max_length=64, unique=True, db_index=True, null=True)
    priorita = models.PositiveSmallIntegerField(default=0, verbose_name='Priorità')

    objects = ClassificazioneAzioneManager()

    @property
    def is_root(self):
        return self.tipo_classificazione == self.TIPO.natura

    def costo_totale(self, territorio=None):
        if self.is_root:
            prefix = 'progetto_set__'
            query_set = self.classificazioni_figlie
        else:
            prefix = ''
            query_set = self.progetti

        if territorio:
            query_set = query_set.filter(**territorio.get_cod_dict('{}territorio_set__'.format(prefix)))

        return query_set.aggregate(totale=models.Sum('{}fin_totale_pubblico'.format(prefix)))['totale'] or 0.0

    def get_absolute_url(self):
        return reverse('progetti_tipologia', kwargs={'slug': self.slug})

    class Meta:
        verbose_name_plural = 'Classificazioni azioni'
        db_table = 'progetti_classificazione_azione'
        ordering = ['priorita', 'short_label', 'codice']


class ClassificazioneOggetto(ClassificazioneBase):
    TIPO = Choices(
        ('settore', 'Settore'),
        ('sottosettore', 'Sotto settore'),
        ('categoria', 'Categoria'),
    )

    class Meta:
        verbose_name_plural = 'Classificazioni oggetti'
        db_table = 'progetti_classificazione_oggetto'


class ClassificazioneQSN(ClassificazioneBase):
    TIPO = Choices(
        ('PRIORITA', 'priorita', u'Priorità'),
        ('OBIETTIVO_GENERALE', 'generale', u'Obiettivo generale'),
        ('OBIETTIVO_SPECIFICO', 'specifico', u'Obiettivo specifico')
    )

    class Meta:
        verbose_name = 'Classificazione QSN'
        verbose_name_plural = 'Classificazioni QSN'
        db_table = 'progetti_classificazione_qsn'


class Tema(models.Model):
    TIPO = Choices(
        ('sintetico', 'Sintetico'),
        ('prioritario', 'Prioritario'),
    )

    tema_superiore = models.ForeignKey('self', default=None, related_name='tema_set', db_column='tema_superiore', null=True, blank=True)
    codice = models.CharField(max_length=16, primary_key=True)
    descrizione = models.CharField(max_length=255)
    descrizione_estesa = models.TextField(null=True, blank=True)
    short_label = models.CharField(max_length=64, blank=True, null=True)
    tipo_tema = models.CharField(max_length=16, choices=TIPO)
    slug = AutoSlugField(populate_from='descrizione', max_length=64, unique=True, db_index=True, null=True)
    priorita = models.PositiveSmallIntegerField(default=0, verbose_name='Priorità')

    objects = TemaManager()

    @property
    def temi_figli(self):
        return self.tema_set

    @property
    def progetti(self):
        return self.progetto_set

    @property
    def is_root(self):
        return self.tipo_tema == self.TIPO.sintetico

    def totale_pro_capite(self, territorio_or_popolazione):
        if isinstance(territorio_or_popolazione, (int, float)):
            popolazione = territorio_or_popolazione
            costo = self.costo_totale()
        else:
            popolazione = territorio_or_popolazione.popolazione_totale or 0.0
            costo = self.costo_totale(territorio_or_popolazione) or 0.0
        if not popolazione:
            return 0.0
        return float(costo) / float(popolazione)

    def costo_totale(self, territorio=None):
        cache_key = ['costo_totale']
        if self.is_root:
            prefix = 'progetto_set__'
            query_set = self.temi_figli
        else:
            prefix = ''
            query_set = self.progetti
        cache_key.append(str(self.codice))

        if territorio:
            query_set = query_set.filter(**territorio.get_cod_dict('{}territorio_set__'.format(prefix)))
            cache_key.append(str(territorio.pk))

        cache_key = '.'.join(cache_key)
        result = cache.get(cache_key)
        if result is None:
            result = query_set.aggregate(totale=models.Sum('{}fin_totale_pubblico'.format(prefix)))['totale'] or 0.0
            cache.set(cache_key, result)
        return result

    def get_absolute_url(self):
        return reverse('progetti_tema', kwargs={'slug': self.slug})

    def __unicode__(self):
        return u'{} {}'.format(self.codice, self.descrizione)

    class Meta:
        verbose_name_plural = 'Temi'
        ordering = ['priorita', 'codice']


class Fonte(models.Model):
    TIPO = Choices(
        ('FS', 'fs', 'FS'),
        ('FSC', 'fsc', 'FSC'),
        ('PAC', 'pac', 'PAC')
    )

    tipo_fonte = models.CharField(max_length=4, choices=TIPO, blank=True, null=True)
    codice = models.CharField(max_length=8, primary_key=True)
    descrizione = models.TextField()
    short_label = models.CharField(max_length=64, blank=True, null=True)

    @property
    def progetti(self):
        return self.progetto_set

    def __unicode__(self):
        return u'{} - {}'.format(self.codice, self.descrizione)

    class Meta:
        verbose_name = 'Fonte'
        verbose_name_plural = 'Fonti'


class Progetto(models.Model):
    TIPI_PROGETTO = Choices(
        ('PM', 'progetto_monitorato', u'Progetto monitorato'),
        ('CIPE', 'assegnazione_cipe', u'Assegnazione CIPE'),
    )
    DPS_FLAG_CUP = Choices(
        ('0', u'CUP non valido'),
        ('1', u'CUP valido'),
        ('2', u'CUP presente')
    )
    DPS_FLAG_PRESENZA_DATE = Choices(
        ('00', u'Date inizio e fine non presenti'),
        ('10', u'Data inizio previsto presente'),
        ('11', u'Date inizio e fine previste, presenti'),
        ('12', u'Data inizio previsto e date fine prevista ed effettiva, presenti'),
        ('20', u'Date inizio previsto ed effettivo presenti, date fine assenti'),
        ('21', u'Date inizio previsto ed effettivo, e data fine prevista presenti'),
        ('22', u'Tutte le date presenti'),
    )
    DPS_FLAG_COERENZA_DATE = Choices(
        ('0', u'Durata incoerente (fine < inizio)'),
        ('1', u'Durata coerente (fine > inizio)'),
        ('2', u'Durata non valutabile (inizio e/o fine mancanti)'),
    )
    FONDO_COMUNITARIO = Choices(
        ('fesr', 'FESR'),
        ('fse', 'FSE')
    )
    TIPO_OPERAZIONE = Choices(
        ('1', 'opere_pubbliche', u'Realizzazione di opere pubbliche'),
        ('2', 'beni_servizi', u'Acquisizione  di beni e servizi'),
        ('3', 'finanziamenti', u'Erogazione di finanziamenti e aiuti a imprese e individui'),
    )
    OBIETTIVO_SVILUPPO = Choices(
        ('COMPETITIVITA', 'competitivita', u'Competitività regionale e occupazione'),
        ('CONVERGENZA', 'convergenza', u'Convergenza'),
        ('COOPERAZIONE', 'cooperazione', u'Cooperazione territoriale europea')
    )
    ACTIVE_FLAG = Choices(
        (1, 'attivo', u'Attivo'),
        (0, 'inattivo', u'Non attivo')
    )
    DPS_FLAG_PAC = Choices(
        ('0', u'Il progetto non appartiene al PAC'),
        ('1', u'Il progetto appartiene al PAC ed è finanziato con risorse dedicate, al di fuori dei Programmi Operativi'),
        ('2', u"Il progetto appartiene al PAC ed è finanziato nell'ambito dei Programmi Operativi"),
    )
    STATO = Choices(
        ('0', 'non_applicabile', u'Non applicabile'),
        ('1', 'non_avviato', u'Non avviato'),
        ('2', 'in_corso', u'In corso'),
        ('3', 'liquidato', u'Liquidato'),
        ('4', 'concluso', u'Concluso'),
    )

    codice_locale = models.CharField(max_length=100, unique=True, db_index=True, db_column='cod_locale_progetto')

    cup = models.CharField(max_length=15, blank=True)
    active_flag = models.BooleanField(default=True, db_index=True)

    progetti_attuati = models.ManyToManyField('self', symmetrical=False, related_name='progetti_attuatori')

    titolo_progetto = models.TextField()
    slug = models.SlugField(max_length=128, blank=True, null=True, unique=True, db_index=True)

    descrizione = models.TextField(blank=True, null=True)

    descrizione_fonte_nome = models.TextField(blank=True, null=True)
    descrizione_fonte_url = models.URLField(blank=True, null=True)

    classificazione_qsn = models.ForeignKey('ClassificazioneQSN', related_name='progetto_set', null=True, blank=True, db_column='classificazione_qsn')
    programma_asse_obiettivo = models.ForeignKey('ProgrammaAsseObiettivo', related_name='progetto_set', null=True, blank=True, db_column='programma_asse_progetto')
    programma_linea_azione = models.ForeignKey('ProgrammaLineaAzione', related_name='progetto_set', null=True, blank=True, db_column='programma_linea_azione')

    obiettivo_sviluppo = models.CharField(max_length=16, blank=True, null=True, choices=OBIETTIVO_SVILUPPO)
    tipo_operazione = models.IntegerField(blank=True, null=True, choices=TIPO_OPERAZIONE)
    fondo_comunitario = models.CharField(max_length=4, blank=True, null=True, choices=FONDO_COMUNITARIO)
    tema = models.ForeignKey('Tema', related_name='progetto_set', null=True, blank=True, db_column='tema')

    fonte_set = models.ManyToManyField('Fonte', related_name='progetto_set', db_table='progetti_progetto_has_fonte')

    classificazione_azione = models.ForeignKey('ClassificazioneAzione', related_name='progetto_set', null=True, blank=True, db_column='classificazione_azione')
    classificazione_oggetto = models.ForeignKey('ClassificazioneOggetto', related_name='progetto_set', null=True, blank=True, db_column='classificazione_oggetto')

    cipe_flag = models.BooleanField(default=False)

    note = models.TextField(null=True, blank=True)

    fin_totale = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    fin_totale_pubblico = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True, db_index=True)
    fin_totale_pubblico_netto = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True, db_index=True)
    economie_totali = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True, db_index=True)
    economie_totali_pubbliche = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True, db_index=True)

    fin_ue = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    fin_stato_pac = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    fin_stato_fondo_rotazione = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    fin_stato_fsc = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    fin_stato_altri_provvedimenti = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    fin_regione = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    fin_provincia = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    fin_comune = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    fin_risorse_liberate = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    fin_altro_pubblico = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    fin_stato_estero = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    fin_privato = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    fin_da_reperire = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    costo = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    costo_rendicontabile_ue = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    pagamento = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    pagamento_rendicontabile_ue = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    pagamento_fsc = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    pagamento_pac = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    data_inizio_prevista = models.DateField(null=True, blank=True)
    data_fine_prevista = models.DateField(null=True, blank=True)
    data_inizio_effettiva = models.DateField(null=True, blank=True)
    data_fine_effettiva = models.DateField(null=True, blank=True)
    data_aggiornamento = models.DateField(null=True, blank=True)
    data_ultimo_rilascio = models.DateField(null=True, blank=True)

    dps_flag_cup = models.CharField(max_length=1, choices=DPS_FLAG_CUP)
    dps_flag_presenza_date = models.CharField(max_length=2, choices=DPS_FLAG_PRESENZA_DATE, null=True, blank=True)
    dps_flag_date_previste = models.CharField(max_length=1, choices=DPS_FLAG_COERENZA_DATE, null=True, blank=True)
    dps_flag_date_effettive = models.CharField(max_length=1, choices=DPS_FLAG_COERENZA_DATE, null=True, blank=True)

    dps_flag_pac = models.CharField(max_length=1, choices=DPS_FLAG_PAC, default='0')

    privacy_flag = models.BooleanField(default=False)

    stato_progetto = models.CharField(max_length=1, choices=STATO, null=True, blank=True, db_index=True)
    stato_finanziario = models.CharField(max_length=1, choices=STATO, null=True, blank=True)

    csv_data = models.TextField()

    territorio_set = models.ManyToManyField('territori.Territorio', through='Localizzazione')
    soggetto_set = models.ManyToManyField('soggetti.Soggetto', null=True, blank=True, through='Ruolo')

    objects = ProgettoManager()
    fullobjects = FullProgettoManager()

    @property
    def costo_ammesso(self):
        # backward compatibility
        return self.costo_rendicontabile_ue

    @property
    def pagamento_ammesso(self):
        # backward compatibility
        return self.pagamento_rendicontabile_ue

    @property
    def tipo_progetto(self):
        if self.cipe_flag:
            return self.TIPI_PROGETTO.assegnazione_cipe
        else:
            return self.TIPI_PROGETTO.progetto_monitorato

    @property
    def fonti(self):
        return self.fonte_set.all()

    def fonte_fs_qs(self):
        return self.fonte_set.filter(tipo_fonte=Fonte.TIPO.fs)

    def fonte_fsc_qs(self):
        return self.fonte_set.filter(tipo_fonte=Fonte.TIPO.fsc)

    def fonte_pac_qs(self):
        return self.fonte_set.filter(tipo_fonte=Fonte.TIPO.pac)

    @property
    def is_fonte_fs_flag(self):
        return self.fonte_fs_qs().count() > 0

    @property
    def is_fonte_fsc_flag(self):
        return self.fonte_fsc_qs().count() > 0

    @property
    def is_fonte_pac_flag(self):
        return self.fonte_pac_qs().count() > 0

    @property
    def fonte_fs_descrizione(self):
        if self.is_fonte_fs_flag:
            return self.fonte_fs_qs()[0].descrizione

    @property
    def fonte_fs_label(self):
        if self.is_fonte_fs_flag:
            return self.fonte_fs_qs()[0].short_label

    @property
    def fonte_fsc_label(self):
        if self.is_fonte_fsc_flag:
            return self.fonte_fsc_qs()[0].short_label

    @property
    def fonte_fsc_descrizione(self):
        if self.is_fonte_fsc_flag:
            return self.fonte_fsc_qs()[0].descrizione

    @property
    def fonte_pac_label(self):
        if self.is_fonte_pac_flag:
            return self.fonte_pac_qs()[0].short_label

    @property
    def fonte_pac_descrizione(self):
        if self.is_fonte_pac_flag:
            return self.fonte_pac_qs()[0].descrizione

    @property
    def fonte_fs_codice(self):
        if self.is_fonte_fs_flag:
            return self.fonte_fs_qs()[0].codice

    @property
    def fonte_fsc_codice(self):
        if self.is_fonte_fsc_flag:
            return self.fonte_fsc_qs()[0].codice

    @property
    def fonte_pac_codice(self):
        if self.is_fonte_pac_flag:
            return self.fonte_pac_qs()[0].codice

    @property
    def territori(self):
        return self.territorio_set.all()

    @property
    def soggetti(self):
        return self.soggetto_set.all()

    @property
    def programmatori(self):
        return self.soggetto_set.filter(ruolo__ruolo=Ruolo.RUOLO.programmatore)

    @property
    def attuatori(self):
        return self.soggetto_set.filter(ruolo__ruolo=Ruolo.RUOLO.attuatore)

    @property
    def regioni(self):
        """
        Return the set of regional codes, for the localization of a project
        """
        return set([t.cod_reg for t in self.territori])

    @property
    def segnalazioni(self):
        return SegnalazioneProgetto.objects.filter(cup=self.cup, pubblicato=True)

    @cached_property
    def pagamenti(self):
        return self.pagamentoprogetto_set.all()

    @property
    def ultimo_aggiornamento(self):
        """
        la data_aggiornamento potrebbe essere obsoleta rispetto ai pagamenti
        """
        pagamenti = self.pagamenti
        if not pagamenti and self.data_aggiornamento:
            return self.data_aggiornamento
        return max(self.data_aggiornamento, *[p.data for p in pagamenti])

    @property
    def percentuale_pagamenti(self):
        if not self.fin_totale_pubblico_netto or not self.pagamento:
            return 0.0
        return (float(self.pagamento) or 0.0) / (float(self.fin_totale_pubblico_netto) or 0.0) * 100.0

    def delibere_cipe(self):
        return self.deliberacipe_set.all()

    @property
    def assegnazioni_delibere(self):
        return self.progettodeliberacipe_set.all()

    @property
    def fonte_fin(self):
        """
        Return the first level of programma (asse-obiettivo/linea-azione) classification which is used in the fonte_fin filtering of search results
        """
        if self.programma_asse_obiettivo:
            return self.programma_asse_obiettivo.programma
        elif self.programma_linea_azione:
            return self.programma_linea_azione.programma
        else:
            return None

    @property
    def fonti_fin(self):
        """
        Return an array with the first levels of programma_(asse-obiettivo/linea-azione) classifications which is used in the fonte_fin filtering of search results
        """
        fonti_fin = []
        if self.programma_asse_obiettivo:
            fonti_fin.append(self.programma_asse_obiettivo.programma)
        if self.programma_linea_azione:
            fonti_fin.append(self.programma_linea_azione.programma)

        return fonti_fin

    @property
    def get_tipo_progetto_display(self):
        # per csv
        return dict(self.TIPI_PROGETTO)[self.tipo_progetto]

    @property
    def nomi_programmatori(self):
        # per csv
        return [r.soggetto.denominazione for r in self.ruolo_set.all() if r.ruolo == Ruolo.RUOLO.programmatore]

    @property
    def nomi_attuatori(self):
        # per csv
        return [r.soggetto.denominazione for r in self.ruolo_set.all() if r.ruolo == Ruolo.RUOLO.attuatore]

    @property
    def nomi_territori(self):
        # per csv
        return set([t.nome_con_provincia for t in self.territori])

    @property
    def ambiti_territoriali(self):
        # per csv
        return set([t.ambito_territoriale for t in self.territori])

    def get_absolute_url(self):
        return reverse('progetti_progetto', kwargs={'slug': self.slug})

    def update(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)
        self.save()

        return self

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.slug is None:
            original_slug = slugify(u'{}'.format(self.codice_locale))

            cnt = 0
            slug = original_slug
            while not slug or Progetto.fullobjects.exclude(pk=self.pk).filter(slug=slug):
                cnt += 1
                slug = u'{}-{}'.format(original_slug, cnt)

            self.slug = slug

        super(Progetto, self).save(force_insert, force_update, using, update_fields)

    def __unicode__(self):
        return u'{}'.format(self.codice_locale)

    class Meta:
        verbose_name_plural = 'Progetti'


class ProgettoDeliberaCIPE(models.Model):
    """
    Tabella di collegamento tra i progetti e le delibere
    """
    progetto = models.ForeignKey(Progetto)
    delibera = models.ForeignKey('DeliberaCIPE')
    finanziamento = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    note = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return u'p:{} - d:{}'.format(self.progetto, self.delibera)


class DeliberaCIPE(models.Model):
    """
    Contiene tutte le delibere CIPE
    """
    num = models.IntegerField(unique=True, db_index=True)
    anno = models.CharField(max_length=4, null=True, blank=True)
    data_adozione = models.DateField(null=True, blank=True)
    data_pubblicazione = models.DateField(null=True, blank=True)
    oggetto = models.TextField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    fondi_assegnati = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    progetto_set = models.ManyToManyField(Progetto, through=ProgettoDeliberaCIPE)

    def __unicode__(self):
        return u'{}_{}'.format(self.num, self.anno)

    class Meta:
        verbose_name = 'Delibera CIPE'
        verbose_name_plural = 'Delibere CIPE'
        ordering = ['-anno', '-num']


class CUP(models.Model):
    """
    CUP can be multiple (sic!)
    A project may, after being assigned a CUP at the start, be splitted into several sections, each of which will get its own CUP.
    """
    progetto = models.ForeignKey(Progetto, related_name='cups_progetto')
    cup = models.CharField(max_length=15)

    def __unicode__(self):
        return u'{} - {}'.format(self.progetto, self.cup)

    class Meta:
        verbose_name_plural = 'CUP'


class Localizzazione(models.Model):
    DPS_FLAG_CAP = Choices(
        ('0', 'CAP non valido o incoerente con territorio'),
        ('1', 'CAP valido e coerente'),
        ('2', 'CAP mancante o territorio nazionale o estero'),
    )

    progetto = models.ForeignKey(Progetto)
    territorio = models.ForeignKey(Territorio)
    indirizzo = models.CharField(max_length=550, blank=True, null=True)
    cap = models.CharField(max_length=5, blank=True, null=True)
    dps_flag_cap = models.CharField(max_length=1, choices=DPS_FLAG_CAP, default='0')

    def __unicode__(self):
        return u'{} {} ({})'.format(self.progetto, self.territorio, self.dps_flag_cap)

    class Meta:
        verbose_name_plural = 'Localizzazioni'


class Ruolo(models.Model):
    """
    The role of the recipient in the project.
    """
    RUOLO = Choices(
        ('1', 'programmatore', 'Programmatore'),
        ('2', 'attuatore', 'Attuatore'),
    )

    progetto = models.ForeignKey(Progetto)
    soggetto = models.ForeignKey(Soggetto)
    ruolo = models.CharField(max_length=1, choices=RUOLO)
    progressivo_ruolo = models.PositiveSmallIntegerField(null=True, blank=True)
    # codice_progetto = models.CharField(max_length=100, db_index=True)

    @classmethod
    def inv_ruoli_dict(cls):
        # build an inverse dictionary for the ruoli, code => descr
        return {v: k for k, v in cls.RUOLO._choice_dict.iteritems()}

    @property
    def soggetti(self):
        return self.soggetto_set.all()

    @property
    def progetti(self):
        return self.progetto_set.all()

    def __unicode__(self):
        return u'{}, {} nel progetto {}'.format(self.soggetto, self.get_ruolo_display(), self.progetto)

    class Meta:
        verbose_name = 'Ruolo'
        verbose_name_plural = 'Ruoli'
        unique_together = (
            ('progetto', 'soggetto', 'ruolo'),
            ('progetto', 'ruolo', 'progressivo_ruolo'),
        )
        index_together = [
            ['progetto', 'soggetto', 'ruolo'],
            ['progetto', 'ruolo', 'progressivo_ruolo'],
        ]


class PagamentoProgetto(models.Model):
    progetto = models.ForeignKey(Progetto, related_name='pagamentoprogetto_set')
    data = models.DateField()
    ammontare = models.DecimalField(max_digits=14, decimal_places=2)
    ammontare_fsc = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    ammontare_pac = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    ammontare_rendicontabile_ue = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    @property
    def percentuale(self):
        fin_totale_pubblico_netto = self.progetto.fin_totale_pubblico_netto or self.progetto.fin_totale_pubblico or 0
        return (self.ammontare / fin_totale_pubblico_netto) * Decimal(100) if fin_totale_pubblico_netto else 0.0

    def __unicode__(self):
        return u'Pagamento del progetto {} del {} di {}'.format(self.progetto, self.data, self.ammontare)

    class Meta:
        verbose_name = 'Pagamento progetto'
        verbose_name_plural = 'Pagamenti progetti'
        ordering = ['data']


class SegnalazioneProgetto(TimeStampedModel):
    TIPOLOGIA_FINANZIATORE = 'FINAZIATORE'
    TIPOLOGIA_ATTUATORE = 'ATTUATORE'
    TIPOLOGIA_REALIZZATORE = 'REALIZZATORE'
    TIPOLOGIA_OSSERVATORE = 'OSSERVATORE'
    TIPOLOGIA_ALTRO = 'ALTRO'

    TIPOLOGIE = (
        (TIPOLOGIA_FINANZIATORE, "Faccio parte dell'amministrazione che programma e finanzia"),
        (TIPOLOGIA_ATTUATORE, "Faccio parte dell'organizzazione che gestisce l'attuazione del progetto"),
        (TIPOLOGIA_REALIZZATORE, 'Lavoro / ho lavorato per la realizzazione del progetto'),
        (TIPOLOGIA_OSSERVATORE, 'Abito lì vicino'),
        (TIPOLOGIA_ALTRO, 'Conosco il progetto per un altro motivo'),
    )

    pubblicato = models.BooleanField(default=False)

    come_lo_conosci = models.CharField(choices=TIPOLOGIE, max_length=12, verbose_name='Come conosci il progetto?*')
    come_lo_conosci_altro = models.TextField(verbose_name='Specificare come hai conosciuto il progetto', blank=True, null=True)

    cup = models.CharField(max_length=15, verbose_name='Codice del progetto*')
    is_cipe = models.BooleanField(default=False, verbose_name='Progetto CIPE')
    organizzazione = models.CharField(max_length=255, verbose_name='Amministrazione o altra organizzazione*')
    utente = models.CharField(max_length=255, verbose_name='Nome e cognome*')
    email = models.EmailField(verbose_name='E-mail*')
    descrizione = models.TextField(verbose_name='Racconto del progetto*')
    come_migliorare = models.TextField(blank=True, null=True, verbose_name='Come si potrebbe migliorare?*')

    risultati_conseguiti = models.TextField(blank=True, null=True)
    effetti_sul_territorio = models.TextField(blank=True, null=True)
    cosa_piace = models.TextField(blank=True, null=True, verbose_name='Cosa ti è piaciuto di più?')
    cosa_non_piace = models.TextField(blank=True, null=True, verbose_name='Cosa ti è piaciuto di meno?')
    quanto_utile = models.TextField(blank=True, null=True, verbose_name='Per cosa è stato utile il progetto?')

    @property
    def progetto(self):
        return Progetto.objects.get(cup=self.cup)

    def __unicode__(self):
        return u'{} su {}'.format(self.email, self.cup)

    class Meta:
        verbose_name = 'Segnalazione'
        verbose_name_plural = 'Segnalazioni'
