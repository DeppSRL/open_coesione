from django.core.management.base import BaseCommand

import logging

from progetti.models import ProgrammaAsseObiettivo, ProgrammaLineaAzione

class Command(BaseCommand):
    help = "Move links and documenti relations from ProgrammaAsseObiettivo/ProgrammaLineaAzione tables to ProgrammaAsseObiettivoExtraInfo/ProgrammaLineaAzioneExtraInfo tables respectively"
    logger = logging.getLogger('csvimport')

    def handle(self, *args, **options):
        for model in [ProgrammaAsseObiettivo, ProgrammaLineaAzione]:
            objects = model.objects.all()
            for object in objects:
                for link in object.links.all():
                    self.logger.info('{0} | codice: {1} (link: {2})'.format(model, object.codice, link.url))
                    link.content_object=object.extra_info
                    link.save()

                for documento in object.documenti.all():
                    self.logger.info('{0} | codice: {1} (documento: {2})'.format(model, object.codice, documento.file))
                    documento.content_object=object.extra_info
                    documento.save()

        self.logger.info('done!')
