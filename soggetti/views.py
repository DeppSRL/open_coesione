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
    context_object_name = 'soggetto'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(SoggettoView, self).get_context_data(**kwargs)

        context = self.get_aggregate_data(context, soggetto=self.object)

        # calcolo dei collaboratori con cui si spartiscono piu' soldi
        collaboratori = {}
        for soggetti in [x.soggetti for x in self.object.progetti]:
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

        # calcolo dei comuni un cui questo soggetto ha operato di piu'
        context['territori_piu_finanziati_pro_capite'] = Territorio.objects.comuni()\
            .filter(progetto__soggetto_set__pk=self.object.pk)\
            .annotate(totale=Sum('progetto__fin_totale_pubblico'))\
            .order_by('-totale')[:5]


        #context['map'] = self.get_map_context( )

        context['lista_finanziamenti_per_regione'] = [
            (regione,float(Progetto.objects.nel_territorio( regione ).filter(soggetto_set__pk=self.object.pk).aggregate(totale=Sum('fin_totale_pubblico'))['totale'] or 0))
            for regione in Territorio.objects.regioni()
        ]


        return context