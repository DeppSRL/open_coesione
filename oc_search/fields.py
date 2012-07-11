from django.utils import translation
from django.conf import settings
from haystack.fields import SearchField

class L10NCharField(SearchField):
    """
    Standard SearchFields fail to correctly set up the language code when
    launched in the reuild_index or update_index management commands.

    This may results in problems with L10N and conversions of dates and numbers.

    This is a problem with the prepare_template method that should firstly
    activate the translations, in order to enable the LANGUAGE_CODE settings
    """

    def prepare_template(self, obj):

        translation.activate(settings.LANGUAGE_CODE)
        return super(L10NCharField, self).prepare_template(obj)

