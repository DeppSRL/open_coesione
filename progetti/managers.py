from datetime import datetime
from django.db import models

class ProgettiQuerySet(models.query.QuerySet):

    def conclusi(self, date=datetime.now() ):
        return self.filter(data_fine_effettiva__lte=date).order_by('-data_fine_effettiva')

    def avviati(self, date=datetime.now() ):
        return self.filter(data_inizio_effettiva__lte=date).order_by('-data_inizio_effettiva')

    def totali(self, territorio=None, tema=None, tipo=None, classificazione=None, soggetto=None):

        query_set = self

        if territorio:
            query_set = query_set.nel_territorio( territorio )

        if tipo:
            query_set = query_set.del_tipo( tipo )

        if tema:
            query_set = query_set.con_tema( tema )

        if classificazione:
            query_set = query_set.con_natura( classificazione )

        if soggetto:
            query_set = query_set.del_soggetto( soggetto )

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
        else:
            raise Exception('Territorio non valido %s' % territorio)

    def nei_territori(self, territori):
        conditions = False # zero
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
        return self.filter(classificazione_azione__classificazione_superiore=natura)

    def del_soggetto(self, soggetto):
        return self.filter(soggetto_set__pk=soggetto.pk)

    def totale_costi(self, territorio=None, tema=None, tipo=None,classificazione=None, soggetto=None):
        return float(sum([l['fin_totale_pubblico'] for l in self.totali(territorio, tema, tipo,classificazione, soggetto).filter(fin_totale_pubblico__isnull=False).values('codice_locale', 'fin_totale_pubblico')]) or 0.0)

    def totale_pagamenti(self, territorio=None, tema=None, tipo=None,classificazione=None, soggetto=None):
        return float(sum([l['pagamento'] for l in self.totali(territorio, tema, tipo,classificazione, soggetto).filter(pagamento__isnull=False).values('codice_locale', 'pagamento')]) or 0.0)

    def totale_progetti(self, territorio=None, tema=None, tipo=None,classificazione=None, soggetto=None):
        return self.totali(territorio, tema, tipo,classificazione, soggetto).count()



class ProgettiManager(models.Manager):

    territorio=None
    tema=None
    tipo=None

    def get_query_set(self):
        return ProgettiQuerySet(self.model, using=self._db) # note the `using` parameter, new in 1.2

    def conclusi(self, date=datetime.now() ):
        return self.get_query_set().conclusi(date)

    def avviati(self, date=datetime.now() ):
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

    def del_soggetto(self, soggetto):
        return self.totali(soggetto=soggetto)

    def totali(self, territorio=None, tema=None, tipo=None,classificazione=None, soggetto=None):
        return self.get_query_set().totali(territorio, tema, tipo, classificazione, soggetto)

    def totale_costi(self, territorio=None, tema=None, tipo=None,classificazione=None, soggetto=None):
        return self.get_query_set().totale_costi(territorio, tema, tipo,classificazione, soggetto)

    def totale_pagamenti(self, territorio=None, tema=None, tipo=None,classificazione=None, soggetto=None):
        return self.get_query_set().totale_pagamenti(territorio, tema, tipo,classificazione, soggetto)

    def totale_progetti(self, territorio=None, tema=None, tipo=None,classificazione=None, soggetto=None):
        return self.get_query_set().totale_progetti(territorio, tema, tipo,classificazione, soggetto)

#    def totale_risorse_stanziate(self, territorio=None, tema=None, tipo=None,classificazione=None):
#        return self.totali(territorio, tema, tipo,classificazione).aggregate(total=models.Sum('fin_totale_pubblico'))['total'] or 0.0


class TemiManager(models.Manager):

    def principali(self):
        return self.get_query_set().filter(tipo_tema=self.model.TIPO.sintetico)

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
