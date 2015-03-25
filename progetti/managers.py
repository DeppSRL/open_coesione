from datetime import datetime
from django.db import models


class ProgettiQuerySet(models.query.QuerySet):

    def conclusi(self, date=None):
        date = date or datetime.now()
        return self.filter(data_fine_effettiva__lte=date).order_by('-data_fine_effettiva')

    def avviati(self, date=None):
        date = date or datetime.now()
        return self.filter(data_inizio_effettiva__lte=date).order_by('-data_inizio_effettiva')

    def totali(self, territorio=None, tema=None, tipo=None, classificazione=None, soggetto=None, territori=None, programmi=None):

        query_set = self

        if territorio:
            query_set = query_set.nel_territorio(territorio)
        elif territori:
            query_set = query_set.nei_territori(territori)

        if tipo:
            query_set = query_set.del_tipo(tipo)

        if tema:
            query_set = query_set.con_tema(tema)

        if classificazione:
            query_set = query_set.con_natura(classificazione)

        if programmi:
            query_set = query_set.con_programmi(programmi)

        if soggetto:
            query_set = query_set.del_soggetto(soggetto)

#        if not query_set:
#            raise Exception('Richiesta non valida')

        return query_set.distinct()

    def nel_territorio(self, territorio):
        if territorio.territorio == territorio.TERRITORIO.R:
            return self.filter(territorio_set__cod_reg=territorio.cod_reg)
        elif territorio.territorio == territorio.TERRITORIO.P:
            return self.filter(territorio_set__cod_prov=territorio.cod_prov)
        elif territorio.territorio == territorio.TERRITORIO.C:
            return self.filter(territorio_set__cod_com=territorio.cod_com)
        elif territorio.territorio == territorio.TERRITORIO.N:
            return self.filter(territorio_set__territorio=territorio.TERRITORIO.N)
        elif territorio.territorio == territorio.TERRITORIO.E:
            return self.filter(territorio_set__pk=territorio.pk)
        else:
            raise Exception('Territorio non valido {0}'.format(territorio))

    def nei_territori(self, territori):
        conditions = False  # zero
        for territorio in territori:
            if not conditions:
                conditions = models.Q(**territorio.get_cod_dict('territorio_set__'))
            else:
                conditions |= models.Q(**territorio.get_cod_dict('territorio_set__'))
        return self.filter(conditions)

    def con_tema(self, tema):
        if tema.is_root:
            return self.filter(tema__tema_superiore=tema)
        else:
            return self.filter(tema=tema)

    def del_tipo(self, tipologia):
        return self.filter(tipo_operazione=tipologia)

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

    def del_soggetto(self, soggetto):
        return self.filter(soggetto_set__pk=soggetto.pk)

    def totale_costi(self, territorio=None, tema=None, tipo=None, classificazione=None, soggetto=None, territori=None, programmi=None):
        return round(float(sum([l['fin_totale_pubblico'] for l in self.totali(territorio, tema, tipo, classificazione, soggetto, territori, programmi).filter(fin_totale_pubblico__isnull=False).values('codice_locale', 'fin_totale_pubblico')]) or 0.0))

    def totale_pagamenti(self, territorio=None, tema=None, tipo=None, classificazione=None, soggetto=None, territori=None, programmi=None):
        return round(float(sum([l['pagamento'] for l in self.totali(territorio, tema, tipo, classificazione, soggetto, territori, programmi).filter(pagamento__isnull=False).values('codice_locale', 'pagamento')]) or 0.0))

    def totale_progetti(self, territorio=None, tema=None, tipo=None, classificazione=None, soggetto=None, territori=None, programmi=None):
        return self.totali(territorio, tema, tipo, classificazione, soggetto, territori, programmi).count()


class ProgettiManager(models.Manager):

    territorio = None
    tema = None
    tipo = None

    def get_query_set(self):
        return ProgettiQuerySet(self.model, using=self._db).filter(active_flag=True)  # note the `using` parameter, new in 1.2

    def conclusi(self, date=None):
        return self.get_query_set().conclusi(date)

    def avviati(self, date=None):
        return self.get_query_set().avviati(date)

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

    def del_soggetto(self, soggetto):
        return self.totali(soggetto=soggetto)

    def totali(self, territorio=None, tema=None, tipo=None, classificazione=None, soggetto=None, territori=None, programmi=None):
        return self.get_query_set().totali(territorio, tema, tipo, classificazione, soggetto, territori, programmi)

    def totale_costi(self, territorio=None, tema=None, tipo=None, classificazione=None, soggetto=None, territori=None, programmi=None):
        return self.get_query_set().totale_costi(territorio, tema, tipo, classificazione, soggetto, territori, programmi)

    def totale_pagamenti(self, territorio=None, tema=None, tipo=None, classificazione=None, soggetto=None, territori=None, programmi=None):
        return self.get_query_set().totale_pagamenti(territorio, tema, tipo, classificazione, soggetto, territori, programmi)

    def totale_progetti(self, territorio=None, tema=None, tipo=None, classificazione=None, soggetto=None, territori=None, programmi=None):
        return self.get_query_set().totale_progetti(territorio, tema, tipo, classificazione, soggetto, territori, programmi)

    def totale_costi_procapite(self, territorio=None, tema=None, tipo=None, classificazione=None, soggetto=None, territori=None, programmi=None):
        from territori.models import Territorio
        territorio = territorio or Territorio.objects.nazione()

        # check if no population defined (foreign countries)
        # and avoid division by zero exception
        if territorio.popolazione_totale is 0:
            return 0
        else:
            return round(self.get_query_set().totale_costi(territorio, tema, tipo, classificazione, soggetto, territori, programmi) / territorio.popolazione_totale)

    def totale_pagamenti_procapite(self, territorio=None, tema=None, tipo=None, classificazione=None, soggetto=None, territori=None, programmi=None):
        from territori.models import Territorio
        territorio = territorio or Territorio.objects.nazione()
        return round(self.get_query_set().totale_pagamenti(territorio, tema, tipo, classificazione, soggetto, territori, programmi) / territorio.popolazione_totale)

    def totale_progetti_procapite(self, territorio=None, tema=None, tipo=None, classificazione=None, soggetto=None, territori=None, programmi=None):
        from territori.models import Territorio
        territorio = territorio or Territorio.objects.nazione()
        return self.get_query_set().totale_progetti(territorio, tema, tipo, classificazione, soggetto, territori, programmi) / territorio.popolazione_totale

#    def totale_risorse_stanziate(self, territorio=None, tema=None, tipo=None,classificazione=None):
#        return self.totali(territorio, tema, tipo,classificazione).aggregate(total=models.Sum('fin_totale_pubblico'))['total'] or 0.0


class FullProgettiManager(ProgettiManager):
    def get_query_set(self):
        return ProgettiQuerySet(self.model, using=self._db)  # note the `using` parameter, new in 1.2


class TemiManager(models.Manager):
    def principali(self):
        return self.get_query_set().filter(tipo_tema=self.model.TIPO.sintetico).order_by('priorita')

    def costo_totale(self):
        return self.get_query_set().annotate(totale=models.Sum('progetto_set__fin_totale_pubblico'))


class ClassificazioneAzioneManager(models.Manager):

    def nature(self):
        """
        an alias of tematiche
        """
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


# class RuoloManager(models.Manager):
#     def get_query_set(self):
#         return models.query.QuerySet(self.model, using=self._db).filter(progetto__active_flag=True).distinct()
