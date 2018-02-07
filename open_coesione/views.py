# -*- coding: utf-8 -*-
import glob
import os
import urllib2
from collections import OrderedDict
from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.http import HttpResponseRedirect, BadHeaderError, HttpResponse, Http404
from django.views.generic.base import TemplateView, RedirectView, TemplateResponseMixin
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from forms import ContactForm
from mixins import DateFilterMixin
from models import PressReview, Pillola, FAQ, Opportunita
from progetti.models import Progetto, Tema, ClassificazioneAzione, DeliberaCIPE
from soggetti.models import Soggetto
from tagging.views import TagFilterMixin
from territori.models import Territorio


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
        if getattr(self, 'cache_enabled', True):
            key = 'context' + getattr(self, 'cache_key', self.request.get_full_path())
            context = cache.get(key)
            if context is None:
                context = get_context_data(self, **kwargs)
                serializable_context = context.copy()
                serializable_context.pop('view', None)
                cache.set(key, serializable_context)
            return context
        else:
            return get_context_data(self, **kwargs)
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
    TEMATIZZAZIONI = settings.TEMATIZZAZIONI

    @property
    def cache_key(self):
        return self.request.path

    @staticmethod
    def add_totali(objects, totali, key='pk'):
        totali_by_key = {x.pop('id'): x for x in totali}
        objects_with_totali = []
        for object in objects:
            object.totali = totali_by_key.get(getattr(object, key), {})
            objects_with_totali.append(object)
        return objects_with_totali

    def get_progetti_queryset(self):
        return Progetto.objects

    def get_aggregate_data(self):
        progetti = self.get_progetti_queryset()

        aggregate_data = progetti.totali()

        aggregate_data['percentuale_costi_pagamenti'] = '{:.0%}'.format(aggregate_data['totale_pagamenti'] / aggregate_data['totale_costi'] if aggregate_data['totale_costi'] > 0.0 else 0.0)

        if not isinstance(getattr(self, 'object', None), Tema):
            aggregate_data['temi_principali'] = self.add_totali(Tema.objects.principali(), progetti.totali_group_by('tema__tema_superiore'))

        if not isinstance(getattr(self, 'object', None), ClassificazioneAzione):
            aggregate_data['nature_principali'] = self.add_totali(ClassificazioneAzione.objects.nature(), progetti.totali_group_by('classificazione_azione__classificazione_superiore'))

        aggregate_data['top_progetti_per_costo'] = progetti.no_privacy().filter(fin_totale_pubblico__isnull=False).order_by('-fin_totale_pubblico', '-data_fine_effettiva')[:5]

        aggregate_data['map_legend_colors'] = settings.MAP_COLORS

        if self.request.GET.get('pro_capite'):
            aggregate_data['mappa_pro_capite'] = True

        return aggregate_data

    def get_tematizzazione(self):
        tematizzazione = self.request.GET.get('tematizzazione', self.TEMATIZZAZIONI[0])

        if tematizzazione in self.TEMATIZZAZIONI:
            return tematizzazione
        else:
            raise Http404

    def tematizza_context_data(self, context):
        context['tematizzazione'] = self.get_tematizzazione()

        for obj in context.get('temi_principali', []) + context.get('nature_principali', []) + context.get('territori', []):
            obj.totale = obj.totali.get(context['tematizzazione'], 0)

    def top_comuni_pro_capite(self, filters, qnt=5):
        def pro_capite_order(territorio):
            territorio['totale_pro_capite'] = territorio['totale'] / territorio['popolazione_totale'] if territorio['popolazione_totale'] else 0.0
            return territorio['totale_pro_capite']

        if isinstance(filters, dict):
            args = []
            kwargs = filters
        else:
            args = filters
            kwargs = {}

        # add filters on active and published projects, to avoid computation errors
        kwargs.update({'progetto__active_flag': True, 'progetto__visualizzazione_flag': '0'})

        territori = Territorio.objects.comuni().filter(*args, **kwargs).values('pk', 'popolazione_totale').annotate(totale=Sum('progetto__fin_totale_pubblico')).filter(totale__isnull=False).order_by()

        territori = sorted(territori, key=pro_capite_order, reverse=True)[:qnt]

        territori_by_pk = Territorio.objects.defer('geom').in_bulk(x['pk'] for x in territori)

        top_comuni_pro_capite = []
        for t in territori:
            territorio = territori_by_pk[t['pk']]
            territorio.totale = t['totale']
            territorio.totale_pro_capite = t['totale_pro_capite']
            top_comuni_pro_capite.append(territorio)

        return top_comuni_pro_capite


class HomeView(AggregatoMixin, TemplateView):
    @cached_context
    def get_cached_context_data(self):
        context = self.get_aggregate_data()

        context['top_progetti'] = context.pop('top_progetti_per_costo')[:3]

        context['numero_soggetti'] = Soggetto.objects.count()

        return context

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        context.update(self.get_cached_context_data())

        self.tematizza_context_data(context)

        context['ultimi_progetti_conclusi'] = self.get_progetti_queryset().no_privacy().conclusi()[:3]

        context['pillola'] = Pillola.objects.order_by('-published_at', '-id')[:1][0]

        context['opportunita'] = self.get_opportunita_info()

        return context

    @staticmethod
    def get_opportunita_info():
        import csv
        import datetime
        import decimal

        today = datetime.date.today().strftime('%Y%m%d')
        lastday = (datetime.date.today() + datetime.timedelta(days=7)).strftime('%Y%m%d')

        opportunita_file = Opportunita.get_solo().file

        opportunita = list(csv.DictReader(open(opportunita_file.path, 'rb'), delimiter=';'))
        opportunita_incorso = filter(lambda x: not bool(x['DATA_SCADENZA'] and (x['DATA_SCADENZA'] < today)), opportunita)
        opportunita_inscadenza = filter(lambda x: bool(x['DATA_SCADENZA'] and (x['DATA_SCADENZA'] <= lastday)), opportunita_incorso)

        opportunita_info = {
            'data_modifica': opportunita_file.storage.modified_time(opportunita_file.name),
        }
        for key, lst in [('incorso', opportunita_incorso), ('inscadenza', opportunita_inscadenza)]:
            opportunita_info[key] = {
                'totale': len(lst),
                'importo': sum(decimal.Decimal(x['IMPORTO'].replace('.', '').replace(',', '.')) for x in lst if x['IMPORTO']),
            }

        return opportunita_info


class RisorsaView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(RisorsaView, self).get_context_data(**kwargs)

        context['risorsa'] = True

        return context


class FondiView(RisorsaView):
    def get_context_data(self, **kwargs):
        context = super(FondiView, self).get_context_data(**kwargs)

        context['delibere'] = DeliberaCIPE.objects.all()
        for delibera in context['delibere']:
            filename = delibera.url.split('?f=')[1]
            delibera.url = 'http://ricerca-delibere.programmazioneeconomica.gov.it/media/docs/20{}/{}'.format(filename[1:3], filename)

        context['totale_fondi_assegnati'] = DeliberaCIPE.objects.aggregate(s=Sum('fondi_assegnati'))['s']
        context['tabella_risorse_1420'] = OpendataView.get_complete_localfile('risorse_coesione_2014_2020.xls')

        return context


class SpesaCertificataView(RisorsaView):
    def get_context_data(self, **kwargs):
        context = super(SpesaCertificataView, self).get_context_data(**kwargs)

        context['spesa_dotazione_file'] = OpendataView.get_complete_localfile('Dotazioni_Certificazioni.xls')
        context['spesa_target_file'] = OpendataView.get_complete_localfile('Target_Risultati.xls')

        return context


class SpesaCertificataGraficiView(RisorsaView):
    @cached_context
    def get_context_data(self, **kwargs):
        import csv
        from collections import OrderedDict
        from csvkit import convert
        from datetime import datetime

        def format_number(value):
            if value:
                return round(float(value.strip()), 2)
            else:
                return ''

        def format_name(value):
            name_map = {
                u'PON GOVERNANCE E AZIONI DI SISTEMA': 'Pon GAS',
                u'PON COMPETENZE PER LO SVILUPPO': 'Pon Istruzione',
                u'POIN ATTRATTORI CULTURALI, NATURALI E TURISMO': 'Poin Attrattori',
                u'POIN ENERGIE RINNOVABILI E RISPARMIO ENERGETICO': 'Poin Energie',
                u'PON GOVERNANCE E ASSISTENZA TECNICA': 'Pon GAT',
                u"PON ISTRUZIONE - AMBIENTI PER L'APPRENDIMENTO": 'Pon Istruzione',
                u'PON RETI E MOBILITÀ': 'Pon Reti',
                u'PON RICERCA E COMPETITIVITÀ': 'Pon Ricerca',
                u'PON AZIONI DI SISTEMA': 'Pon AS',
            }
            value = ' '.join([x.decode('utf8') for x in value.split() if x not in ['CRO', 'CONV', 'FSE', 'FESR']])
            if value in name_map:
                value = name_map[value]
            else:
                value = value.title()
                value = value.replace(' Pa ', ' PA ')
                value = value.replace("D'", "d'")
            return value

        dates = ['{}{:02d}31'.format(y, m) for y in range(2010, 2016) for m in [5, 10, 12]]
        dates += ['20160731', '20161231', '20170331']

        csv2data_key_map = (
            ('TARGET {}', 'target'),
            ('TARGET NAZIONALE {}', 'target'),
            ('TARGET UE {}', 'target'),
            ('STIMA TARGET {}', 'target'),
            ('quota spesa certificata {}', 'risultato_spesa'),
            ('quota pagamenti ammessi {}', 'risultato_pagamenti'),
        )

        reader = csv.DictReader(convert.xls2csv(open(OpendataView.get_latest_localfile('Target_Certificato_Pagamenti.xls'), 'rb'), sheet='Target spesa cert ammessi va').splitlines())

        data = {}
        for row in reader:
            if row['OC_CODICE_PROGRAMMA']:
                program_name = format_name(row['OC_DESCRIZIONE_PROGRAMMA'])
                group_key = '{}_{}'.format(row['QSN_AREA_OBIETTIVO_UE'], row['QSN_FONDO_COMUNITARIO ']).lower()

                if not group_key in data:
                    data[group_key] = []

                dates_data = []
                for date in dates:
                    date_data = {}

                    for csv_key, data_key in csv2data_key_map:
                        csv_key = csv_key.format(date)
                        if csv_key in row:
                            date_data[data_key] = row[csv_key]

                    if date_data:
                        dates_data.append((datetime.strptime(date, '%Y%m%d').strftime('%d/%m/%Y'), date_data))

                for type_name, type_key in [('Obiettivo di spesa certificata', 'target'), ('Spesa certificata su dotazione', 'risultato_spesa'), ('Pagamenti su dotazione', 'risultato_pagamenti')]:
                    data[group_key].append(OrderedDict([('Programma operativo', program_name), ('Tipo dato', type_name)] + [(date, format_number(date_data.get(type_key))) for date, date_data in dates_data]))

        context = super(SpesaCertificataGraficiView, self).get_context_data(**kwargs)

        context['grouped_data'] = []
        for group_key in ['cro_fesr', 'cro_fse', 'conv_fesr', 'conv_fse']:
            type, fund = group_key.upper().split('_')
            context['grouped_data'].append(({'CRO': u'Competitività', 'CONV': u'Convergenza'}[type], fund, data[group_key]))

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

            return HttpResponseRedirect('{}?completed=true'.format(reverse('oc-contatti')))  # Redirect after POST

        return self.get(request, *args, **kwargs)


class DatiISTATView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(DatiISTATView, self).get_context_data(**kwargs)

        istat_path = 'http://www.istat.it/storage/politiche-sviluppo/{}'
        context['istat_metadata_file'] = OpendataView.get_complete_remotefile(istat_path.format('Metainformazione.xls'))

        return context


class OpendataView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(OpendataView, self).get_context_data(**kwargs)

        context['oc_sections'] = OrderedDict([
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

        context['fs_sections'] = OrderedDict([
            ('prog', {
                'name': 'progetti',
                'complete_file': self.get_complete_localfile('progetti_FS0713.zip'),
                'regional_files': self.get_regional_files('prog', 'FS0713'),
            }),
            ('sog', {
                'name': 'soggetti',
                'complete_file': self.get_complete_localfile('soggetti_FS0713.zip'),
                'regional_files': self.get_regional_files('sog', 'FS0713'),
            }),
            ('loc', {
                'name': 'localizzazioni',
                'complete_file': self.get_complete_localfile('localizzazioni_FS0713.zip'),
                'regional_files': self.get_regional_files('loc', 'FS0713'),
            }),
            ('pag', {
                'name': 'pagamenti',
                'complete_file': self.get_complete_localfile('pagamenti_FS0713.zip'),
                'regional_files': self.get_regional_files('pag', 'FS0713'),
            }),
        ])

        context['fsc_sections'] = OrderedDict([
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

        # context['fsc2_sections'] = OrderedDict([
        #     ('prog', {
        #         'name': 'progetti',
        #         'complete_file': self.get_complete_localfile('progetti_FSC0006.zip'),
        #     }),
        #     ('sog', {
        #         'name': 'soggetti',
        #         'complete_file': self.get_complete_localfile('soggetti_FSC0006.zip'),
        #     }),
        #     ('loc', {
        #         'name': 'localizzazioni',
        #         'complete_file': self.get_complete_localfile('localizzazioni_FSC0006.zip'),
        #     }),
        #     ('pag', {
        #         'name': 'pagamenti',
        #         'complete_file': self.get_complete_localfile('pagamenti_FSC0006.zip'),
        #     }),
        # ])

        context['pac_sections'] = OrderedDict([
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

        context['cipe_sections'] = OrderedDict([
            ('prog', {
                'name': 'progetti',
                'complete_file': self.get_complete_localfile('progetti_assegnazioni_CIPE.zip'),
            }),
            ('sog', {
                'name': 'soggetti',
                'complete_file': self.get_complete_localfile('soggetti_assegnazioni_CIPE.zip'),
            }),
            ('loc', {
                'name': 'localizzazioni',
                'complete_file': self.get_complete_localfile('localizzazioni_assegnazioni_CIPE.zip'),
            }),
        ])

        context['oc_metadata_file'] = self.get_complete_localfile('metadati_OC_2007_2013.xls')
        context['oc_utility_metadata_file'] = self.get_complete_localfile('Utility Metadati OC.xls')

        context['metadata_file'] = context['oc_metadata_file']
        context['utility_metadata_file'] = self.get_complete_localfile('Utility Metadati Attuazione.xls')

        context['cipe_metadata_file'] = self.get_complete_localfile('metadati_assegnazioni_cipe.xls')
        # context['cipe_utility_metadata_file'] = self.get_complete_localfile('Utility Metadati Assegnazioni CIPE.xls')

        context['cipe_corrispondenze_file'] = self.get_complete_localfile('corrispondenze_assegnazioni_progetti.csv')
        context['cipe_corrispondenze_metadata_file'] = self.get_complete_localfile('metadati_corrispondenze_assegnazioni_attuazione.xls')

        context['risorse0713_file'] = self.get_complete_localfile('Dotazioni_PO_2007-2013.xls')
        context['risorse1420_file'] = self.get_complete_localfile('Dotazioni_PO_SIE_2014-2020.xls')
        context['decisioni1420_file'] = self.get_complete_localfile('Decisioni_PO_SIE_2014-2020.xls')
        context['dotazionifsc1420_file'] = self.get_complete_localfile('Dotazioni_FSC_2014-2020.xls')
        context['decisionifsc1420_file'] = self.get_complete_localfile('Decisioni_FSC_2014-2020.xls')
        context['dotazionipoc1420_file'] = self.get_complete_localfile('Dotazioni_POC_2014-2020.xls')
        context['decisionipoc1420_file'] = self.get_complete_localfile('Decisioni_POC_2014-2020.xls')

        context['spesa_dotazione_file'] = self.get_complete_localfile('Dotazioni_Certificazioni.xls')
        context['spesa_target_file'] = self.get_complete_localfile('Target_Risultati.xls')

        istat_path = 'http://www.istat.it/storage/politiche-sviluppo/{}'
        context['istat_data_file'] = self.get_complete_remotefile(istat_path.format('Archivio_unico_indicatori_regionali.zip'))
        context['istat_metadata_file'] = self.get_complete_remotefile(istat_path.format('Metainformazione.xls'))

        cpt_path = 'http://www.agenziacoesione.gov.it/it/cpt/02_dati/01catalogo_open_cpt/datasets/{}'
        context['cpt_pa_in_file'] = self.get_complete_remotefile(cpt_path.format('PA_ENTRATE_2000-2015.zip'))
        context['cpt_pa_out_file'] = self.get_complete_remotefile(cpt_path.format('PA_SPESE_2000-2015.zip'))
        context['cpt_spa_in_file'] = self.get_complete_remotefile(cpt_path.format('SPA_ENTRATE_2000-2015.zip'))
        context['cpt_spa_out_file'] = self.get_complete_remotefile(cpt_path.format('SPA_SPESE_2000-2015.zip'))
        context['cpt_metadata_file'] = self.get_complete_remotefile(cpt_path.format('Metadati_flussi.xls'))

        opportunita = Opportunita.get_solo()
        context['opportunita_data_file'] = self.get_complete_objectfile(opportunita.file)
        context['opportunita_metadata_file'] = self.get_complete_objectfile(opportunita.file2)

        context['indagine_data_file'] = self.get_complete_localfile('indagine_data.zip')
        context['indagine_metadata_file'] = self.get_complete_localfile('metadati_indagine_beneficiari_2007_2013.xls')

        context['raccordo_temi_sintetici_file'] = self.get_complete_localfile('raccordo_temi_sintetici.xls')

        context['approfondimenti_1_1_file'] = self.get_complete_localfile('approfondimenti/progetti_focus_scuole.zip')
        context['approfondimenti_1_2_file'] = self.get_complete_localfile('approfondimenti/progetti_focus_scuole_20160630.zip')
        context['approfondimenti_1_metadata_file'] = self.get_complete_localfile('approfondimenti/metadati_focus_scuole.xls')

        context['approfondimenti_2_1_file'] = self.get_complete_localfile('approfondimenti/progetti_focus_beni_confiscati.csv')
        context['approfondimenti_2_2_file'] = self.get_complete_localfile('approfondimenti/progetti_focus_beni_confiscati_20151231.csv')
        context['approfondimenti_2_3_file'] = self.get_complete_localfile('approfondimenti/progetti_focus_beni_confiscati_20141231.csv')
        context['approfondimenti_2_metadata_file'] = self.get_complete_localfile('approfondimenti/metadati_focus_beni_confiscati.xls')

        context['approfondimenti_3_1_file'] = self.get_complete_localfile('approfondimenti/progetti_focus_turismo.zip')
        context['approfondimenti_3_2_file'] = self.get_complete_localfile('approfondimenti/progetti_focus_turismo_20170630.zip')
        context['approfondimenti_3_metadata_file'] = self.get_complete_localfile('approfondimenti/metadati_focus_turismo.xls')

        return context

    @classmethod
    def get_complete_localfile(cls, file_name):
        try:
            file_path = cls.get_latest_localfile(file_name)
            file_size = os.stat(file_path).st_size
        except:
            file_path = file_size = None

        file_date = False
        if file_path:
            import datetime
            import re
            match = re.search('\_((201\d)(0[1-9]|1[012])(0[1-9]|[12][0-9]|3[01]))\.', file_path)
            if match:
                file_date = datetime.datetime.strptime(match.group(1), '%Y%m%d')

        return {
            'file_name': reverse('opendata_clean', kwargs={'path': file_name}),
            'file_size': file_size,
            'file_date': file_date,
            'file_ext': cls.get_file_ext(file_name),
        }

    @classmethod
    def get_complete_remotefile(cls, file_name):
        import datetime
        import email.utils as eut

        try:
            f = urllib2.urlopen(file_name, timeout=2)
            file_size = f.headers['Content-Length']
            file_date = datetime.datetime(*eut.parsedate(f.headers['Last-Modified'])[:6])
        except Exception:
            file_size = None
            file_date = None

        return {
            'file_name': file_name,
            'file_size': file_size,
            'file_date': file_date,
            'file_ext': cls.get_file_ext(file_name),
        }

    @classmethod
    def get_complete_objectfile(cls, file_object):
        return {
            'file_name': file_object.url,
            'file_size': file_object.size,
            'file_date': file_object.storage.modified_time(file_object.name),
            'file_ext': cls.get_file_ext(file_object.name),
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

    @staticmethod
    def get_file_ext(file_name):
        _, file_ext = os.path.splitext(file_name)
        file_ext = file_ext[1:]
        if file_ext == 'zip':
            file_ext += '/csv'

        return file_ext

    @classmethod
    def get_regional_files(cls, section_code, prefix):
        regions = OrderedDict([
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
        ])

        files = []
        for region_code, region_name in regions.items():
            file = cls.get_complete_localfile('{}/{}_{}_{}.zip'.format('regione', section_code, prefix, region_code))
            file['region_name'] = region_name
            files.append(file)

        return files


class OpendataRedirectView(RedirectView):
    def get_redirect_url(self, **kwargs):
        try:
            return u'/media/open_data/{}'.format(OpendataView.get_latest_localfile(kwargs['path'], as_urlpath=True))
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


class OpportunitaDetailView(DetailView):
    model = Opportunita

    def get_object(self, queryset=None):
        return self.model.get_solo()

    def get_context_data(self, **kwargs):
        import csv
        import datetime
        import decimal

        self.object.file.modified_time = self.object.file.storage.modified_time(self.object.file.name)

        context = super(OpportunitaDetailView, self).get_context_data(**kwargs)

        today = datetime.date.today().strftime('%Y%m%d')

        reader = csv.DictReader(open(self.object.file.path, 'rb'), delimiter=';')

        context['opportunita'] = OrderedDict([(False, []), (True, [])])

        for row in sorted(reader, key=lambda x: (x['DATA_SCADENZA'] or '@', x['DATA_PUBBLICAZIONE'])):
            is_expired = bool(row['DATA_SCADENZA'] and (row['DATA_SCADENZA'] < today))

            for c in ('DATA_SCADENZA', 'DATA_PUBBLICAZIONE'):
                row[c] = datetime.datetime.strptime(row[c], '%Y%m%d') if row[c] else ''
            row['IMPORTO'] = decimal.Decimal(row['IMPORTO'].replace('.', '').replace(',', '.')) if row['IMPORTO'] else ''

            context['opportunita'][is_expired].append(row)

        return context


class DocumentsRedirectView(RedirectView):
    def get_redirect_url(self, **kwargs):
        return u'/media/uploads/documenti/{}'.format(kwargs['path'])


class IndicatoriAccessoView(TemplateView):
    lang = None

    def __init__(self, **kwargs):
        super(IndicatoriAccessoView, self).__init__(**kwargs)
        self.lang = self.lang if self.lang == 'en' else 'it'

    def get_context_data(self, **kwargs):
        import csv
        import dateutil.parser as parser

        context = super(IndicatoriAccessoView, self).get_context_data(**kwargs)
        filenames = {
            'en': ['access_indicators_1.csv', 'access_indicators_2.csv', 'access_indicators_3.csv'],
            'it': ['indicatori_accesso_1.csv', 'indicatori_accesso_2.csv', 'indicatori_accesso_3.csv'],
        }

        indicators = []
        for filename in filenames[self.lang]:
            reader = csv.reader(open(os.path.join(settings.STATIC_ROOT, 'csv', filename), 'rb'), delimiter=';')

            colnames_dict = {
                'en': reader.next(),
                'it': reader.next(),
            }

            colnames = colnames_dict[self.lang][1:]

            data = OrderedDict((k, []) for k in colnames)
            for row in reader:
                date = parser.parse(row.pop(0)).strftime('%d/%m/%Y')
                for idx, colname in enumerate(colnames):
                    try:
                        value = float(row[idx].replace('.', '').replace(',', '.'))
                    except ValueError:
                        pass
                    else:
                        data[colname].append({'date': date, 'value': value})

            indicators.append({'filename': 'csv/{}'.format(filename), 'data': data})

        context['indicators'] = indicators
        context['lang'] = self.lang

        return context
