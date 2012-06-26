from datetime import datetime
from django.views.generic.base import TemplateView
from django.db.models import Count, Sum
from progetti.models import Progetto, Tema, ClassificazioneOggetto, ClassificazioneAzione
from soggetti.models import Soggetto
from territori.models import Territorio
from django.utils import simplejson


class AggregatoView(object):


    def get_map_context(self, territorio=None, **options):

        extent = territorio.geom.extent if territorio else Territorio.objects.filter(territorio='R').extent()

        data = {}

        zoom = options.get('zoom', 6)
        zoomrange = options.get('zoomrange', [6, 7])
        poi = options.get('poi', False)

        if territorio:
            if territorio.territorio == Territorio.TERRITORIO.R:
                zoom = 8
                zoomrange =[8,10]
                data = {
                    "comuni-r-%s"%territorio.cod_reg: {
                        'numero': dict(
                            (t['cod_com'], t['s']) for t in Territorio.objects.filter(territorio='C', cod_reg=territorio.cod_reg ).annotate(s=Count('progetto')).values('cod_com','s')
                        ),
                        'costo': dict(
                            (t['cod_com'], t['s']) for t in Territorio.objects.filter(territorio='C', cod_reg=territorio.cod_reg ).annotate(s=Sum('progetto__fin_totale_pubblico')).values('cod_com','s')
                        ),
                        'pagamento': dict(
                            (t['cod_com'], t['s']) for t in Territorio.objects.filter(territorio='C', cod_reg=territorio.cod_reg ).annotate(s=Sum('progetto__pagamento')).values('cod_com','s')
                        )
                    },
                    "province-r-%s"%territorio.cod_reg: {
                        'numero': dict(
                            (t.cod_prov, Territorio.objects.filter(cod_prov=t.cod_prov).aggregate(s=Count('progetto'))['s'])
                                for t in Territorio.objects.filter(territorio='P', cod_reg=territorio.cod_reg)
                        ),
                        'costo': dict(
                            (t.cod_prov, Territorio.objects.filter(cod_prov=t.cod_prov).aggregate(s=Sum('progetto__fin_totale_pubblico'))['s'])
                                for t in Territorio.objects.filter(territorio='P', cod_reg=territorio.cod_reg)
                        ),
                        'pagamento': dict(
                            (t.cod_prov, Territorio.objects.filter(cod_prov=t.cod_prov).aggregate(s=Sum('progetto__pagamento'))['s'])
                                for t in Territorio.objects.filter(territorio='P', cod_reg=territorio.cod_reg)
                        )
                    }
                }
            elif territorio.territorio == Territorio.TERRITORIO.P:
                zoom = 10
                zoomrange =[10,11]
                data = {
                    'comuni-p-%s'%territorio.cod_prov: {
                        'numero': dict(
                            (t['cod_com'], t['s']) for t in Territorio.objects.filter(territorio='C', cod_prov=territorio.cod_prov ).annotate(s=Count('progetto')).values('cod_com','s')
                        ),
                        'costo': dict(
                            (t['cod_com'], t['s']) for t in Territorio.objects.filter(territorio='C', cod_prov=territorio.cod_prov ).annotate(s=Sum('progetto__fin_totale_pubblico')).values('cod_com','s')
                        ),
                        'pagamento': dict(
                            (t['cod_com'], t['s']) for t in Territorio.objects.filter(territorio='C', cod_prov=territorio.cod_prov ).annotate(s=Sum('progetto__pagamento')).values('cod_com','s')
                        )
                    },
                }
            elif territorio.territorio == Territorio.TERRITORIO.C:
                zoom = 5
                zoomrange =[5]
                poi = territorio.geom.centroid.coords
                extent = Territorio.objects.filter(territorio='R').extent()
        else:
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
                        (t.cod_reg, Territorio.objects.filter(cod_reg=t.cod_reg).aggregate(s=Sum('progetto__pagamento'))['s'])
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
                        (t.cod_prov, Territorio.objects.filter(cod_prov=t.cod_prov).aggregate(s=Sum('progetto__pagamento'))['s'])
                            for t in Territorio.objects.filter(territorio='P')
                    )
                }
            }

        return {
            'extent' : "[{{lon: {0}, lat: {1}}},{{lon: {2}, lat: {3}}}]".format( *extent ),
            'zoomlev' : zoom,
            'zoomrange' : simplejson.dumps( zoomrange ),
            'data' : simplejson.dumps( data ),
            'poi' : simplejson.dumps( poi ),
        }


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

        context['top_progetti_per_costo'] = Progetto.objects.filter(fin_totale_pubblico__isnull=False).order_by('-fin_totale_pubblico')[:3]

        #context['ultimi_progetti_avviati'] = Progetto.objects.filter(data_inizio_effettiva__lte=datetime.now()).order_by('-data_inizio_effettiva')[:3]
        #context['ultimi_progetti_conclusi'] = Progetto.objects.filter(data_fine_effettiva__lte=datetime.now()).order_by('-data_fine_effettiva')[:3]

        context['numero_soggetti'] = Soggetto.objects.count()

        context['map'] = self.get_map_context()
        context['temi_principali'] = [
            {
            'object': tema,
            'data': Tema.objects.\
                filter(tema_superiore=tema).\
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
                aggregate(numero=Count('progetto_set'),
                          costo=Sum('progetto_set__fin_totale_pubblico'),
                          pagamento=Sum('progetto_set__pagamento'))
            } for natura in ClassificazioneAzione.objects.tematiche()
        ]

        return context

