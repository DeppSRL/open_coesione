"""
This command create slugs for various Model
- Territorio uses his denominazione
- ClassificazioneAzione (Nature) and Tema uses a file to mapping their descrizione with a label

mapping file is located in:
- dati/topic_mapping.csv for Tema
- dati/nature_mapping.csv for Nature

Usage:

`django-admin.py slugify --reset --model=topic
`django-admin.py slugify --model=topic
`django-admin.py slugify --reset --model=nature
`django-admin.py slugify --model=nature
`django-admin.py slugify --reset --model=location
`django-admin.py slugify --model=location

NOTE:
%_mapping.csv files has 'DB,SLUG' as Header (first line)


"""
import csv
from optparse import make_option

from django.core.management.base import BaseCommand
from django.db import transaction
from django.template.defaultfilters import slugify
from progetti.models import Tema, ClassificazioneAzione, Progetto
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
                    help='Type of import: proj|loc|rec|nature|topic'),
        make_option('--file',
            default='dati/{0}_mapping.csv',
            help='CSV file containing mapping for short_labels [dati/topic_mapping.csv|dati/nature_mapping.csv]'),

        make_option('--reset',
            default=False,
            action="store_true",
            help='Remove all slugs'),
    )

    @transaction.commit_on_success
    def handle(self, *args, **options):
        if options['type'] == 'proj':
            self.handle_proj(*args, **options)
        elif options['type'] == 'loc':
            self.handle_loc(*args, **options)
        elif options['type'] == 'rec':
            self.handle_rec(*args, **options)
        elif options['type'] in ['nature', 'topic']:
            self.handle_short_labels(*args, **options)
        else:
            self.logger.error("Wrong type %s. Select among proj, loc, rec, nature, topic" % options['type'])
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
        if options['reset']:
            Territorio.objects.update(slug=None)
            self.logger.info("territori slugs have been reset. now exiting")
            return

        territori = Territorio.objects.filter(slug__isnull=True)
        self.logger.info("{0} territori will be slugified".format(territori.count()))
        for n, territorio in enumerate(territori):
            territorio.slug = slugify("{0}".format(territorio.codice_locale))
            territorio.save()
            if n%100 == 0:
                self.logger.debug(n)

        self.logger.info("done!")



    def handle_rec(self, *args, **options):
        if options['reset']:
            Soggetto.objects.update(slug=None)
            self.logger.info("soggetti slugs have been reset. now exiting")
            return

        soggetti = Soggetto.objects.filter(slug__isnull=True)
        self.logger.info("{0} soggetti will be slugified".format(soggetti.count()))
        for n, soggetto in enumerate(soggetti):
            soggetto.slug = slugify("{0}".format(soggetto.codice_locale))
            soggetto.save()
            if n%100 == 0:
                self.logger.debug(n)

        self.logger.info("done!")


    def handle_short_labels(self, *args, **options):
        with open( options['file'].format(options['type']), 'rb' ) as f:

            reader = csv.DictReader(f, delimiter=',')

            model = {
                'topic': Tema,
                'nature': ClassificazioneAzione
            }[ options['type'] ]

            for row in reader:

                self.logger.debug("* try to retrieve '{0}' from {1}s".format(row['DB'], options['type']))

                instance = [
                    # takes all objects with this descrizione
                    x for x in model.objects.filter( descrizione = row['DB'] )
                    # and filter by is_root property
                    if x.is_root
                ][0] # we wants only one instance...

                instance.short_label = row['SLUG']
                instance.save()

                self.logger.debug("- seek '{0}': '{1}'".format( row[ 'SLUG' ], instance if instance else 'NOT FOUND' ))


        self.logger.debug("{0} {1} have been slugified\n".format(reader.line_num,options['type']))
