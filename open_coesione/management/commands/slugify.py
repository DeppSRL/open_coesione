from optparse import make_option

from django.core.management.base import BaseCommand
from django.db import transaction
from django.template.defaultfilters import slugify
from territori.models import Territorio
from progetti.models import Progetto
from soggetti.models import Soggetto

import logging

class Command(BaseCommand):
    help = "Create slugs for Territori"
    logger = logging.getLogger('csvimport')

    option_list = BaseCommand.option_list + (
        make_option('--type',
                    dest='type',
                    default='proj',
                    help='Type of import: proj|loc|rec'),
        make_option('--reset',
            default=False,
            help='Remove all slugs'),
    )

    def handle(self, *args, **options):
        if options['type'] == 'proj':
            self.handle_proj(*args, **options)
        elif options['type'] == 'loc':
            self.handle_loc(*args, **options)
        elif options['type'] == 'rec':
            self.handle_rec(*args, **options)
        else:
            self.logger.error("Wrong type %s. Select among proj, loc and rec." % options['type'])
            exit(1)

    def handle_proj(self, *args, **options):
        if options['reset']:
            Progetto.objects.update(slug=None)
            self.logger.info("progetti slugs have been reset. now exiting")
            return

        progetti = Progetto.objects.filter(slug__isnull=True)
        self.logger.info("{0} progetti will be slugified".format(progetti.count()))
        for n, progetto in enumerate(progetti):
            progetto.slug = slugify("{0}".format(progetto.codice_locale))
            progetto.save()
            if n%100 == 0:
                self.logger.debug(n)

        self.logger.info("done!")


    def handle_loc(self, *args, **options):
        with transaction.commit_on_success():
            if options['reset']:
                Territorio.objects.update(slug='')
                self.logger.info("territori slugs have been reset. now exiting")
                return

            count = 0
            for territorio in Territorio.objects.all():
                # skipping already populated
                if territorio.slug:
                    continue
                territorio.slug = slugify(territorio.denominazione)
                territorio.save()
                count += 1

        self.logger.info("{0} territori have been slugified\n".format(count))
