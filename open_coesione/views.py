from datetime import datetime
from django.views.generic.base import TemplateView
from django.db.models import Count, Sum
from progetti.models import Progetto, Tema, ClassificazioneOggetto, ClassificazioneAzione
from territori.models import Territorio
from django.utils import simplejson


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

        cost_payment_ratio = context['total_cost_paid'] / context['total_cost'] if context['total_cost'] > 0.0 else 0.0
        context['cost_payments_ratio'] = "%d%%" % int(cost_payment_ratio * 100)

        context['temi_principali'] = Tema.objects.principali()

        #tipologie = dict(Progetto.TIPO_OPERAZIONE)
        context['tipologie_principali'] = ClassificazioneAzione.objects.tematiche()
#        [
#            ({'tipo': tipologie[str(x['tipo_operazione'])], 'totale': x['total'], 'tipo_operazione': x['tipo_operazione']})
#            for x in Progetto.objects.values('tipo_operazione').annotate(total= models.Sum('fin_totale_pubblico'))
#        ]
        context['top_progetti_per_costo'] = Progetto.objects.filter(costo__isnull=False).order_by('-fin_totale_pubblico')[:3]

        context['ultimi_progetti_avviati'] = Progetto.objects.filter(data_inizio_effettiva__lte=datetime.now()).order_by('-data_inizio_effettiva')[:3]
        context['ultimi_progetti_conclusi'] = Progetto.objects.filter(data_fine_effettiva__lte=datetime.now()).order_by('-data_fine_effettiva')[:3]

        italy_extent = Territorio.objects.filter(territorio='R').extent()
        context['extent'] = "[{lon: %s, lat: %s},{lon: %s, lat: %s}]" % \
            (italy_extent[0], italy_extent[1], italy_extent[2], italy_extent[3])
        context['zoomlev'] = 6
        context['zoomrange'] = simplejson.dumps([6, 7])

        data = {
            'regioni': {
                'numero': dict(
                    (t.cod_reg, Territorio.objects.filter(cod_reg=t.cod_reg).aggregate(s=Count('progetto'))['s'])
                        for t in Territorio.objects.filter(territorio='R')
                ),
                'costo': dict(
                    (t.cod_reg, Territorio.objects.filter(cod_reg=t.cod_reg).aggregate(s=Sum('progetto__fin_totale_pubblico'))['s'])
                        for t in Territorio.objects.filter(territorio='R')
                ),
                'pagamento': dict(
                    (t.cod_reg, Territorio.objects.filter(cod_reg=t.cod_reg).aggregate(s=Sum('progetto__costo'))['s'])
                        for t in Territorio.objects.filter(territorio='R')
                )
            },
            'province': {
                'numero': dict(
                    (t.cod_prov, Territorio.objects.filter(cod_prov=t.cod_prov).aggregate(s=Count('progetto'))['s'])
                        for t in Territorio.objects.filter(territorio='P')
                ),
                'costo': dict(
                    (t.cod_prov, Territorio.objects.filter(cod_prov=t.cod_prov).aggregate(s=Sum('progetto__fin_totale_pubblico'))['s'])
                        for t in Territorio.objects.filter(territorio='P')
                ),
                'pagamento': dict(
                    (t.cod_prov, Territorio.objects.filter(cod_prov=t.cod_prov).aggregate(s=Sum('progetto__costo'))['s'])
                        for t in Territorio.objects.filter(territorio='P')
                )
            }
        }
        context['data'] = simplejson.dumps(data)
        return context
