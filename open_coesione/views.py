# coding=utf-8
import logging
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, BadHeaderError, HttpResponse
from django.utils.datastructures import SortedDict
from django.views.generic import ListView

import os
from django.views.generic.base import TemplateView, RedirectView
from django.db.models import Count, Sum
from open_coesione.forms import ContactForm
from open_coesione.models import PressReview, Pillola
from open_coesione.settings import PROJECT_ROOT
from progetti.models import Progetto, Tema, ClassificazioneAzione, DeliberaCIPE
from soggetti.models import Soggetto
from territori.models import Territorio
from django.conf import settings
from django.db import models
from django.core.cache import cache

def cached_context(get_context_data):
    """
    This decorator is used to cache the ``get_context_data()`` method
    called by a ``get()`` or ``post()`` in the views.
    It generates a unique key for the request,
    checks if the key is in the cache:
    if it is, then it returns it,
    else it will generate and save the key, before returning it.
    """

    def decorator(self, **kwargs):
        key = 'context' + self.request.get_full_path()
        context = cache.get(key)
        if context is None:
            context = get_context_data(self, **kwargs)
            serializable_context = context.copy()
            serializable_context.pop('view', None)
            cache.set(key, serializable_context)
        return context
    return decorator


class PilloleView(ListView):
    model = Pillola
    template_name = "pillole.html"

    def get_queryset(self):
        queryset = super(PilloleView, self).get_queryset()
        return queryset.order_by('-published_at', '-id')




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
        elif 'programma' in filter:
            query_filters = dict(programma=filter['programma'])
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


    def get_context_data(self, **kwargs):

        ##
        # low-level caching, to allow adding latest_pillole
        # out of the cached context (fast-refresh)
        ##
        key = 'context' + self.request.get_full_path()
        context = cache.get(key)
        if context is None:
            context = super(HomeView, self).get_context_data(**kwargs)
            context = self.get_aggregate_data(context)
            context['top_progetti'] = Progetto.objects.filter(fin_totale_pubblico__isnull=False).order_by('-fin_totale_pubblico')[:5]
            context['numero_soggetti'] = Soggetto.objects.count()
            serializable_context = context.copy()
            serializable_context.pop('view', None)
            cache.set(key, serializable_context)

        context['latest_pillole'] = Pillola.objects.order_by('-published_at', '-id')[:3]
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
    template_name = 'flat/spesa_certificata_grafici.html'

    def get_context_data(self, **kwargs):

        import csv

        context = super(SpesaCertificataView, self).get_context_data(**kwargs)

        context['chart_tables'] = []

        for tipo in ['competitivita_fesr', 'competitivita_fse', 'convergenza_fesr', 'convergenza_fse']:

            context['chart_tables'].append((tipo, csv.reader( open(os.path.join(PROJECT_ROOT, 'static/csv/spesa_certificata/%s.csv' % tipo))) ))

        return context


class ContactView(TemplateView):

    def get_context_data(self, **kwargs):

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


class OpendataView(TemplateView):
    """
    Basic template view with an extended context, containing the pointers
    to the downloadable files.
    """
    def get_context_data(self, **kwargs):
        context = super(OpendataView, self).get_context_data(**kwargs)

        data_date = '20131231'
        cipe_date = '20121231'
        spesa_date = '20131231'
        istat_date = '20140221'

        regions = SortedDict([
            ('VDA', 'Valle d\'Aosta'),
            ('PIE', 'Piemonte'),
            ('LOM', 'Lombardia'),
            ('TN_BZ', 'Trento e Bolzano'),
            ('VEN', 'Veneto'),
            ('FVG', 'Friuli-Venezia Giulia'),
            ('LIG', 'Liguria'),
            ('EMR', 'Emilia-Romagna'),
            ('TOS', 'Toscana'),
            ('UMB', 'Umbria'),
            ('MAR', 'Marche'),
            ('LAZ', 'Lazio'),
            ('ABR', 'Abruzzo'),
            ('CAM', 'Campania'),
            ('MOL', 'Molise'),
            ('PUG', 'Puglia'),
            ('CAL', 'Calabria'),
            ('BAS', 'Basilicata'),
            ('SIC', 'Sicilia'),
            ('SAR', 'Sardegna'),
            ('MULTI', 'Multi-regionali'),
        ])

        themes = SortedDict([
            ('AGENDA_DIGITALE', 'Agenda digitale'),
            ('AMBIENTE', 'Ambiente'),
            ('CULTURA_TURISMO', 'Cultura e turismo'),
            ('COMPETITIVITA_IMPRESE', u'Competitività imprese'),
            ('ENERGIA', 'Energia'),
            ('INCLUSIONE_SOCIALE', 'Inclusione sociale'),
            ('ISTRUZIONE', 'Istruzione'),
            ('OCCUPAZIONE', 'Occupazione'),
            ('RAFFORZAMENTO_PA', 'Rafforzamento PA'),
            ('RICERCA_INNOVAZIONE', 'Ricerca e innovazione'),
            ('CITTA_RURALE', 'Città e aree rurali'),
            ('INFANZIA_ANZIANI', 'Infanzia e anziani'),
            ('TRASPORTI', 'Trasporti'),
        ])


        fs_sections = SortedDict([
            ('prog', { 'name': 'progetti',
                       'complete_file': self.get_complete_file('progetti_FS0713_{0}.zip'.format(data_date)),
                       'regional_files': self.get_regional_files('prog', 'FS0713', regions, data_date),
#                       'theme_files': self.get_theme_files('prog', 'progetti', themes, data_date)
                }
            ),
            ('sog', { 'name': 'soggetti',
                      'complete_file': self.get_complete_file('soggetti_FS0713_{0}.zip'.format(data_date)),
                      'regional_files': self.get_regional_files('sog', 'FS0713', regions, data_date),
#                      'theme_files': self.get_theme_files('sog', 'soggetti', themes, data_date)
                }
            ),
            ('loc', { 'name': 'localizzazioni',
                      'complete_file': self.get_complete_file('localizzazioni_FS0713_{0}.zip'.format(data_date)),
                      'regional_files': self.get_regional_files('loc', 'FS0713', regions, data_date),
#                      'theme_files': self.get_theme_files('loc', 'localizzazioni', themes, data_date)
                }
            ),
            ('pag', { 'name': 'pagamenti',
                      'complete_file': self.get_complete_file('pagamenti_FS0713_{0}.zip'.format(data_date)),
                      'regional_files': self.get_regional_files('pag', 'FS0713', regions, data_date),
#                      'theme_files': self.get_theme_files('pag', 'pagamenti', themes, data_date)
                }
            ),
        ])
        fs_metadata_file = self.get_complete_file("metadati_attuazione.xls")

        fsc_sections = SortedDict([
            ('prog', { 'name': 'progetti',
                       'complete_file': self.get_complete_file('progetti_FSC0713_{0}.zip'.format(data_date)),
                }
            ),
            ('sog', { 'name': 'soggetti',
                      'complete_file': self.get_complete_file('soggetti_FSC0713_{0}.zip'.format(data_date)),
                }
            ),
            ('loc', { 'name': 'localizzazioni',
                      'complete_file': self.get_complete_file('localizzazioni_FSC0713_{0}.zip'.format(data_date)),
                }
            ),
            ('pag', { 'name': 'pagamenti',
                      'complete_file': self.get_complete_file('pagamenti_FSC0713_{0}.zip'.format(data_date)),
                }
            ),
        ])
        fsc_metadata_file = self.get_complete_file("metadati_attuazione.xls")

        cipe_sections = SortedDict([
            ('prog', { 'name': 'progetti',
                       'complete_file': self.get_complete_file("assegnazioni_CIPE_{0}.zip".format(cipe_date)),
                }
            ),
            ('loc', { 'name': 'localizzazioni',
                      'complete_file': self.get_complete_file("localizzazioni_CIPE_{0}.zip".format(cipe_date)),
                }
            ),
        ])
        cipe_metadata_file = self.get_complete_file("metadati_attuazione.xls")


        context['spesa_dotazione_file'] = self.get_complete_file("Dotazioni_Certificazioni_{0}.xlsx".format(spesa_date))
        context['spesa_target_file'] = self.get_complete_file("Target_Risultati_{0}.xlsx".format(spesa_date))

        context['istat_data_file'] = self.get_complete_file("Indicatori_regionali_{0}.zip".format(istat_date))
        context['istat_metadata_file'] = self.get_complete_file("Metainformazione.xls")

        context['cpt_pa_in_file'] = self.get_complete_file("PA_ENTRATE_1996-2011.zip".format(istat_date))
        context['cpt_pa_out_file'] = self.get_complete_file("PA_SPESE_1996-2011.zip".format(istat_date))
        context['cpt_spa_in_file'] = self.get_complete_file("SPA_ENTRATE_1996-2011.zip".format(istat_date))
        context['cpt_spa_out_file'] = self.get_complete_file("SPA_SPESE_1996-2011.zip".format(istat_date))
        context['cpt_metadata_file'] = self.get_complete_file("CPT_Metadati_perCSV_def.xls")

        context['data_date'] = data_date
        context['fs_sections'] = fs_sections
        context['fsc_sections'] = fsc_sections
        context['cipe_sections'] = cipe_sections
        context['fs_metadata_file'] = fs_metadata_file
        context['fsc_metadata_file'] = fsc_metadata_file
        context['cipe_metadata_file'] = cipe_metadata_file

        return  context

    def get_complete_file(self, file_name):
        file_path = os.path.join(settings.MEDIA_ROOT, "open_data", file_name)
        file_size = os.stat(file_path).st_size
        return {
            'file_name': file_name,
            'file_size': file_size
        }


    def get_theme_files(selfself, section_code, section_name, themes, data_date):
        files = []
        for theme_code, theme_name in themes.items():
            file_name = "{0}_{1}_{2}.zip".format(section_code, theme_code, data_date)
            file_path = os.path.join(settings.MEDIA_ROOT, "open_data", section_name, file_name)
            file_size = os.stat(file_path).st_size
            files.append({
                'theme_name': theme_name,
                'file_name': file_name,
                'file_size': file_size
            })
        return files

    def get_regional_files(self, section_code, prefix, regions, data_date):
        files = []
        for reg_code, reg_name in regions.items():
            file_name = "{0}_{1}_{2}_{3}.zip".format(section_code, prefix, reg_code, data_date)
            file_path = os.path.join(settings.MEDIA_ROOT, "open_data", "regione", file_name)
            file_size = os.stat(file_path).st_size
            files.append({
                'region_name': reg_name,
                'file_name': file_name,
                'file_size': file_size
            })
        return files


class PilloleRedirectView(RedirectView):

   def get_redirect_url(self, **kwargs):
        return "/media/pillole/{0}".format(kwargs['path'])


class OpendataRedirectView(RedirectView):

   def get_redirect_url(self, **kwargs):
        return "/media/open_data/{0}".format(kwargs['path'])
