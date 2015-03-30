# coding=utf-8
import os
import urllib2
import glob

from django.views.generic.base import TemplateView, RedirectView, TemplateResponseMixin
from django.db.models import Sum
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, BadHeaderError, HttpResponse, Http404
from django.utils.datastructures import SortedDict
from django.views.generic import ListView
from django.conf import settings
from django.db import models
from django.core.cache import cache
from django.views.generic.detail import DetailView

from open_coesione.forms import ContactForm
from open_coesione.models import PressReview, Pillola, FAQ
from open_coesione.settings import PROJECT_ROOT
from progetti.models import Progetto, Tema, ClassificazioneAzione, DeliberaCIPE
from soggetti.models import Soggetto
from territori.models import Territorio

from tagging.views import TagFilterMixin
from open_coesione.mixins import DateFilterMixin


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


class XRobotsTagTemplateResponseMixin(TemplateResponseMixin):
    x_robots_tag = False

    def get_x_robots_tag(self):
        return self.x_robots_tag

    def render_to_response(self, context, **response_kwargs):
        response = super(XRobotsTagTemplateResponseMixin, self).render_to_response(context, **response_kwargs)
        if self.get_x_robots_tag():
            response['X-Robots-Tag'] = self.get_x_robots_tag()
        return response


class AggregatoMixin(object):
    def get_aggregate_data(self, context, **filter):
        if len(filter) > 1:
            raise Exception('Only one filter kwargs is accepted')

        if 'programma' in filter:
            raise Exception('Filter "programma" is deprecated')

        # read tematizzazione GET param
        tematizzazione = self.request.GET.get('tematizzazione', 'totale_costi')

        context = dict(
            totale_costi=Progetto.objects.totale_costi(**filter),
            totale_pagamenti=Progetto.objects.totale_pagamenti(**filter),
            totale_progetti=Progetto.objects.totale_progetti(**filter),
            tematizzazione=tematizzazione,
            **context
        )
        context['percentuale_costi_pagamenti'] = '{0:.0%}'.format(
            context['totale_pagamenti'] /
            context['totale_costi'] if context['totale_costi'] > 0.0 else 0.0
        )

        query_models = {
            'temi_principali': {
                'manager': Tema.objects,
                'parent_class_field': 'tema_superiore',
                'manager_parent_method': 'principali',
                'filter_name': 'tema',
            },
            'nature_principali': {
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
        elif 'programmi' in filter:
            query_filters = dict(programmi=filter['programmi'])
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
        if isinstance(filters, dict):
            args = []
            kwargs = filters
        else:
            args = filters
            kwargs = {}

        # add filters on active projects, to avoid computation errors
        kwargs.update({
            'progetto__active_flag': True,
        })

        queryset = Territorio.objects.comuni().filter(*args, **kwargs).defer('geom')\
            .annotate(totale=models.Sum('progetto__fin_totale_pubblico'))\
            .filter(totale__isnull=False)

        def pro_capite_order(territorio):
            territorio.totale_pro_capite = territorio.totale / territorio.popolazione_totale if territorio.popolazione_totale else 0.0
            return territorio.totale_pro_capite

        return sorted(
            queryset,
            key=pro_capite_order,
            reverse=True,
        )[:qnt]


class AccessControlView(object):
    """
    Define access control for the view
    """
    # @method_decorator(login_required)
    # def dispatch(self, *args, **kwargs):
    #     return super(AccessControlView, self).dispatch(*args, **kwargs)
    pass


class HomeView(AccessControlView, AggregatoMixin, TemplateView):
    @cached_context
    def get_cached_context_data(self):
        context = {}

        context = self.get_aggregate_data(context)

        context['numero_soggetti'] = Soggetto.objects.count()

        context['top_progetti'] = Progetto.objects.filter(fin_totale_pubblico__isnull=False).order_by('-fin_totale_pubblico', '-data_fine_effettiva')[:3]

        return context

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        context.update(self.get_cached_context_data())

        context['ultimi_progetti_conclusi'] = Progetto.objects.filter(privacy_flag=False).conclusi().order_by('-data_fine_effettiva', '-fin_totale_pubblico')[:3]

        context['pillola'] = Pillola.objects.order_by('-published_at', '-id')[:1][0]

        return context


# class HomeView(AccessControlView, AggregatoMixin, TemplateView):
#     def get_context_data(self, **kwargs):
#         """
#         low-level caching, to allow adding latest_pillole out of the cached context (fast-refresh)
#         """
#         key = 'context' + self.request.get_full_path()
#         context = cache.get(key)
#
#         if context is None:
#             context = super(HomeView, self).get_context_data(**kwargs)
#             context = self.get_aggregate_data(context)
#
#             context['top_progetti'] = Progetto.objects.filter(
#                 fin_totale_pubblico__isnull=False,
#             ).order_by('-fin_totale_pubblico')[:3]
#
#             context['numero_soggetti'] = Soggetto.objects.count()
#
#             serializable_context = context.copy()
#             serializable_context.pop('view', None)
#             cache.set(key, serializable_context)
#
#         context['ultimi_progetti_conclusi'] = Progetto.objects.filter(
#             data_fine_effettiva__lte=datetime.now(),
#             privacy_flag=False,
#         ).order_by('-data_fine_effettiva', '-fin_totale_pubblico')[:3]
#
#         context['pillola'] = Pillola.objects.order_by('-published_at', '-id')[:1][0]
#
#         return context


class RisorsaView(AccessControlView, TemplateView):
    def get_context_data(self, **kwargs):
        context = super(RisorsaView, self).get_context_data(**kwargs)
        context['risorsa'] = True

        return context


class FondiView(RisorsaView):
    def get_context_data(self, **kwargs):
        # import csv

        context = super(FondiView, self).get_context_data(**kwargs)

        # context['competitivita_fesr_fse'] = csv.reader(open(os.path.join(PROJECT_ROOT, 'static/csv/fondi_europei/competitivita_fesr_fse.csv')))

        # context['fesr_data_comp'] = csv.reader(open(os.path.join(PROJECT_ROOT, 'static/csv/fondi_europei/competitivita_fesr.csv')))
        # context['fse_data_comp'] = csv.reader(open(os.path.join(PROJECT_ROOT, 'static/csv/fondi_europei/competitivita_fse.csv')))

        # context['convergenza_fesr_fse'] = csv.reader(open(os.path.join(PROJECT_ROOT, 'static/csv/fondi_europei/convergenza_fesr_fse.csv')))

        # context['fesr_data_conv_regioni'] = csv.reader(open(os.path.join(PROJECT_ROOT, 'static/csv/fondi_europei/convergenza_fesr_regioni.csv')))
        # context['fesr_data_conv_temi'] = csv.reader(open(os.path.join(PROJECT_ROOT, 'static/csv/fondi_europei/convergenza_fesr_temi.csv')))

        # context['fse_data_conv_regioni'] = csv.reader(open(os.path.join(PROJECT_ROOT, 'static/csv/fondi_europei/convergenza_fse_regioni.csv')))
        # context['fse_data_conv_temi'] = csv.reader(open(os.path.join(PROJECT_ROOT, 'static/csv/fondi_europei/convergenza_fse_temi.csv')))

        context['delibere'] = DeliberaCIPE.objects.all()
        context['totale_fondi_assegnati'] = DeliberaCIPE.objects.aggregate(s=Sum('fondi_assegnati'))['s']

        return context


class SpesaCertificataGraficiView(RisorsaView):
    def get_context_data(self, **kwargs):
        import csv

        context = super(SpesaCertificataGraficiView, self).get_context_data(**kwargs)

        context['chart_tables'] = []
        for tipo in ['competitivita_fesr', 'competitivita_fse', 'convergenza_fesr', 'convergenza_fse']:
            context['chart_tables'].append((tipo, csv.reader(open(os.path.join(PROJECT_ROOT, 'static/csv/spesa_certificata/{0}.csv'.format(tipo))))))

        return context


class ContactView(TemplateView):
    def get_context_data(self, **kwargs):
        return {
            'contact_form': ContactForm() if self.request.method == 'GET' else ContactForm(self.request.POST),
            'contact_form_submitted': self.request.GET.get('completed', '') == 'true'
        }

    def post(self, request, *args, **kwargs):
        form = ContactForm(self.request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            try:
                # Process the data in form.cleaned_data
                form.execute()
            except BadHeaderError:
                return HttpResponse('Invalid header found.')

            return HttpResponseRedirect('{0}?completed=true'.format(reverse('oc-contatti')))  # Redirect after POST

        return self.get(request, *args, **kwargs)


class OpendataView(TemplateView):
    @cached_context
    def get_context_data(self, **kwargs):
        context = super(OpendataView, self).get_context_data(**kwargs)

        context['oc_sections'] = SortedDict([
            ('prog', {
                'name': 'progetti',
                'complete_file': self.get_complete_localfile('progetti_OC.zip'),
                'regional_files': self.get_regional_files('prog', 'OC'),
            }),
            ('sog', {
                'name': 'soggetti',
                'complete_file': self.get_complete_localfile('soggetti_OC.zip'),
                'regional_files': self.get_regional_files('sog', 'OC'),
            }),
            ('loc', {
                'name': 'localizzazioni',
                'complete_file': self.get_complete_localfile('localizzazioni_OC.zip'),
                'regional_files': self.get_regional_files('loc', 'OC'),
            }),
            ('pag', {
                'name': 'pagamenti',
                'complete_file': self.get_complete_localfile('pagamenti_OC.zip'),
                'regional_files': self.get_regional_files('pag', 'OC'),
            }),
        ])

        context['fs_sections'] = SortedDict([
            ('prog', {
                'name': 'progetti',
                'complete_file': self.get_complete_localfile('progetti_FS0713.zip'),
                'regional_files': self.get_regional_files('prog', 'FS0713'),
                # 'theme_files': self.get_theme_files('prog', 'progetti')
            }),
            ('sog', {
                'name': 'soggetti',
                'complete_file': self.get_complete_localfile('soggetti_FS0713.zip'),
                'regional_files': self.get_regional_files('sog', 'FS0713'),
                # 'theme_files': self.get_theme_files('sog', 'soggetti')
            }),
            ('loc', {
                'name': 'localizzazioni',
                'complete_file': self.get_complete_localfile('localizzazioni_FS0713.zip'),
                'regional_files': self.get_regional_files('loc', 'FS0713'),
                # 'theme_files': self.get_theme_files('loc', 'localizzazioni')
            }),
            ('pag', {
                'name': 'pagamenti',
                'complete_file': self.get_complete_localfile('pagamenti_FS0713.zip'),
                'regional_files': self.get_regional_files('pag', 'FS0713'),
                # 'theme_files': self.get_theme_files('pag', 'pagamenti')
            }),
        ])

        context['fsc_sections'] = SortedDict([
            ('prog', {
                'name': 'progetti',
                'complete_file': self.get_complete_localfile('progetti_FSC0713.zip'),
            }),
            ('sog', {
                'name': 'soggetti',
                'complete_file': self.get_complete_localfile('soggetti_FSC0713.zip'),
            }),
            ('loc', {
                'name': 'localizzazioni',
                'complete_file': self.get_complete_localfile('localizzazioni_FSC0713.zip'),
            }),
            ('pag', {
                'name': 'pagamenti',
                'complete_file': self.get_complete_localfile('pagamenti_FSC0713.zip'),
            }),
        ])

        context['pac_sections'] = SortedDict([
            ('prog', {
                'name': 'progetti',
                'complete_file': self.get_complete_localfile('progetti_PAC.zip'),
            }),
            ('sog', {
                'name': 'soggetti',
                'complete_file': self.get_complete_localfile('soggetti_PAC.zip'),
            }),
            ('loc', {
                'name': 'localizzazioni',
                'complete_file': self.get_complete_localfile('localizzazioni_PAC.zip'),
            }),
            ('pag', {
                'name': 'pagamenti',
                'complete_file': self.get_complete_localfile('pagamenti_PAC.zip'),
            }),
        ])

        context['cipe_sections'] = SortedDict([
            ('prog', {
                'name': 'progetti',
                'complete_file': self.get_complete_localfile('assegnazioni_CIPE.zip'),
            }),
            ('loc', {
                'name': 'localizzazioni',
                'complete_file': self.get_complete_localfile('localizzazioni_CIPE.zip'),
            }),
        ])

        context['oc_metadata_file'] = self.get_complete_localfile('Metadati_OC.xls')
        context['oc_utility_metadata_file'] = self.get_complete_localfile('Utility Metadati OC.xls')

        context['metadata_file'] = self.get_complete_localfile('Metadati_attuazione.xls')
        context['utility_metadata_file'] = self.get_complete_localfile('Utility Metadati Attuazione.xls')

        context['spesa_dotazione_file'] = self.get_complete_localfile('Dotazioni_Certificazioni.xls')
        context['spesa_target_file'] = self.get_complete_localfile('Target_Risultati.xls')

        # context['istat_data_file'] = self.get_complete_localfile('Indicatori_regionali.zip')
        # context['istat_metadata_file'] = self.get_complete_localfile('Metainformazione.xls')
        istat_path = 'http://www.istat.it/storage/politiche-sviluppo/{0}'
        context['istat_data_file'] = self.get_complete_remotefile(istat_path.format('Archivio_unico_indicatori_regionali.zip'))
        context['istat_metadata_file'] = self.get_complete_remotefile(istat_path.format('Metainformazione.xls'))

        context['indagine_data_file'] = self.get_complete_localfile('indagine_data.zip')
        context['indagine_metadata_file'] = self.get_complete_localfile('indagine_metadata.xls')

        cpt_path = 'http://www.dps.gov.it/opencms/export/sites/dps/it/documentazione/politiche_e_attivita/CPT/{0}/{1}'
        cpt_subpath = 'BD_CPT/2014_CSV/CSV'
        context['cpt_pa_in_file'] = self.get_complete_remotefile(cpt_path.format(cpt_subpath, 'PA_ENTRATE_1996-2012.zip'))
        context['cpt_pa_out_file'] = self.get_complete_remotefile(cpt_path.format(cpt_subpath, 'PA_SPESE_1996-2012.zip'))
        context['cpt_spa_in_file'] = self.get_complete_remotefile(cpt_path.format(cpt_subpath, 'SPA_ENTRATE_1996-2012.zip'))
        context['cpt_spa_out_file'] = self.get_complete_remotefile(cpt_path.format(cpt_subpath, 'SPA_SPESE_1996-2012.zip'))
        context['cpt_metadata_file'] = self.get_complete_remotefile(cpt_path.format('METADATA', 'CPT_Metadati_perCSV_def.xls'))

        context['raccordo_temi_sintetici_file'] = self.get_complete_localfile('raccordo_temi_sintetici.xls')

        return context

    @staticmethod
    def get_complete_remotefile(file_name):
        try:
            f = urllib2.urlopen(file_name)
            file_size = f.headers['Content-Length']
        except urllib2.HTTPError:
            file_size = None

        return {
            'file_name': file_name,
            'file_size': file_size
        }

    @staticmethod
    def get_latest_localfile(file_name, as_urlpath=False):
        opendata_path = os.path.join(settings.MEDIA_ROOT, 'open_data')

        def add_wildcard(file_name):
            wildcard = '201?????'
            file_name, file_ext = os.path.splitext(file_name)
            return file_name + '_' + wildcard + file_ext

        file_path = os.path.join(opendata_path, *file_name.split('/'))
        if not os.path.isfile(file_path):
            files = sorted(glob.glob(add_wildcard(file_path)))
            if files:
                file_path = files[-1]
            else:
                raise IOError

        if as_urlpath:
            file_path = '/'.join(os.path.split(os.path.relpath(file_path, opendata_path)))

        return file_path

    @classmethod
    def get_complete_localfile(cls, file_name):
        try:
            file_path = cls.get_latest_localfile(file_name)
            file_size = os.stat(file_path).st_size
        except:
            file_size = None

        return {
            'file_name': reverse('opendata_clean', kwargs={'path': file_name}),
            'file_size': file_size
        }

    @classmethod
    def get_regional_files(cls, section_code, prefix):
        regions = SortedDict([
            ('VDA', "Valle d'Aosta"),
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
            ('NAZ', 'Italia'),
            ('EST', 'Estero'),
            # ('MULTI', 'Multi-regionali'),
        ])

        files = []
        for region_code, region_name in regions.items():
            file = cls.get_complete_localfile('{0}/{1}_{2}_{3}.zip'.format('regione', section_code, prefix, region_code))
            file['region_name'] = region_name
            files.append(file)

        return files

    # @classmethod
    # def get_theme_files(cls, section_code, section_name):
    #     themes = SortedDict([
    #         ('AGENDA_DIGITALE', 'Agenda digitale'),
    #         ('AMBIENTE', 'Ambiente'),
    #         ('CULTURA_TURISMO', 'Cultura e turismo'),
    #         ('COMPETITIVITA_IMPRESE', u'Competitività imprese'),
    #         ('ENERGIA', 'Energia'),
    #         ('INCLUSIONE_SOCIALE', 'Inclusione sociale'),
    #         ('ISTRUZIONE', 'Istruzione'),
    #         ('OCCUPAZIONE', 'Occupazione'),
    #         ('RAFFORZAMENTO_PA', 'Rafforzamento PA'),
    #         ('RICERCA_INNOVAZIONE', 'Ricerca e innovazione'),
    #         ('CITTA_RURALE', 'Città e aree rurali'),
    #         ('INFANZIA_ANZIANI', 'Infanzia e anziani'),
    #         ('TRASPORTI', 'Trasporti'),
    #     ])
    #
    #     files = []
    #     for theme_code, theme_name in themes.items():
    #         file = cls.get_complete_localfile('{0}/{1}_{2}.zip'.format(section_name, section_code, theme_code))
    #         file['theme_name'] = theme_name
    #         files.append(file)
    #
    #     return files


class OpendataRedirectView(RedirectView):
    def get_redirect_url(self, **kwargs):
        try:
            return u'/media/open_data/{0}'.format(OpendataView.get_latest_localfile(kwargs['path'], as_urlpath=True))
        except:
            raise Http404('File not found.')


class PillolaListView(ListView, TagFilterMixin, DateFilterMixin):
    model = Pillola

    def get_queryset(self):
        queryset = super(PillolaListView, self).get_queryset()
        queryset = self._apply_date_filter(queryset)
        queryset = self._apply_tag_filter(queryset)
        queryset = queryset.order_by('-published_at', '-id')

        return queryset

    def get_context_data(self, **kwargs):
        context = super(PillolaListView, self).get_context_data(**kwargs)
        context['date_choices'] = self._get_date_choices()
        context['tag_choices'] = self._get_tag_choices()

        return context


class PillolaDetailView(DetailView):
    model = Pillola


class PillolaRedirectView(RedirectView):
    def get_redirect_url(self, **kwargs):
        return u'/media/pillole/{0}'.format(kwargs['path'])


class PressReviewListView(ListView):
    model = PressReview


class FAQListView(ListView):
    model = FAQ
    lang = None

    def __init__(self, **kwargs):
        super(FAQListView, self).__init__(**kwargs)
        self.model.lang = self.lang

    def get_context_data(self, **kwargs):
        context = super(FAQListView, self).get_context_data(**kwargs)
        context['title'] = 'Frequently Asked Questions' if self.lang == 'en' else 'Domande frequenti'

        return context


class DocumentsRedirectView(RedirectView):
    def get_redirect_url(self, **kwargs):
        return u'/media/uploads/documenti/{0}'.format(kwargs['path'])
