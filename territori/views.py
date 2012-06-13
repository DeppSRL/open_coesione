from django.db import models
from django.views.generic.detail import DetailView
from open_coesione.views import AggregatoView
from progetti.models import Progetto, Tema
from territori.models import Territorio


class TerritorioView(AggregatoView, DetailView):
    context_object_name = 'territorio'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(TerritorioView, self).get_context_data(**kwargs)

        context['total_cost'] = Progetto.objects.totale_costi(territorio=self.object)
        context['total_cost_paid'] = Progetto.objects.totale_costi_pagati(territorio=self.object)
        context['total_projects'] = Progetto.objects.totale_progetti(territorio=self.object)
        context['total_allocated_resources'] = Progetto.objects.totale_risorse_stanziate(territorio=self.object)
        context['cost_payments_ratio'] = "{0:.0%}".format(context['total_cost_paid'] / context['total_cost'])

        # TODO: bisogna localizzarlo per territorio
        context['temi_principali'] = Tema.objects.filter(tema_superiore=None)

        tipologie = dict(Progetto.TIPO_OPERAZIONE)
        context['tipologie_principali'] = [
        ({'tipo': tipologie[str(x['tipo_operazione'])], 'totale': x['total'], 'tipo_operazione': x['tipo_operazione']})
        for x in Progetto.objects.nel_territorio(self.object).values('tipo_operazione').annotate(total= models.Sum('costo'))
        ]

        context['progetti_piu_costosi'] = Progetto.objects.nel_territorio(self.object).order_by('-fin_totale')[:3]
        context['ultimi_progetti_conclusi'] = Progetto.objects.conclusi().nel_territorio(self.object)[:3]

        if self.object.territorio == Territorio.TERRITORIO.R:
            context['territori_piu_finanziati'] = Territorio.objects.filter(cod_reg=self.object.cod_reg)
        elif self.object.territorio == Territorio.TERRITORIO.P:
            context['territori_piu_finanziati'] = Territorio.objects.filter(cod_prov=self.object.cod_prov)
        elif self.object.territorio == Territorio.TERRITORIO.C:
            context['territori_piu_finanziati'] = Territorio.objects.filter(cod_com=self.object.cod_com)
        else:
            raise Exception('Territorio non valido %s' % self.object)

        context['territori_piu_finanziati'] = context['territori_piu_finanziati'].annotate(totale=models.Sum('progetto__costo')).filter(totale__isnull=False).order_by('-totale')[:3]

        return context

    def get_object(self, queryset=None):
        # TODO: la denominazione non DEVE essere lo slug
        return Territorio.objects.get(denominazione=self.kwargs['slug'])


class RegioneView(TerritorioView):
    #raise Exception("Class RegioneView needs to be implemented")
    pass

class ProvinciaView(TerritorioView):
    #raise Exception("Class ProvinciaView needs to be implemented")
    pass

class ComuneView(TerritorioView):
    #raise Exception("Class ComuneView needs to be implemented")
    pass