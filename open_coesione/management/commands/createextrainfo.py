from django.core.management.base import BaseCommand

import logging

from progetti.models import ProgrammaAsseObiettivo, ProgrammaLineaAzione

class Command(BaseCommand):
    help = "Create ExtraInfo object for each ProgrammaAsseObiettivo/ProgrammaLineaAzione object"
    logger = logging.getLogger('csvimport')

    def handle(self, *args, **options):
        for model in [ProgrammaAsseObiettivo, ProgrammaLineaAzione]:
            objects = model.objects.all()
            for object in objects:
                i = object.extra_info

        self.logger.info('done!')
