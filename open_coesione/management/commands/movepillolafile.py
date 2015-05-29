import os
import shutil
from django.core.management.base import BaseCommand

import logging
from django.template.defaultfilters import slugify
from open_coesione import settings

from open_coesione.models import File, Pillola

media = lambda f: os.path.join(settings.MEDIA_ROOT, f)

class Command(BaseCommand):
    help = 'Move file content from Pillola tables to File table'
    logger = logging.getLogger('csvimport')

    def handle(self, *args, **options):
        objects = Pillola.objects.exclude(file__isnull=True).exclude(file='')
        for object in objects:
            filename = str(object.file)
            basename = os.path.basename(filename)

            newdirname = os.path.join('files', slugify('{0} {1}'.format('Pillola', object.id)))
            newfilename = os.path.join(newdirname, basename)

            if not os.path.isdir(media(newdirname)):
                os.makedirs(media(newdirname))

            shutil.copyfile(media(filename), media(newfilename))

            file = File(content_object=object, description=basename, file=newfilename)
            file.save()

            object.file = None
            object.save()

            self.logger.info('Pillola: {} ({} -> {})'.format(object, filename, newfilename))

        self.logger.info('done!')
