from datetime import datetime
from django.views.generic.base import TemplateView
from django.db import models
from progetti.models import Progetto, Tema, ClassificazioneOggetto


class AggregatoView(object):
    # raise Exception("Class AggregatoView needs to be implemented")
    pass

class HomeView(AggregatoView, TemplateView):
    template_name = 'homepage.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        context['total_cost'] = Progetto.objects.totale_costi()
        context['total_cost_paid'] = Progetto.objects.totale_costi_pagati()
        context['total_projects'] = Progetto.objects.totale_progetti()
        context['total_allocated_resources'] = Progetto.objects.totale_risorse_stanziate()

        cost_payment_ratio = context['total_cost_paid'] / context['total_cost']
        context['cost_payments_ratio'] = "%d%%" % int(cost_payment_ratio * 100)

        context['temi_principali'] = Tema.objects.principali()

        tipologie = dict(Progetto.TIPO_OPERAZIONE)
        context['tipologie_principali'] = []
        [
            ({'tipo': tipologie[str(x['tipo_operazione'])], 'totale': x['total'], 'tipo_operazione': x['tipo_operazione']})
            for x in Progetto.objects.values('tipo_operazione').annotate(total= models.Sum('fin_totale_pubblico'))
        ]
        context['top_progetti_per_costo'] = Progetto.objects.filter(costo__isnull=False).order_by('-fin_totale_pubblico')[:3]

        context['ultimi_progetti_avviati'] = Progetto.objects.filter(data_inizio_effettiva__lte=datetime.now()).order_by('-data_inizio_effettiva')[:3]
        context['ultimi_progetti_conclusi'] = Progetto.objects.filter(data_fine_effettiva__lte=datetime.now()).order_by('-data_fine_effettiva')[:3]

        return context

