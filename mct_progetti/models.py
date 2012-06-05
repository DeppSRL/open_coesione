# -*- coding: utf-8 -*-

from django.db import models
from model_utils import Choices

from localita.models import Localita

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

    @property
    def progetti(self):
        return self.progetto_set

    def __unicode__(self):
        return self.codice

    class Meta:
        verbose_name_plural = "Programmi - Assi - Obiettivi operativi"


class Tema(models.Model):
    TIPO = Choices(
        ('sintetico', 'Sintetico'),
        ('prioritario', 'Prioritario'),
    )
    tema_superiore = models.ForeignKey('Tema', default=None,
                                       related_name='tema_set',
                                       db_column='tema_superiore', null=True, blank=True)
    codice = models.CharField(max_length=16, primary_key=True)
    descrizione = models.TextField()
    tipo_tema = models.CharField(max_length=16, choices=TIPO)

    @property
    def temi_figli(self):
        return self.tema_set

    @property
    def progetti(self):
        return self.progetto_set

    def __unicode__(self):
        return self.codice

    class Meta:
        verbose_name_plural = "Temi"

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


class ClassificazioneAzione(models.Model):
    TIPO = Choices(
        ('natura', 'Natura'),
        ('tipologia', 'Tipologia'),
    )
    classificazione_superiore = models.ForeignKey('ClassificazioneAzione', default=None,
                                                  related_name='classificazione_set',
                                                  db_column='classificazione_superiore', null=True, blank=True)
    codice = models.CharField(max_length=8, primary_key=True)
    descrizione = models.TextField()
    tipo_classificazione = models.CharField(max_length=16, choices=TIPO)

    @property
    def classificazioni_figlie(self):
        return self.classificazione_set

    @property
    def progetti(self):
        return self.progetto_set

    def __unicode__(self):
        return self.codice

    class Meta:
        verbose_name_plural = "Classificazioni azioni"


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
        return self.codice

    class Meta:
        verbose_name_plural = "Classificazioni oggetti"

class Progetto(models.Model):
    DPS_FLAG_CUP = Choices(
        ('0', 'CUP non valido'),
        ('1', 'CUP valido'),
        ('2', 'CUP presente')
    )
    DPS_DATE = Choices(
        ('00', 'Date inizio e fine non presenti'),
        ('10', 'Data inizio previsto presente'),
        ('11', 'Date inizio e fine previste, presenti'),
        ('12', 'Data inizio previsto e date fine prevista ed effettiva, presenti'),
        ('20', 'Date inizio previsto ed effettivo presenti, date fine assenti'),
        ('21', 'Date inizio previsto ed effettivo, e data fine prevista presenti'),
        ('22', 'Tutte le date presenti'),
    )
    DPS_FLAG_DATE = Choices(
        ('0', 'Durata incoerente (fine < inizio)'),
        ('1', 'Durata coerente (fine > inizio)'),
        ('2', 'Durata non valutabile (inizio e/o fine mancanti)'),
    )
    FONDO_COMUNITARIO = Choices(
        ('erdf', 'ERDF'),
        ('esf', 'ESF')
    )
    TIPO_OPERAZIONE = Choices(
        ('1', 'opere_pubbliche', 'Realizzazione di opere pubbliche'),
        ('2', 'beni_servizi', 'Acquisizione  di beni e servizi'),
        ('3', 'finanziamenti', 'Erogazione di finanziamenti e aiuti a imprese e individui'),
    )
    OBIETTIVO_SVILUPPO = Choices(
        ('COMPETITIVITA', 'competitivita', 'Competitività regionale e occupazione'),
        ('CONVERGENZA', 'convergenza', 'Convergenza'),
        ('COOPERAZIONE', 'cooperazione', 'Cooperazione territoriale europea')
    )

    codice_locale = models.CharField(max_length=100, primary_key=True,
                                     db_column='cod_locale_progetto')
    cup = models.CharField(max_length=15)
    titolo_progetto = models.TextField()
    classificazione_qsn = models.ForeignKey('ClassificazioneQSN',
                                            related_name='progetto_set',
                                            db_column='classificazione_qsn')

    stato_fs = models.NullBooleanField(blank=True)
    stato_fsc = models.NullBooleanField(blank=True)
    stato_dps = models.NullBooleanField(blank=True)

    programma_asse_obiettivo = models.ForeignKey('ProgrammaAsseObiettivo',
                                                 related_name='progetto_set',
                                                 db_column='programma_asse_progetto')

    data_aggiornamento = models.DateField(null=True)

    obiettivo_sviluppo = models.CharField(max_length=16,
                                          blank=True, null=True,
                                          choices=OBIETTIVO_SVILUPPO)
    tipo_operazione = models.IntegerField(null=True, choices=TIPO_OPERAZIONE)
    fondo_comunitario = models.CharField(max_length=4,
                                         blank=True, null=True,
                                         choices=FONDO_COMUNITARIO)
    tema = models.ForeignKey('Tema',
                             related_name='progetto_set',
                             db_column='tema')

    intesa_istituzionale = models.ForeignKey('Intesa',
                                             related_name='progetto_set',
                                             db_column='intesa_istituzionale')

    classificazione_azione = models.ForeignKey('ClassificazioneAzione',
                                               related_name='progetto_set',
                                               db_column='classificazione_azione')

    classificazione_oggetto = models.ForeignKey('ClassificazioneOggetto',
                                                related_name='progetto_set',
                                                db_column='classificazione_oggetto')

    fin_totale = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    fin_totale_pubblico = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    fin_ue = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    fin_stato_fondo_rotazione = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    fin_stato_fsc = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    fin_stato_altri_provvedimenti = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    fin_regione = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    fin_provincia = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    fin_comune = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    fin_altro_pubblico = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    fin_stato_estero = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    fin_privato = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    fin_da_reperire = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    costo = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    costo_ammesso = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    pagamento = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    pagamento_fsc = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    pagamento_ammesso = models.DecimalField(max_digits=14, decimal_places=2, null=True)

    data_inizio_prevista = models.DateField(null=True)
    data_fine_prevista = models.DateField(null=True)
    data_inizio_effettiva = models.DateField(null=True)
    data_fine_effettiva = models.DateField(null=True)

    data_inizio_info = models.IntegerField(null=True)
    dps_date = models.CharField(max_length=2, choices=DPS_DATE)
    dps_flag_date_previste = models.CharField(max_length=1, choices=DPS_FLAG_DATE)
    dps_flag_date_effettive = models.CharField(max_length=1, choices=DPS_FLAG_DATE)
    dps_flag_cup = models.CharField(max_length=1, choices=DPS_FLAG_CUP)

    localita_set = models.ManyToManyField(Localita, through='Localizzazione')
    soggetto_set = models.ManyToManyField('Soggetto')

    @property
    def localita(self):
        return self.localita_set.all()

    @property
    def soggetti(self):
        return self.soggetto_set.all()

    def __unicode__(self):
        return self.codice_locale

    class Meta:
        verbose_name_plural = "Progetti"


class Localizzazione(models.Model):
    DPS_FLAG_CAP = Choices(
        ('0', 'CAP non valido o incoerente con territorio'),
        ('1', 'CAP valido e coerente'),
        ('2', 'CAP mancante o territorio nazionale o estero'),
    )
    localita = models.ForeignKey(Localita, verbose_name=u'Località')
    progetto = models.ForeignKey('Progetto', db_column='codice_progetto')
    indirizzo = models.CharField(max_length=255, blank=True, null=True)
    cap = models.CharField(max_length=5, blank=True, null=True)
    dps_flag_cap = models.CharField(max_length=1, choices=DPS_FLAG_CAP)

    class Meta:
        verbose_name_plural = "Localizzazioni"


class Soggetto(models.Model):
    RUOLO = Choices(
        ('1', 'programmatore', 'Programmatore'),
        ('2', 'attuatore', 'Attuatore'),
        ('3', 'destinatario', 'Destinatario del finanziamento'),
        ('4', 'realizzatore', 'Realizzatore')
    )
    codice_fiscale = models.CharField(max_length=16, primary_key=True)
    denominazione = models.CharField(max_length=255)
    ruolo = models.CharField(max_length=1, choices=RUOLO)

    @property
    def progetti(self):
        return self.progetto_set.all()

    def __unicode__(self):
        return "%s" % (self.denominazione, )

    class Meta:
        verbose_name_plural = "Soggetti"
