from django.db import models
from django.db.models.aggregates import Count, Sum
from django.template.defaultfilters import slugify
from django.views.generic.detail import DetailView
from open_coesione.views import AggregatoView
from progetti.models import Progetto, Tema, ClassificazioneAzione
from territori.models import Territorio


class TerritorioView(AggregatoView, DetailView):
    context_object_name = 'territorio'
    tipo_territorio = ''
    model = 'Territorio'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TerritorioView, self).get_context_data(**kwargs)

        context['total_cost'] = Progetto.objects.totale_costi(territorio=self.object)
        context['total_cost_paid'] = Progetto.objects.totale_costi_pagati(territorio=self.object)
        context['total_projects'] = Progetto.objects.totale_progetti(territorio=self.object)
        context['total_allocated_resources'] = Progetto.objects.totale_risorse_stanziate(territorio=self.object)
        context['cost_payments_ratio'] = "{0:.0%}".format(context['total_cost_paid'] / context['total_cost'] if context['total_cost'] > 0.0 else 0.0)

        context['temi_principali'] = [
            {
            'object': tema,
            'data': Tema.objects.\
                filter(tema_superiore=tema).\
                filter(**self.object.get_cod_dict(prefix='progetto_set__territorio_set__')).\
                aggregate(numero=Count('progetto_set'),
                          costo=Sum('progetto_set__fin_totale_pubblico'),
                          pagamento=Sum('progetto_set__pagamento'))
            } for tema in Tema.objects.principali()
        ]

        context['tipologie_principali'] = [
            {
            'object': natura,
            'data': ClassificazioneAzione.objects.\
                filter(classificazione_superiore=natura).\
                filter(**self.object.get_cod_dict(prefix='progetto_set__territorio_set__')).\
                aggregate(numero=Count('progetto_set'),
                          costo=Sum('progetto_set__fin_totale_pubblico'),
                          pagamento=Sum('progetto_set__pagamento'))
            } for natura in ClassificazioneAzione.objects.tematiche()
        ]

        context['top_progetti_per_costo'] = Progetto.objects.nel_territorio(self.object).filter(fin_totale_pubblico__isnull=False).order_by('-fin_totale_pubblico')[:3]
        context['ultimi_progetti_conclusi'] = Progetto.objects.conclusi().nel_territorio(self.object)[:3]

        context['territori_piu_finanziati_pro_capite'] = Territorio.objects\
            .filter( territorio=Territorio.TERRITORIO.C ,**self.object.get_cod_dict() )\
            .exclude(pk=self.object.pk)\
            .annotate( totale=models.Sum('progetto__fin_totale_pubblico') )\
            .filter( totale__isnull=False )\
            .order_by('-totale')[:3]
        # sotto territori del territorio richiesto
#        context['territori_piu_finanziati'] = Territorio.objects\
#                .exclude(pk=self.object.pk)\
#                .filter(totale__isnull=False, territorio= Territorio.TERRITORIO.C, **self.object.get_cod_dict())\
#                .annotate(totale=models.Sum('progetto__costo'))\
#                .order_by('-fin_totale_pubblico')[:3]

        context['map'] = self.get_map_context( self.object )

        return context

    def get_object(self, queryset=None):
        return Territorio.objects.get(slug= slugify(self.kwargs['slug']) , territorio= self.tipo_territorio)


class RegioneView(TerritorioView):
    tipo_territorio = Territorio.TERRITORIO.R

class ProvinciaView(TerritorioView):
    tipo_territorio = Territorio.TERRITORIO.P

class ComuneView(TerritorioView):
    tipo_territorio = Territorio.TERRITORIO.C