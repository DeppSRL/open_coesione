from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.db.models import Count, Sum
from open_coesione.views import AggregatoView, AccessControlView
from progetti.models import Progetto, Tema, ClassificazioneAzione
from soggetti.models import Soggetto
from territori.models import Territorio

class SoggettiView(AggregatoView, TemplateView):
    #raise Exception("Class SoggettiView needs to be implemented")
    pass

class SoggettoView(AggregatoView, DetailView):
    model = Soggetto

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(SoggettoView, self).get_context_data(**kwargs)

        context['total_cost'] = Progetto.objects.totale_costi(soggetto=self.object)
        context['total_cost_paid'] = Progetto.objects.totale_costi_pagati(soggetto=self.object)
        context['total_projects'] = Progetto.objects.totale_progetti(soggetto=self.object)
        context['cost_payments_ratio'] = "{0:.0%}".format(context['total_cost_paid'] / context['total_cost'] if context['total_cost'] > 0.0 else 0.0)

        context['temi_principali'] = [
            {
            'object': tema,
            'data': Tema.objects.\
                        filter(tema_superiore=tema).\
                        filter(progetto_set__soggetto_set__pk=self.object.pk).
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
                        filter(progetto_set__soggetto_set__pk=self.object.pk).\
                        aggregate(numero=Count('progetto_set'),
                            costo=Sum('progetto_set__fin_totale_pubblico'),
                            pagamento=Sum('progetto_set__pagamento'))
            } for natura in ClassificazioneAzione.objects.tematiche()
        ]


        # calcolo dei collaboratori con cui si spartiscono piu' soldi
        collaboratori = {}
        for soggetti in [x.soggetti  for x in self.object.progetti]:
            for s in soggetti:
                if s == self.object:
                    continue
                if not s in collaboratori:
                    collaboratori[s] = 0
                collaboratori[s] += 1

        context['top_collaboratori'] = sorted(
            # create a list of dict with partners
            [{'soggetto':key, 'numero':collaboratori[key]} for key in collaboratori],
            # sorted by totale
            key = lambda c: c['numero'],
            # desc
            reverse = True )[:5]

        # calcolo dei progetti con piu' fondi
        context['top_progetti'] = self.object.progetti.order_by('-fin_totale_pubblico')[:5]

        context['map'] = self.get_map_context( )


        return context