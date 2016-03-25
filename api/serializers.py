# -*- coding: utf-8 -*-
from rest_framework import serializers, pagination
from rest_framework.reverse import reverse
from progetti.models import Progetto, Tema, ClassificazioneAzione, ProgrammaAsseObiettivo, Ruolo, PagamentoProgetto,\
    ClassificazioneQSN, ClassificazioneOggetto
from soggetti.models import Soggetto
from territori.models import Territorio

__author__ = 'guglielmo'


class FiltersField(serializers.Field):
    """
    Field that returns urls for progetti or soggetti with a given tema or natura.
    """
    filter_name = ''

    def __init__(self, filter_name):
        self.filter_name = filter_name
        super(FiltersField, self).__init__(self)

    def field_to_native(self, obj, field_name):
        request = self.context.get('request')
        format = self.context.get('format')

        progetti_filter_url = '{}?{}={}'.format(reverse('api-progetto-list', request=request, format=format), self.filter_name, obj.slug)
        soggetti_filter_url = '{}?{}={}'.format(reverse('api-soggetto-list', request=request, format=format), self.filter_name, obj.slug)

        ret = {
            'progetti': progetti_filter_url,
            'soggetti': soggetti_filter_url,
        }

        return ret


class FacetsField(serializers.Field):
    """
    Field that returns info about the facets.
    Can be used both for progetti and soggetti results lists.
    """
    def field_to_native(self, obj, field_name):
        if not 'view' in self.context:
            return {}

        facet_counts = self.context['view'].get_queryset().facet_counts()

        temi_inv_dict = {t['codice']: t['slug'] for t in Tema.objects.principali().values('codice', 'slug').order_by('codice')}

        nature_inv_dict = {n['codice']: n['slug'] for n in ClassificazioneAzione.objects.nature().values('codice', 'slug').order_by('codice')}
        nature_inv_dict.update({'ND': 'non-definito'})

        ruoli_inv_dict = Ruolo.inv_ruoli_dict()

        ret = {}

        if 'natura' in facet_counts['fields']:
            ret['natura'] = ['{} ({})'.format(nature_inv_dict[i[0]], i[1]) for i in facet_counts['fields']['natura'] if i[1]]

        if 'tema' in facet_counts['fields']:
            ret['tema'] = ['{} ({})'.format(temi_inv_dict[i[0]], i[1]) for i in facet_counts['fields']['tema'] if i[1]]

        if 'ruolo' in facet_counts['fields']:
            ret['ruolo'] = ['{} ({})'.format(ruoli_inv_dict[i[0]], i[1]) for i in facet_counts['fields']['ruolo'] if i[1]]

        return ret


class SoggettoSlugField(serializers.RelatedField):
    def to_native(self, value):
        return reverse('api-soggetto-detail', kwargs={'slug': value}, request=self.context.get('request'), format=self.context.get('format'))


class TemaModelSerializer(serializers.ModelSerializer):
    filters = FiltersField('tema')

    class Meta:
        model = Tema
        exclude = ('descrizione_estesa', 'tema_superiore', 'tipo_tema')
        depth = 1


class NaturaModelSerializer(serializers.ModelSerializer):
    filters = FiltersField('natura')

    class Meta:
        model = ClassificazioneAzione
        exclude = ('descrizione_estesa', 'priorita', 'tipo_classificazione', 'classificazione_superiore')
        depth = 1


class TerritorioModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Territorio
        fields = ('denominazione', 'denominazione_ted', 'territorio', 'slug', 'cod_reg', 'cod_prov', 'cod_com')


class SoggettoModelSerializer(serializers.ModelSerializer):
    territorio = TerritorioModelSerializer()

    class Meta:
        model = Soggetto
        exclude = ('id', 'created', 'modified')
        depth = 1


class ProgrammaModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgrammaAsseObiettivo


class ClassificazioneQSNModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassificazioneQSN


class ClassificazioneOggettoModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassificazioneOggetto


class PagamentoProgettoSerializer(serializers.ModelSerializer):
    data = serializers.DateField()
    ammontare = serializers.DecimalField()

    class Meta:
        model = PagamentoProgetto
        fields = ('data', 'ammontare')


class RuoloProgettoSerializer(serializers.ModelSerializer):
    soggetto = serializers.HyperlinkedRelatedField(view_name='api-soggetto-detail')

    def to_native(self, obj):
        ret = super(RuoloProgettoSerializer, self).to_native(obj)
        ret.update({
            'codice': ret['ruolo'],
            'ruolo': obj.get_ruolo_display(),
            'slug': obj.soggetto.slug,
            'soggetto_label': obj.soggetto.denominazione
        })
        return ret

    class Meta:
        model = Ruolo
        fields = ('ruolo', 'soggetto')


class ProgettoModelSerializer(serializers.ModelSerializer):
    territorio_set = TerritorioModelSerializer(many=True)
    pagamenti = PagamentoProgettoSerializer(many=True)
    ruolo_set = RuoloProgettoSerializer(many=True)

    class Meta:
        model = Progetto
        exclude = ('territorio', 'created', 'modified', )
        depth = 1


class ProgettoSearchResultSerializer(serializers.Serializer):
    slug = serializers.CharField()
    url = serializers.HyperlinkedIdentityField(view_name='api-progetto-detail')
    codice_locale = serializers.CharField(max_length=200)
    cup = serializers.CharField(max_length=100)
    titolo_progetto = serializers.CharField(required=False)
    classificazione_cup = serializers.CharField(required=False)
    fin_totale_pubblico = serializers.FloatField()
    pagamento = serializers.FloatField()
    percentuale_pagamenti = serializers.FloatField()
    soggetto = SoggettoSlugField(many=True)
    territorio = serializers.RelatedField(many=True)
    tema_slug = serializers.CharField()
    natura_slug = serializers.CharField()
    data_inizio_effettiva = serializers.DateField()
    data_fine_effettiva = serializers.DateField()

    def to_native(self, obj):
        obj2 = obj.object

        obj2.classificazione_cup = obj2.classificazione_oggetto.codice if obj2.classificazione_oggetto else 'ND'
        obj2.soggetto = set(o.slug for o in obj2.soggetto_set.all())
        obj2.territorio = set(o.slug for o in obj2.territorio_set.all())
        obj2.tema_slug = obj2.tema.tema_superiore.slug
        obj2.natura_slug = obj2.classificazione_azione.classificazione_superiore.slug if obj2.classificazione_azione else 'nd'

        return super(ProgettoSearchResultSerializer, self).to_native(obj2)

    def get_field_key(self, field_name):
        fields_map = {
            'soggetto': 'soggetti',
            'territorio': 'territori',
            'tema_slug': 'tema',
            'natura_slug': 'natura',
        }
        return fields_map.get(field_name, field_name)


class PaginatedProgettoSerializer(pagination.PaginationSerializer):
    page_size = serializers.Field(source='paginator.per_page')
    current_page = serializers.Field(source='number')
    last_page = serializers.Field(source='paginator.num_pages')
    facet_counts = FacetsField()

    class Meta:
        object_serializer_class = ProgettoSearchResultSerializer


class SoggettoSearchResultSerializer(serializers.Serializer):
    url = serializers.HyperlinkedIdentityField(view_name='api-soggetto-detail')
    denominazione = serializers.CharField(required=False)
    tema = serializers.RelatedField(many=True)
    ruolo = serializers.RelatedField(many=True)
    costo = serializers.FloatField()
    num_progetti = serializers.IntegerField()

    def to_native(self, obj):
        obj2 = obj.object

        obj2.tema = Tema.objects.filter(tema_set__progetto_set__soggetto_set=obj2).values_list('slug', flat=True).distinct()
        obj2.ruolo = [Ruolo.inv_ruoli_dict()[r] for r in Ruolo.objects.filter(soggetto=obj2).values_list('ruolo', flat=True).distinct()]
        obj2.costo = obj.costo
        obj2.num_progetti = obj.n_progetti

        return super(SoggettoSearchResultSerializer, self).to_native(obj2)

    def get_field_key(self, field_name):
        fields_map = {
            'num_progetti': 'n_progetti',
        }
        return fields_map.get(field_name, field_name)


class PaginatedSoggettoSerializer(pagination.PaginationSerializer):
    page_size = serializers.Field(source='paginator.per_page')
    current_page = serializers.Field(source='number')
    last_page = serializers.Field(source='paginator.num_pages')
    facet_counts = FacetsField()

    class Meta:
        object_serializer_class = SoggettoSearchResultSerializer
