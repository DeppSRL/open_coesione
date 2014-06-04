from django.core.management.base import BaseCommand
from django.db.models import F

import logging

from progetti.models import ProgrammaAsseObiettivo, ProgrammaLineaAzione
from open_coesione.models import URL

class Command(BaseCommand):
    help = "Move url_riferimento content from ProgrammaAsseObiettivo/ProgrammaLineaAzione tables to URL table"
    logger = logging.getLogger('csvimport')

    def handle(self, *args, **options):
        for model in [ProgrammaAsseObiettivo, ProgrammaLineaAzione]:
            objects = model.objects.exclude(url_riferimento__isnull=True).exclude(url_riferimento='').exclude(urls_riferimento__url=F('url_riferimento'))
            for object in objects:
                self.logger.info('{0} | codice: {1} ({2})'.format(model, object.codice, object.url_riferimento))
                url = URL(content_object=object, url=object.url_riferimento)
                url.save()

        self.logger.info('done!')
