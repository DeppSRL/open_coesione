# -*- coding: utf-8 -*-
from datetime import datetime
from django.db import models


class ProgettoQuerySet(models.query.QuerySet):
    def no_privacy(self):
        return self.filter(privacy_flag=False)

    def conclusi(self, date=None):
        date = date or datetime.now()
        return self.filter(data_fine_effettiva__lte=date, stato_progetto=self.model.STATO.concluso).order_by('-data_fine_effettiva', '-fin_totale_pubblico')

    def del_soggetto(self, soggetto):
        return self.filter(soggetto_set__pk=soggetto.pk).distinct()

    def nel_territorio(self, territorio):
        if territorio.is_regione:
            return self.filter(territorio_set__cod_reg=territorio.cod_reg).distinct()
        elif territorio.is_provincia:
            return self.filter(territorio_set__cod_prov=territorio.cod_prov).distinct()
        elif territorio.is_comune:
            return self.filter(territorio_set__cod_com=territorio.cod_com).distinct()
        elif territorio.is_nazionale:
            return self.filter(territorio_set__territorio=territorio.TERRITORIO.N).distinct()
        elif territorio.is_estero:
            return self.filter(territorio_set__pk=territorio.pk).distinct()
        else:
            raise Exception('Territorio non valido {}'.format(territorio))

    def nei_territori(self, territori):
        conditions = False  # zero
        for territorio in territori:
            if not conditions:
                conditions = models.Q(**territorio.get_cod_dict('territorio_set__'))
            else:
                conditions |= models.Q(**territorio.get_cod_dict('territorio_set__'))
        return self.filter(conditions).distinct()

    def del_tipo(self, tipologia):
        return self.filter(tipo_operazione=tipologia)

    def con_tema(self, tema):
        if tema.is_root:
            return self.filter(tema__tema_superiore=tema)
        else:
            return self.filter(tema=tema)

    def con_natura(self, natura):
        if natura.is_root:
            return self.filter(classificazione_azione__classificazione_superiore=natura)
        else:
            return self.filter(classificazione_azione=natura)

    def con_programmi(self, programmi):
        from progetti.gruppo_programmi import split_by_type

        programmi_splitted = split_by_type(programmi)

        from django.db.models import Q

        return self.filter(
            Q(programma_asse_obiettivo__classificazione_superiore__classificazione_superiore__in=programmi_splitted['programmi_asse_obiettivo']) |
            Q(programma_linea_azione__classificazione_superiore__classificazione_superiore__in=programmi_splitted['programmi_linea_azione'])
        )

    def totali(self, **kwargs):
        queryset = self

        soggetto = kwargs.pop('soggetto', None)
        if soggetto:
            queryset = queryset.del_soggetto(soggetto)

        territorio = kwargs.pop('territorio', None)
        territori = kwargs.pop('territori', None)
        if territorio:
            queryset = queryset.nel_territorio(territorio)
        elif territori:
            queryset = queryset.nei_territori(territori)

        tipo = kwargs.pop('tipo', None)
        if tipo:
            queryset = queryset.del_tipo(tipo)

        tema = kwargs.pop('tema', None)
        if tema:
            queryset = queryset.con_tema(tema)

        classificazione = kwargs.pop('classificazione', None)
        if classificazione:
            queryset = queryset.con_natura(classificazione)

        programmi = kwargs.pop('programmi', None)
        if programmi:
            queryset = queryset.con_programmi(programmi)

        return queryset

    def totale_costi(self, **kwargs):
        return self.dict_totali(**kwargs)['totale_costi']
        # return round(float(sum([l['fin_totale_pubblico'] for l in self.totali(territorio, tema, tipo, classificazione, soggetto, territori, programmi).filter(fin_totale_pubblico__isnull=False).values('codice_locale', 'fin_totale_pubblico')]) or 0.0))

    def totale_pagamenti(self, **kwargs):
        return self.dict_totali(**kwargs)['totale_pagamenti']
        # return round(float(sum([l['pagamento'] for l in self.totali(territorio, tema, tipo, classificazione, soggetto, territori, programmi).filter(pagamento__isnull=False).values('codice_locale', 'pagamento')]) or 0.0))

    def totale_progetti(self, **kwargs):
        return self.dict_totali(**kwargs)['totale_progetti']
        # return self.totali(territorio, tema, tipo, classificazione, soggetto, territori, programmi).count()

    def dict_totali(self, **kwargs):
        from django.db import connection

        queryset = self.totali(**kwargs).values('codice_locale', 'fin_totale_pubblico', 'pagamento')

        sql, params = queryset.query.sql_with_params()

        cursor = connection.cursor()
        cursor.execute('SELECT SUM(t.fin_totale_pubblico) AS "totale_costi", SUM(t.pagamento) AS "totale_pagamenti", COUNT(*) AS "totale_progetti" from ({}) AS t'.format(sql), params)

        dict_totali = dict(zip((x.name for x in cursor.description), cursor.fetchone()))

        dict_totali['totale_costi'] = round(float(dict_totali['totale_costi'] or 0.0))
        dict_totali['totale_pagamenti'] = round(float(dict_totali['totale_pagamenti'] or 0.0))

        return dict_totali


class ProgettoManager(models.Manager):
    def get_query_set(self):
        return ProgettoQuerySet(self.model, using=self._db).filter(active_flag=True)

    def no_privacy(self):
        return self.get_query_set().no_privacy()

    def conclusi(self, date=None):
        return self.get_query_set().conclusi(date)

    def del_soggetto(self, soggetto):
        return self.totali(soggetto=soggetto)

    def nel_territorio(self, territorio):
        return self.totali(territorio=territorio)

    def nei_territori(self, territori):
        return self.get_query_set().nei_territori(territori)

    def del_tipo(self, tipo):
        return self.totali(tipo=tipo)

    def con_tema(self, tema):
        return self.totali(tema=tema)

    def con_natura(self, classificazione):
        return self.totali(classificazione=classificazione)

    def con_programmi(self, programmi):
        return self.totali(programmi=programmi)

    def dict_totali(self, **kwargs):
        return self.get_query_set().dict_totali(**kwargs)

    def totali(self, **kwargs):
        return self.get_query_set().totali(**kwargs)

    def totale_costi(self, **kwargs):
        return self.get_query_set().totale_costi(**kwargs)

    def totale_pagamenti(self, **kwargs):
        return self.get_query_set().totale_pagamenti(**kwargs)

    def totale_progetti(self, **kwargs):
        return self.get_query_set().totale_progetti(**kwargs)

    def totale_costi_procapite(self, **kwargs):
        from territori.models import Territorio
        territorio = kwargs.setdefault('territorio', Territorio.objects.nazione())
        return round(self.get_query_set().totale_costi(**kwargs) / territorio.popolazione_totale) if territorio.popolazione_totale else 0

    def totale_pagamenti_procapite(self, **kwargs):
        from territori.models import Territorio
        territorio = kwargs.setdefault('territorio', Territorio.objects.nazione())
        return round(self.get_query_set().totale_pagamenti(**kwargs) / territorio.popolazione_totale) if territorio.popolazione_totale else 0

    def totale_progetti_procapite(self, **kwargs):
        from territori.models import Territorio
        territorio = kwargs.setdefault('territorio', Territorio.objects.nazione())
        return self.get_query_set().totale_progetti(**kwargs) / territorio.popolazione_totale if territorio.popolazione_totale else 0


class FullProgettoManager(ProgettoManager):
    def get_query_set(self):
        return ProgettoQuerySet(self.model, using=self._db)


class TemaManager(models.Manager):
    def principali(self):
        return self.get_query_set().filter(tipo_tema=self.model.TIPO.sintetico).order_by('priorita')

    def costo_totale(self):
        return self.get_query_set().annotate(totale=models.Sum('progetto_set__fin_totale_pubblico'))


class ClassificazioneAzioneManager(models.Manager):
    def nature(self):
        return self.tematiche()

    def tematiche(self):
        return self.get_query_set().filter(tipo_classificazione=self.model.TIPO.natura).order_by('priorita')

    def costo_totale(self):
        return self.get_query_set().annotate(totale=models.Sum('progetto_set__fin_totale_pubblico'))


class ProgrammaQuerySet(models.query.QuerySet):
    def programmi(self):
        return self.filter(tipo_classificazione=self.model.TIPO.programma)

    def programmi_fesr(self):
        return self.programmi().filter(descrizione__icontains=' FESR ')

    def programmi_fse(self):
        return self.programmi().filter(descrizione__icontains=' FSE ')

    def programmi_competitivita(self):
        return self.programmi().filter(descrizione__icontains=' CRO ')

    def programmi_convergenza(self):
        return self.programmi().filter(descrizione__icontains=' CONV ')


class ProgrammaManager(models.Manager):
    def get_query_set(self):
        return ProgrammaQuerySet(self.model, using=self._db)

    def programmi(self):
        return self.get_query_set().programmi()

    def programmi_fesr(self):
        return self.get_query_set().programmi_fesr()

    def programmi_fse(self):
        return self.get_query_set().programmi_fse()

    def programmi_competitivita(self):
        return self.get_query_set().programmi_competitivita()

    def programmi_convergenza(self):
        return self.get_query_set().programmi_convergenza()
