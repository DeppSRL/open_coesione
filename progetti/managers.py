# -*- coding: utf-8 -*-
from datetime import datetime
from django.db import models
from territori.models import Territorio


class ProgettoQuerySet(models.query.QuerySet):
    def no_privacy(self):
        return self.filter(privacy_flag=False)

    def conclusi(self, date=None):
        date = date or datetime.now()
        return self.filter(data_fine_effettiva__lte=date, stato_progetto=self.model.STATO.concluso).order_by('-data_fine_effettiva', '-fin_totale_pubblico')

    def del_soggetto(self, soggetto):
        return self.filter(soggetto_set__pk=soggetto.pk).distinct()

    # def nei_territori(self, territori):
    #     conditions = False  # zero
    #     for territorio in territori:
    #         if not conditions:
    #             conditions = models.Q(**territorio.get_cod_dict('territorio_set__'))
    #         else:
    #             conditions |= models.Q(**territorio.get_cod_dict('territorio_set__'))
    #     return self.filter(conditions).distinct()

    # def nei_territori(self, territori):
    #     grouped_cod_dict = {}
    #     for territorio in territori:
    #         for k, v in territorio.get_cod_dict('territorio_set__').items():
    #             grouped_cod_dict.setdefault(k, []).append(v)
    #
    #     conditions = models.Q()
    #     for k, v in grouped_cod_dict.items():
    #         conditions.add(models.Q(**{k: v[0]} if len(v) == 1 else {'{}__in'.format(k): v}), models.Q.OR)
    #     return self.filter(conditions).distinct()

    def nei_territori(self, territori):
        from itertools import groupby
        from operator import itemgetter

        conditions = models.Q()
        for key, group in groupby(sorted([(k, v) for territorio in territori for k, v in territorio.get_cod_dict('territorio_set__').items()], key=itemgetter(0)), key=itemgetter(0)):
            vals = map(itemgetter(1), group)
            conditions.add(models.Q(**{key: vals[0]} if len(vals) == 1 else {'{}__in'.format(key): vals}), models.Q.OR)
        return self.filter(conditions).distinct()

    # def nei_territori(self, territori):
    #     from itertools import groupby
    #     from operator import itemgetter
    #
    #     conditions = models.Q()
    #     for key, group in groupby(sorted([(k, v) for territorio in territori for k, v in territorio.get_cod_dict().items()], key=itemgetter(0)), key=itemgetter(0)):
    #         vals = map(itemgetter(1), group)
    #         conditions.add(models.Q(**{key: vals[0]} if len(vals) == 1 else {'{}__in'.format(key): vals}), models.Q.OR)
    #
    #     return self.filter(territorio_set__pk__in=list(Territorio.objects.filter(conditions).values_list('pk', flat=True))).distinct()

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

        return self.filter(
            models.Q(programma_asse_obiettivo__classificazione_superiore__classificazione_superiore__in=programmi_splitted['programmi_asse_obiettivo']) |
            models.Q(programma_linea_azione__classificazione_superiore__classificazione_superiore__in=programmi_splitted['programmi_linea_azione'])
        )

    # def myfilter(self, **kwargs):
    #     queryset = self
    #
    #     soggetto = kwargs.pop('soggetto', None)
    #     if soggetto:
    #         queryset = queryset.del_soggetto(soggetto)
    #
    #     territori = kwargs.pop('territori', None)
    #     if territori:
    #         queryset = queryset.nei_territori(territori)
    #
    #     tema = kwargs.pop('tema', None)
    #     if tema:
    #         queryset = queryset.con_tema(tema)
    #
    #     classificazione = kwargs.pop('classificazione', None)
    #     if classificazione:
    #         queryset = queryset.con_natura(classificazione)
    #
    #     programmi = kwargs.pop('programmi', None)
    #     if programmi:
    #         queryset = queryset.con_programmi(programmi)
    #
    #     return queryset

    # def totale_costi(self, **kwargs):
    #     return self.myfilter(**kwargs).totali()['totale_costi']

    # def totale_pagamenti(self, **kwargs):
    #     return self.myfilter(**kwargs).totali()['totale_pagamenti']

    # def totale_progetti(self, **kwargs):
    #     return self.myfilter(**kwargs).totali()['totale_progetti']

    def totali(self):
        return self._totali()[0]

    def totali_group_by(self, group_by):
        return self._totali(group_by)

    def _totali(self, group_by=None):
        from django.db import connection

        def dictfetchall(cursor):
            col_names = [x.name for x in cursor.description]
            for row in cursor.fetchall():
                yield dict(zip(col_names, row))

        fields = ['codice_locale', 'fin_totale_pubblico', 'pagamento']
        if group_by:
            fields.append(group_by)

        queryset = self.values(*fields)

        sql, params = queryset.query.sql_with_params()

        sql = 'SUM(sq.fin_totale_pubblico) AS "totale_costi", SUM(sq.pagamento) AS "totale_pagamenti", COUNT(*) AS "totale_progetti" from ({}) AS sq'.format(sql)
        if group_by:
            sql = 'SELECT sq.{1} AS "id", {0} GROUP BY sq.{1}'.format(sql, group_by.split('__')[-1])
        else:
            sql = 'SELECT {}'.format(sql)

        cursor = connection.cursor()
        cursor.execute(sql, params)

        totali = list(dictfetchall(cursor))

        for item in totali:
            item['totale_costi'] = round(float(item['totale_costi'] or 0.0))
            item['totale_pagamenti'] = round(float(item['totale_pagamenti'] or 0.0))

        return totali


class ProgettoManager(models.Manager):
    def get_query_set(self):
        return ProgettoQuerySet(self.model, using=self._db).filter(active_flag=True)

    def no_privacy(self):
        return self.get_query_set().no_privacy()

    def conclusi(self, date=None):
        return self.get_query_set().conclusi(date)

    def del_soggetto(self, soggetto):
        return self.get_query_set().del_soggetto(soggetto)

    def nei_territori(self, territori):
        return self.get_query_set().nei_territori(territori)

    def con_tema(self, tema):
        return self.get_query_set().con_tema(tema)

    def con_natura(self, classificazione):
        return self.get_query_set().con_natura(classificazione)

    def con_programmi(self, programmi):
        return self.get_query_set().con_programmi(programmi)

    # def myfilter(self, **kwargs):
    #     return self.get_query_set().myfilter(**kwargs)

    def totali(self):
        return self.get_query_set().totali()

    def totali_group_by(self, group_by):
        return self.get_query_set().totali_group_by(group_by)

    # def totale_costi(self, **kwargs):
    #     return self.get_query_set().totale_costi(**kwargs)

    # def totale_pagamenti(self, **kwargs):
    #     return self.get_query_set().totale_pagamenti(**kwargs)

    # def totale_progetti(self, **kwargs):
    #     return self.get_query_set().totale_progetti(**kwargs)

    # def totale_costi_procapite(self, **kwargs):
    #     from territori.models import Territorio
    #     territorio = kwargs.setdefault('territorio', Territorio.objects.nazione())
    #     return round(self.get_query_set().totale_costi(**kwargs) / territorio.popolazione_totale) if territorio.popolazione_totale else 0


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
        # return self.get_query_set().filter(tipo_classificazione=self.model.TIPO.natura).filter(classificazione_set__progetto_set__active_flag=True).distinct().order_by('priorita')
        return self.get_query_set().filter(tipo_classificazione=self.model.TIPO.natura).filter(priorita__gt=0).order_by('priorita')

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
