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

class Command(BaseCommand):
    help = "Create slugs for Territori"
    allowed_models = ['location','topic','nature','project']

    option_list = BaseCommand.option_list + (
        make_option('--model',
            default='location',
            help='Model to slugify [{0}]'.format('|'.join(allowed_models))),

        make_option('--file',
            default='dati/{0}_mapping.csv',
            help='Model to slugify [location|topic|nature]'),

        make_option('--reset',
            default=False,
            action="store_true",
            help='Remove all slugs'),
    )

    @transaction.commit_on_success
    def handle(self, *args, **options):

        models = [ options['model'], ] if not options['model'] == 'all' else self.allowed_models

        for model in models:

            options['model'] = model

            if options['reset']:

                self.handle_reset( *args,**options )

            else:

                self.handle_slugs( *args,**options )



    def handle_reset(self, *args, **options):

        if options['model'] == 'location':

            Territorio.objects.update(slug='')

        if options['model'] == 'topic':

            Tema.objects.update(short_label='')

        if options['model'] == 'nature':

            ClassificazioneAzione.objects.update(short_label='')

        if options['model'] == 'project':

            Progetto.objects.update(slug='')

        print "Slug for '{0}' has been cleaned".format(options['model'])

    def handle_slugs(self, *args, **options):

        count = 0
        key_db, key_slug = 'DB', 'SLUG'

        if options['model'] == 'location':

            for territorio in Territorio.objects.all():
                print "{1} - Slugify {0}".format(territorio, count)
                # skipping already populated
                if territorio.slug:
                    continue
                territorio.slug = slugify(territorio.denominazione)
                territorio.save()
                count += 1

        elif options['model'] == 'project':

            for progetto in Progetto.objects.all():
                print "{1} - Slugify {0}".format(progetto, count)
                # skipping already populated
                if progetto.slug:
                    continue
                progetto.slug = slugify(progetto.codice_locale)
                progetto.save()
                count += 1

        else:
            print options['file']
            with open( options['file'].format(options['model']), 'rb' ) as f:

                reader = csv.DictReader(f, delimiter=',')

                model = {
                    'topic': Tema,
                    'nature': ClassificazioneAzione
                }[ options['model'] ]

                for row in reader:

                    print "* try to retrieve '{0}' from {1}s".format(row[ key_db ], options['model'])

                    instance = [
                        # takes all objects with this descrizione
                        x for x in model.objects.filter( descrizione = row[ key_db ] )
                        # and filter by is_root property
                        if x.is_root
                    ][0] # we wants only one instance...

                    instance.short_label = row[ key_slug ]
                    instance.save()

                    print "- seek '{0}': '{1}'".format( row[ key_slug ], instance if instance else 'NOT FOUND' )
                    count += 1


        print "{0} {1} have been slugified\n".format(count,options['model'])
