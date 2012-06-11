from django.db import models

class ProgettiManager(models.Manager):

    def totale_costi(self):
        return self.get_query_set().aggregate(total=models.Sum('costo'))['total']

    def totale_costi_pagati(self):
        return self.get_query_set().aggregate(total=models.Sum('pagamento'))['total']

    def totale_progetti(self):
        return self.get_query_set().count()

    def totale_risorse_stanziate(self):
        return self.get_query_set().aggregate(total=models.Sum('fin_totale'))['total']
