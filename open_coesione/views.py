from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from datetime import datetime
import os
from django.views.generic.base import TemplateView, View
from django.db.models import Count, Sum
from open_coesione.settings import PROJECT_ROOT
from progetti.models import Progetto, Tema, ClassificazioneOggetto, ClassificazioneAzione
from soggetti.models import Soggetto
from territori.models import Territorio
from django.utils import simplejson
from django.conf import settings


class AccessControlView(object):
    """
    Define access control for the view
    """
#    @method_decorator(login_required)
#    def dispatch(self, *args, **kwargs):
#        return super(AccessControlView, self).dispatch(*args, **kwargs)
    pass

class AggregatoView(object):
    def get_aggregate_data(self,context, **filter):

        if len(filter) > 1:
            raise Exception('Only one filter kwargs is accepted')

        context = dict(
            totale_costi    =   Progetto.objects.totale_costi(**filter),
            totale_pagamenti=   Progetto.objects.totale_pagamenti(**filter),
            totale_progetti =   Progetto.objects.totale_progetti(**filter),
            **context
        )
        context['percentuale_costi_pagamenti'] = "{0:.0%}".format(context['totale_pagamenti'] / context['totale_costi'] if context['totale_costi'] > 0.0 else 0.0)

        # read tematizzazione GET param
        context['tematizzazione'] = self.request.GET.get('tematizzazione', 'totale_costi')

        #if filters.has_key('tema') or filters.has_key('natura'):

        # create tematizzazione field
        aggregate_field = {
            'totale_costi': Sum('progetto_set__fin_totale_pubblico'),
            'totale_pagamenti': Sum('progetto_set__pagamento'),
            'totale_progetti': Count('progetto_set')
        }[ context['tematizzazione'] ]

        query_models = {
            'temi_principali' : {
                'manager': Tema.objects,
                'parent_class_field': 'tema_superiore',
                'manager_parent_method': 'principali'
            },
            'nature_principali' : {
                'manager': ClassificazioneAzione.objects,
                'parent_class_field': 'classificazione_superiore',
                'manager_parent_method': 'tematiche'
            }
        }

        # specialize the filter
        if filter.has_key('territorio'):
            query_filters = dict( **filter['territorio'].get_cod_dict(prefix='progetto_set__territorio_set__') )
        elif filter.has_key('tema'):
            query_filters = dict(progetto_set__tema__tema_superiore=filter['tema'])
            del query_models['temi_principali']
        elif filter.has_key('classificazione'):
            query_filters = dict(progetto_set__classificazione_azione__classificazione_superiore=filter['classificazione'])
            del query_models['nature_principali']
        else:
            # homepage takes all
            query_filters = {}

        for name in query_models:
            context[name] = []
            # takes all root models ( principali or tematiche )
            for object in getattr(query_models[name]['manager'], query_models[name]['manager_parent_method'])():
                q = query_filters.copy()
                # add %model%_superiore to query filters
                q[query_models[name]['parent_class_field']] = object
                # make query and add totale to object
                object.tot = query_models[name]['manager'].filter( **q ).aggregate( tot=aggregate_field )['tot']
                # add object to right context
                context[name].append( object )

        context['map_legend_colors'] = settings.MAP_COLORS

        return context



class HomeView(AccessControlView, AggregatoView, TemplateView):
    template_name = 'homepage.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        context = self.get_aggregate_data(context)

        context['top_progetti_per_costo'] = Progetto.objects.filter(fin_totale_pubblico__isnull=False).order_by('-fin_totale_pubblico')[:3]

        #context['ultimi_progetti_avviati'] = Progetto.objects.filter(data_inizio_effettiva__lte=datetime.now()).order_by('-data_inizio_effettiva')[:3]
        #context['ultimi_progetti_conclusi'] = Progetto.objects.filter(data_fine_effettiva__lte=datetime.now()).order_by('-data_fine_effettiva')[:3]

        context['numero_soggetti'] = Soggetto.objects.count()

        return context

class RisorseView(AccessControlView, TemplateView):
    def get_context_data(self, **kwargs):
        context = super(RisorseView, self).get_context_data(**kwargs)
        context['risorsa'] = True
        return  context

class FondiView(RisorseView):
    template_name = 'flat/fonti_finanziamento.html'

    def get_context_data(self, **kwargs):

        context = super(FondiView, self).get_context_data(**kwargs)

        import csv

        context['competitivita_fesr_fse'] = csv.reader(open(os.path.join(PROJECT_ROOT, 'static/csv/fondi_europei/competitivita_fesr_fse.csv')))

        context['fesr_data_comp'] = csv.reader(open(os.path.join(PROJECT_ROOT, 'static/csv/fondi_europei/competitivita_fesr.csv')))
        context['fse_data_comp'] = csv.reader(open(os.path.join(PROJECT_ROOT, 'static/csv/fondi_europei/competitivita_fse.csv')))

        context['convergenza_fesr_fse'] = csv.reader(open(os.path.join(PROJECT_ROOT, 'static/csv/fondi_europei/convergenza_fesr_fse.csv')))

        context['fesr_data_conv_regioni'] = csv.reader(open(os.path.join(PROJECT_ROOT, 'static/csv/fondi_europei/convergenza_fesr_regioni.csv')))
        context['fesr_data_conv_temi'] = csv.reader(open(os.path.join(PROJECT_ROOT, 'static/csv/fondi_europei/convergenza_fesr_temi.csv')))

        context['fse_data_conv_regioni'] = csv.reader(open(os.path.join(PROJECT_ROOT, 'static/csv/fondi_europei/convergenza_fse_regioni.csv')))
        context['fse_data_conv_temi'] = csv.reader(open(os.path.join(PROJECT_ROOT, 'static/csv/fondi_europei/convergenza_fse_temi.csv')))

        return context

