from datetime import datetime
from django.db import models

class ProgettiQuerySet(models.query.QuerySet):

    def conclusi(self, date=datetime.now() ):
        return self.filter(data_fine_effettiva__lte=date).order_by('-data_fine_effettiva')

    def avviati(self, date=datetime.now() ):
        return self.filter(data_inizio_effettiva__lte=date).order_by('-data_inizio_effettiva')

    def totali(self, territorio=None, tema=None, tipo=None):

        query_set = self

        if territorio:
            query_set = self.nel_territorio( territorio )

        if tipo:
            query_set = self.del_tipo( tipo )

        if tema:
            query_set = self.con_tema( tema )

#        if not query_set:
#            raise Exception('Richiesta non valida')

        return query_set

    def nel_territorio(self, territorio):
        if territorio.territorio == territorio.TERRITORIO.R:
            return self.filter(territorio_set__cod_reg=territorio.pk)
        elif territorio.territorio == territorio.TERRITORIO.P:
            return self.filter(territorio_set__cod_prov=territorio.pk)
        elif territorio.territorio == territorio.TERRITORIO.C:
            return self.filter(territorio_set__cod_com=territorio.pk)
        else:
            raise Exception('Territorio non valido %s' % territorio)

    def con_tema(self, tema):
        return self.filter(tema=tema)

    def del_tipo(self, tipologia):
        return self.filter(tipo_operazione=tipologia)

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

    def del_tipo(self, tipo):
        return self.totali(tipo=tipo)

    def con_tema(self, tema):
        return self.totali(tema=tema)

    def totali(self, territorio=None, tema=None, tipo=None):
        return self.get_query_set().totali(territorio, tema, tipo)

    def totale_costi(self, territorio=None, tema=None, tipo=None):
        return self.totali(territorio, tema, tipo).aggregate(total=models.Sum('fin_totale'))['total']

    def totale_costi_pagati(self, territorio=None, tema=None, tipo=None):
        return self.totali(territorio, tema, tipo).aggregate(total=models.Sum('pagamento'))['total']

    def totale_progetti(self, territorio=None, tema=None, tipo=None):
        return self.totali(territorio, tema, tipo).count()

    def totale_risorse_stanziate(self, territorio=None, tema=None, tipo=None):
        return self.totali(territorio, tema, tipo).aggregate(total=models.Sum('fin_totale'))['total']
