from rest_framework.reverse import reverse
from soggetti.models import Soggetto
from territori.models import Territorio

__author__ = 'guglielmo'
from rest_framework import serializers, pagination
from progetti.models import Progetto, Tema, ClassificazioneAzione, ProgrammaAsseObiettivo


class FacetsField(serializers.Field):
    """
    Field that returns info about the facets.

    Can be used both for progetti and soggetti results lists.
    """
    def field_to_native(self, obj, field_name):
        if 'view' in self.context:
            facet_counts = self.context['view'].get_queryset().facet_counts()
        else:
            return {}

        ret = {}
        nature = []
        temi = []
        ruoli = []

        if 'natura' in facet_counts['fields']:
            ret['natura'] = ["{0} ({1})".format(i[0], i[1]) for i in facet_counts['fields']['natura'] if i[1]]

        if 'tema' in facet_counts['fields']:
            ret['tema'] = ["{0} ({1})".format(i[0], i[1]) for i in facet_counts['fields']['tema'] if i[1]]

        if 'ruolo' in facet_counts['fields']:
            ret['ruolo'] = ["{0} ({1})".format(i[0], i[1]) for i in facet_counts['fields']['ruolo'] if i[1]]

        return ret



class SoggettoSlugField(serializers.RelatedField):
    def to_native(self, value):
        return reverse('api-soggetto-detail', kwargs={'slug': value}, request=self.context.get('request'), format=self.context.get('format'))


class ProgettoSearchResultSerializer(serializers.Serializer):
    """
    """

    slug = serializers.HyperlinkedIdentityField(view_name='api-progetto-detail')
    clp = serializers.CharField(max_length=200)
    cup = serializers.CharField(max_length=100)
    titolo = serializers.CharField(required=False)
    fin_totale_pubblico = serializers.FloatField()
    pagamento = serializers.FloatField()
    soggetto = SoggettoSlugField(many=True)
    tema = serializers.RelatedField()
    natura = serializers.RelatedField()

    def get_field_key(self, field_name):
        """
        Transform inner solr field names into meaningful keys
        """
        fields_map = {
            'clp': 'codice_locale',
            'slug': 'url',
            'titolo': 'titolo_progetto',
        }
        if field_name in fields_map:
            return fields_map[field_name]
        else:
            return field_name



class PaginatedProgettoSerializer(pagination.PaginationSerializer):
    """
    Serializes page objects of user querysets.
    """
    page_size = serializers.Field(source='paginator.per_page')
    current_page = serializers.Field(source='number')
    last_page = serializers.Field(source='paginator.num_pages')
    facet_counts = FacetsField()

    class Meta:
        object_serializer_class = ProgettoSearchResultSerializer


class ProgettoModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Progetto
        depth = 1




class SoggettoSearchResultSerializer(serializers.Serializer):
    """
    """

    slug = serializers.HyperlinkedIdentityField(view_name='api-soggetto-detail')
    denominazione = serializers.CharField(required=False)
    tema = serializers.RelatedField(many=True)
    ruolo = serializers.RelatedField(many=True)
    costo = serializers.FloatField()
    n_progetti = serializers.IntegerField()

    def get_field_key(self, field_name):
        """
        Transform inner solr field names into meaningful keys
        """
        fields_map = {
            'slug': 'url',
        }
        if field_name in fields_map:
            return fields_map[field_name]
        else:
            return field_name


class PaginatedSoggettoSerializer(pagination.PaginationSerializer):
    """
    Serializes page objects of user querysets.
    """
    page_size = serializers.Field(source='paginator.per_page')
    current_page = serializers.Field(source='number')
    last_page = serializers.Field(source='paginator.num_pages')
    facet_counts = FacetsField()

    class Meta:
        object_serializer_class = SoggettoSearchResultSerializer


class SoggettoModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Soggetto
        depth = 1



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
        req_format = self.context.get('format', None)
        progetti_filter_url = "{0}?{1}={2}".format(
                reverse('api-progetto-list', request=request, format=req_format),
                self.filter_name,
                obj.codice
            )
        soggetti_filter_url = "{0}?{1}={2}".format(
                reverse('api-soggetto-list', request=request, format=req_format),
                self.filter_name,
                obj.codice
            )

        ret = {
            'progetti': progetti_filter_url,
            'soggetti': soggetti_filter_url,
        }

        return ret


class TemaModelSerializer(serializers.ModelSerializer):
    filters = FiltersField('tema')

    class Meta:
        model = Tema
        exclude = ('descrizione_estesa', 'slug', 'tema_superiore', 'tipo_tema')
        depth = 1


class NaturaModelSerializer(serializers.ModelSerializer):
    filters = FiltersField('natura')

    class Meta:
        model = ClassificazioneAzione
        exclude = ('descrizione_estesa', 'slug', 'priorita', 'tipo_classificazione', 'classificazione_superiore')
        depth = 1


class TerritorioModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Territorio
        fields = ('denominazione', 'denominazione_ted', 'territorio', 'slug', 'cod_reg', 'cod_prov', 'cod_com')


class ProgrammaModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProgrammaAsseObiettivo

