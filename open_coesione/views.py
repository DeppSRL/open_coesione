# coding=utf-8
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, BadHeaderError, HttpResponse
from django.views.generic import ListView

import os
from django.views.generic.base import TemplateView
from django.db.models import Count, Sum
from open_coesione.forms import ContactForm
from open_coesione.models import PressReview
from open_coesione.settings import PROJECT_ROOT
from progetti.models import Progetto, Tema, ClassificazioneAzione, DeliberaCIPE
from soggetti.models import Soggetto
from territori.models import Territorio
from django.conf import settings
from django.db import models
from django.core.cache import cache


def cached_context(get_context_data):
    """
    Questo decoratore viene usato per fare la cache del metodo get_context_data
    chiamato da get() o post() nelle viste.
    Si occupa di creare una chiave univoca per la richiesta,
    dopodiche controlla se è presente in cache;
    se lo è, restituisce il contesto precedentemente elaborato,
    altrimenti lo genera e lo salva con quella chiave
    """

    def decorator(self, **kwargs):
        key = 'context' + self.request.get_full_path()
        context = cache.get(key)
        if context is None:
            context = get_context_data(self, **kwargs)
            cache.set(key, context)
        return context
    return decorator


class AccessControlView(object):
    """
    Define access control for the view
    """
#    @method_decorator(login_required)
#    def dispatch(self, *args, **kwargs):
#        return super(AccessControlView, self).dispatch(*args, **kwargs)
    pass


class CGView(TemplateView):
    """
    cache generator view
    generates the curl invocations to pre-navigate the time-consuming urls
    can be filtered by maps or pages
    """

    template_name = 'cache_generator.txt'
    filter = None

    def get_context_data(self, **kwargs):
        context = super(CGView, self).get_context_data(**kwargs)
        context['tematizzazioni'] = '{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti}'
        context['regioni'] = Territorio.objects.filter(territorio='R')
        context['province'] = Territorio.objects.filter(territorio='P')
        context['temi'] = Tema.objects.principali()
        context['nature'] = ClassificazioneAzione.objects.nature()
        context['soggetti'] = Soggetto.objects.annotate(c=Count('progetto')).filter(c__gte=1000).order_by('c')
        context['base_url'] = "http://{0}".format(Site.objects.get_current())
        context['curl_cmd'] = "curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\\n'"
        context['log_file'] = "cache_generation.log"

        context['maps'] = True
        context['pages'] = True
        if self.filter == 'maps':
            context['pages'] = False
        if self.filter == 'pages':
            context['maps'] = False


        return context


class AggregatoView(object):

    def get_aggregate_data(self, context, **filter):

        if len(filter) > 1:
            raise Exception('Only one filter kwargs is accepted')

        # read tematizzazione GET param
        tematizzazione = self.request.GET.get('tematizzazione', 'totale_costi')

        context = dict(
            totale_costi=Progetto.objects.totale_costi(**filter),
            totale_pagamenti=Progetto.objects.totale_pagamenti(**filter),
            totale_progetti=Progetto.objects.totale_progetti(**filter),
            tematizzazione=tematizzazione,
            **context
        )
        context['percentuale_costi_pagamenti'] = "{0:.0%}".format(
            context['totale_pagamenti'] /
            context['totale_costi'] if context['totale_costi'] > 0.0 else 0.0
        )


        # create tematizzazione field
        # aggregate_field = {
        #     'totale_costi': Sum('progetto_set__fin_totale_pubblico'),
        #     'totale_pagamenti': Sum('progetto_set__pagamento'),
        #     'totale_progetti': Count('progetto_set')
        # }[ context['tematizzazione'] ]

        query_models = {
            'temi_principali' : {
                'manager': Tema.objects,
                'parent_class_field': 'tema_superiore',
                'manager_parent_method': 'principali',
                'filter_name': 'tema',
            },
            'nature_principali' : {
                'manager': ClassificazioneAzione.objects,
                'parent_class_field': 'classificazione_superiore',
                'manager_parent_method': 'tematiche',
                'filter_name': 'classificazione'
            }
        }

        # specialize the filter
        if 'territorio' in filter:
            query_filters = dict(territorio=filter['territorio'])
        elif 'soggetto' in filter:
            query_filters = dict(soggetto=filter['soggetto'])
        elif 'tema' in filter:
            query_filters = dict(tema=filter['tema'])
            del query_models['temi_principali']
        elif 'classificazione' in filter:
            query_filters = dict(classificazione=filter['classificazione'])
            del query_models['nature_principali']
        else:
            # homepage takes all
            query_filters = {}

        for name in query_models:
            context[name] = []
            # takes all root models ( principali or tematiche )
            for obj in getattr(query_models[name]['manager'], query_models[name]['manager_parent_method'])():
                q = query_filters.copy()
                # add %model%_superiore to query filters
                q[query_models[name]['filter_name']] = obj
                # make query and add totale to object
                # obj.tot = query_models[name]['manager'].filter( **q ).aggregate( tot=aggregate_field )['tot']
                obj.tot = getattr(Progetto.objects, context['tematizzazione'])(**q)
                # add object to right context
                context[name].append(obj)

        context['map_legend_colors'] = settings.MAP_COLORS

        if self.request.GET.get('pro_capite'):
            context['mappa_pro_capite'] = True

        return context

    def top_comuni_pro_capite(self, filters, qnt=5):

        queryset = Territorio.objects.comuni().filter( **filters ).defer('geom')\
            .annotate( totale=models.Sum('progetto__fin_totale_pubblico'))\
            .filter( totale__isnull=False )

        def pro_capite_order(territorio):
            territorio.totale_pro_capite = territorio.totale / territorio.popolazione_totale if territorio.popolazione_totale else 0.0
            return territorio.totale_pro_capite

        return sorted(
            queryset,
            key= pro_capite_order,
            reverse=True
        )[:qnt]


class HomeView(AccessControlView, AggregatoView, TemplateView):
    template_name = 'homepage.html'

    @cached_context
    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        context = self.get_aggregate_data(context)

        context['top_progetti'] = Progetto.objects.filter(fin_totale_pubblico__isnull=False).order_by('-fin_totale_pubblico')[:5]

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

        context['delibere'] = DeliberaCIPE.objects.all()
        context['totale_fondi_assegnati'] = DeliberaCIPE.objects.aggregate(s = Sum('fondi_assegnati'))['s']

        return context


class SpesaCertificataView(RisorseView):
    template_name = 'flat/spesa_certificata.html'

    def get_context_data(self, **kwargs):

        import csv

        context = super(SpesaCertificataView, self).get_context_data(**kwargs)

        context['chart_tables'] = []

        for tipo in ['competitivita_fesr', 'competitivita_fse', 'convergenza_fesr', 'convergenza_fse']:

            context['chart_tables'].append((tipo, csv.reader( open(os.path.join(PROJECT_ROOT, 'static/csv/spesa_certificata/%s.csv' % tipo))) ))

        return context


class ContactView(TemplateView):

    def get_context_data(self, **kwargs):

#        if self.request.method == 'POST': # If the form has been submitted...
#            form = ContactForm( self.request.POST ) # A form bound to the POST data
#            if form.is_valid(): # All validation rules pass
#                # Process the data in form.cleaned_data
#                form.send_mail()
#                return HttpResponseRedirect( reverse('oc_contatti') ) # Redirect after POST
#        else:
#            form = ContactForm() # An unbound form

        return {
            'contact_form' : ContactForm() if self.request.method == 'GET' else ContactForm( self.request.POST ),
            'contact_form_submitted' : self.request.GET.get('completed','') == 'true'
        }

    def post(self, request, *args, **kwargs):
        form = ContactForm( self.request.POST ) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            try:
                # Process the data in form.cleaned_data
                form.execute()
            except BadHeaderError:
                return HttpResponse('Invalid header found.')

            return HttpResponseRedirect( "{0}?completed=true".format(reverse('oc_contatti')) ) # Redirect after POST

        return self.get(request, *args, **kwargs)


class PressView(ListView):
    model = PressReview
    template_name = 'flat/press_review.html'
    queryset = PressReview.objects.all().order_by('-published_at')

