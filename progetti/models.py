# -*- coding: utf-8 -*-

from django.db import models
from model_utils import Choices
from progetti.managers import ProgettiManager, TemiManager, ClassificazioneAzioneManager
from soggetti.models import Soggetto


class ClassificazioneQSN(models.Model):
    TIPO = Choices(
        ('PRIORITA', 'priorita', u'Priorità'),
        ('OBIETTIVO_GENERALE', 'generale', u'Obiettivo generale'),
        ('OBIETTIVO_SPECIFICO', 'specifico', u'Obiettivo specifico')
    )
    classificazione_superiore = models.ForeignKey('ClassificazioneQSN', default=None,
                                                  related_name='classificazione_set',
                                                  db_column='classificazione_superiore', null=True, blank=True)
    codice = models.CharField(max_length=16, primary_key=True)
    descrizione = models.TextField()
    tipo_classificazione = models.CharField(max_length=32, choices=TIPO)

    @property
    def classificazioni_figlie(self):
        return self.classificazione_set

    @property
    def progetti(self):
        return self.progetto_set

    def __unicode__(self):
        return self.codice

    class Meta:
        verbose_name = "Classificazione QSN"
        verbose_name_plural = "Classificazioni QSN"
        db_table = 'progetti_classificazione_qsn'


class ProgrammaAsseObiettivo(models.Model):
    TIPO = Choices(
        ('PROGRAMMA_FS', 'programma', u'Programma FS'),
        ('ASSE', 'asse', u'Asse'),
        ('OBIETTIVO_OPERATIVO', 'obiettivo', u'Obiettivo operativo')
    )
    classificazione_superiore = models.ForeignKey('ProgrammaAsseObiettivo', default=None,
                                                  related_name='classificazione_set',
                                                  db_column='classificazione_superiore',
                                                  null=True, blank=True)
    codice = models.CharField(max_length=32, primary_key=True)
    descrizione = models.TextField()
    tipo_classificazione = models.CharField(max_length=32, choices=TIPO)
    url_riferimento = models.URLField(max_length=255, blank=True, null=True)

    @property
    def progetti(self):
        return self.progetto_set

    def __unicode__(self):
        return self.codice + " - " + unicode(self.descrizione)

    class Meta:
        verbose_name_plural = "Programmi - Assi - Obiettivi operativi"
        db_table = 'progetti_programma_asse_obiettivo'


class Tema(models.Model):
    TIPO = Choices(
        ('sintetico', 'Sintetico'),
        ('prioritario', 'Prioritario'),
    )
    tema_superiore = models.ForeignKey('Tema', default=None,
                                       related_name='tema_set',
                                       db_column='tema_superiore', null=True, blank=True)
    codice = models.CharField(max_length=16, primary_key=True)
    descrizione = models.CharField(max_length=255)
    descrizione_estesa = models.TextField(null=True, blank=True)
    short_label = models.CharField(max_length=64, blank=True, null=True)
    tipo_tema = models.CharField(max_length=16, choices=TIPO)
    slug = models.CharField(max_length=64, blank=True, null=True)

    objects = TemiManager()

    @property
    def temi_figli(self):
        return self.tema_set

    @property
    def progetti(self):
        return self.progetto_set

    @property
    def is_root(self):
        return self.tipo_tema == Tema.TIPO.sintetico

    def costo_totale(self, territorio=None ):
        if self.is_root:
            prefix = 'progetto_set__'
            query_set = self.temi_figli
        else:
            prefix = ''
            query_set = self.progetti

        if territorio:
            query_set = query_set.filter( **territorio.get_cod_dict('{0}territorio_set__'.format(prefix) ) )

        return query_set.aggregate(totale=models.Sum('{0}fin_totale_pubblico'.format(prefix)) )['totale'] or 0.0

    @models.permalink
    def get_absolute_url(self):
        return ('progetti_tema', (), {
            'slug' : self.slug
        })

    def __unicode__(self):
        return u'%s %s' % (self.codice, self.descrizione)

    class Meta:
        verbose_name_plural = "Temi"
        ordering = ['short_label','codice']

class Intesa(models.Model):
    codice = models.CharField(max_length=8, primary_key=True)
    descrizione = models.TextField()

    @property
    def progetti(self):
        return self.progetto_set


    def __unicode__(self):
        return self.codice + " - " + self.descrizione

    class Meta:
        verbose_name = "Intesa istituzionale"
        verbose_name_plural = "Intese istituzionali"

class Fonte(models.Model):
    codice = models.CharField(max_length=8, primary_key=True)
    descrizione = models.TextField()

    @property
    def progetti(self):
        return self.progetto_set


    def __unicode__(self):
        return self.codice + " - " + self.descrizione

    class Meta:
        verbose_name = "Fonte"
        verbose_name_plural = "Fonti"


class ClassificazioneAzione(models.Model):

    objects = ClassificazioneAzioneManager()

    TIPO = Choices(
        ('natura', 'Natura'),
        ('tipologia', 'Tipologia'),
    )
    classificazione_superiore = models.ForeignKey('ClassificazioneAzione', default=None,
                                                  related_name='classificazione_set',
                                                  db_column='classificazione_superiore', null=True, blank=True)
    codice = models.CharField(max_length=8, primary_key=True)
    descrizione = models.TextField()
    short_label = models.CharField(max_length=64, blank=True, null=True)
    tipo_classificazione = models.CharField(max_length=16, choices=TIPO)
    slug = models.CharField(max_length=64, blank=True, null=True)

    @property
    def classificazioni_figlie(self):
        return self.classificazione_set

    @property
    def progetti(self):
        return self.progetto_set

    @property
    def is_root(self):
        return self.tipo_classificazione == ClassificazioneAzione.TIPO.natura

    def costo_totale(self, territorio=None ):
        if self.is_root:
            prefix = 'progetto_set__'
            query_set = self.classificazioni_figlie
        else:
            prefix = ''
            query_set = self.progetti

        if territorio:
            query_set = query_set.filter( **territorio.get_cod_dict('{0}territorio_set__'.format(prefix) ) )

        return query_set.aggregate(totale=models.Sum('{0}fin_totale_pubblico'.format(prefix)) )['totale'] or 0.0

    @models.permalink
    def get_absolute_url(self):
        return ('progetti_tipologia', (), {
            'slug' : self.slug
        })

    def __unicode__(self):
        return u'%s %s' % (self.codice, self.descrizione)

    class Meta:
        verbose_name_plural = "Classificazioni azioni"
        db_table = 'progetti_classificazione_azione'
        ordering = ['short_label','codice']


class ClassificazioneOggetto(models.Model):
    TIPO = Choices(
        ('settore', 'Settore'),
        ('sottosettore', 'Sotto settore'),
        ('categoria', 'Categoria'),
    )
    classificazione_superiore = models.ForeignKey('ClassificazioneOggetto', default=None,
                                                  related_name='classificazione_set',
                                                  db_column='classificazione_superiore', null=True, blank=True)
    codice = models.CharField(max_length=16, primary_key=True)
    descrizione = models.TextField()
    tipo_classificazione = models.CharField(max_length=16, choices=TIPO)

    @property
    def classificazioni_figlie(self):
        return self.classificazione_set

    @property
    def progetti(self):
        return self.progetto_set

    def __unicode__(self):
        return u'%s %s' % (self.codice, self.descrizione)

    class Meta:
        verbose_name_plural = "Classificazioni oggetti"
        db_table = 'progetti_classificazione_oggetto'
        ordering = ['codice']




class Progetto(models.Model):

    objects = ProgettiManager()    # override the default manager

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

    codice_locale = models.CharField(max_length=100, primary_key=True,
                                     db_column='cod_locale_progetto')
    cup = models.CharField(max_length=15)
    titolo_progetto = models.TextField()
    descrizione = models.TextField(blank=True, null=True)
    slug = models.CharField(max_length=128, blank=True, null=True)
    classificazione_qsn = models.ForeignKey('ClassificazioneQSN',
                                            related_name='progetto_set',
                                            db_column='classificazione_qsn')

    programma_asse_obiettivo = models.ForeignKey('ProgrammaAsseObiettivo',
                                                 related_name='progetto_set',
                                                 db_column='programma_asse_progetto')

    obiettivo_sviluppo = models.CharField(max_length=16,
                                          blank=True, null=True,
                                          choices=OBIETTIVO_SVILUPPO)
    tipo_operazione = models.IntegerField(blank=True, null=True, choices=TIPO_OPERAZIONE)
    fondo_comunitario = models.CharField(max_length=4,
                                         blank=True, null=True,
                                         choices=FONDO_COMUNITARIO)
    tema = models.ForeignKey('Tema',
                             related_name='progetto_set',
                             db_column='tema')

#    intesa_istituzionale = models.ForeignKey('Intesa',
#                                             related_name='progetto_set',
#                                             db_column='intesa_istituzionale')
    fonte = models.ForeignKey('Fonte',
                              related_name='progetto_set',
                              db_column='fonte')

    classificazione_azione = models.ForeignKey('ClassificazioneAzione',
                                               related_name='progetto_set',
                                               db_column='classificazione_azione')

    classificazione_oggetto = models.ForeignKey('ClassificazioneOggetto',
                                                related_name='progetto_set',
                                                db_column='classificazione_oggetto')


    fin_totale = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    fin_totale_pubblico = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    fin_ue = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    fin_stato_fondo_rotazione = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    fin_stato_fsc = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    fin_stato_altri_provvedimenti = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    fin_regione = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    fin_provincia = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    fin_comune = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    fin_altro_pubblico = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    fin_stato_estero = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    fin_privato = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    fin_da_reperire = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    costo = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    costo_ammesso = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    pagamento = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    pagamento_fsc = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    pagamento_ammesso = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    data_inizio_prevista = models.DateField(null=True, blank=True)
    data_fine_prevista = models.DateField(null=True, blank=True)
    data_inizio_effettiva = models.DateField(null=True, blank=True)
    data_fine_effettiva = models.DateField(null=True, blank=True)
    data_inizio_info = models.IntegerField(null=True, blank=True)
    data_aggiornamento = models.DateField(null=True, blank=True)

    dps_flag_cup = models.CharField(max_length=1, choices=DPS_FLAG_CUP)
    dps_flag_presenza_date = models.CharField(max_length=2, choices=DPS_FLAG_PRESENZA_DATE)
    dps_flag_date_previste = models.CharField(max_length=1, choices=DPS_FLAG_COERENZA_DATE)
    dps_flag_date_effettive = models.CharField(max_length=1, choices=DPS_FLAG_COERENZA_DATE)

    territorio_set = models.ManyToManyField('territori.Territorio', through='Localizzazione')
    soggetto_set = models.ManyToManyField('soggetti.Soggetto', null=True, blank=True, through='Ruolo')

    @property
    def territori(self):
        return self.territorio_set.all()

    @property
    def soggetti(self):
        return self.soggetto_set.all()

    @property
    def programmatori(self):
        return self.soggetto_set.filter(ruolo=Ruolo.RUOLO.programmatore)

    @property
    def destinatari(self):
        return self.soggetto_set.filter(ruolo=Soggetto.RUOLO.destinatario)

    @property
    def attuatori(self):
        return self.soggetto_set.filter(ruolo=Soggetto.RUOLO.attuatore)

    @property
    def destinatari(self):
        return self.soggetto_set.filter(ruolo=Soggetto.RUOLO.destinatario)

    def __unicode__(self):
        return self.codice_locale

    @models.permalink
    def get_absolute_url(self):
        return ('progetti_progetto', (), {
            'slug': self.slug
        })

    def percentuale_pagamenti(self):
        if not self.fin_totale_pubblico:
            return 0.0
        return (float(self.pagamento) or 0.0) / (float(self.fin_totale_pubblico) or 0.0) * 100.0

    class Meta:
        verbose_name_plural = "Progetti"


class Localizzazione(models.Model):
    DPS_FLAG_CAP = Choices(
        ('0', 'CAP non valido o incoerente con territorio'),
        ('1', 'CAP valido e coerente'),
        ('2', 'CAP mancante o territorio nazionale o estero'),
                                                           )
    territorio = models.ForeignKey('territori.Territorio', verbose_name=u'Territorio')
    progetto = models.ForeignKey(Progetto, db_column='codice_progetto')
    indirizzo = models.CharField(max_length=512, blank=True, null=True)
    cap = models.CharField(max_length=5, blank=True, null=True)
    dps_flag_cap = models.CharField(max_length=1, choices=DPS_FLAG_CAP)

    def __unicode__(self):
        return u"%s %s (%s)" % (self.progetto, self.territorio, self.dps_flag_cap)

    class Meta:
        verbose_name_plural = "Localizzazioni"

class Ruolo(models.Model):
    """
    The role of the recipient in the project.
    """
    RUOLO = Choices(
        ('1', 'programmatore', 'Programmatore'),
        ('2', 'attuatore', 'Attuatore'),
        ('3', 'destinatario', 'Destinatario'),
        ('4', 'realizzatore', 'Realizzatore')
    )
    soggetto = models.ForeignKey('soggetti.Soggetto', verbose_name=u'Soggetto')
    progetto = models.ForeignKey(Progetto, db_column='codice_progetto')
    ruolo = models.CharField(max_length=1, choices=RUOLO)

    @property
    def soggetti(self):
        return self.soggetto_set.all()

    @property
    def progetti(self):
        return self.progetto_set.all()

    def __unicode__(self):
        return u"%s" % (self.get_ruolo_display(),)

    class Meta:
        verbose_name = "Ruolo"
        verbose_name_plural = "Ruoli"


