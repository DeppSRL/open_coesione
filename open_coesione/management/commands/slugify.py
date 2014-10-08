"""
This command create slugs for various Model
- Territorio uses his denominazione
- ClassificazioneAzione (Nature) and Tema uses a file to mapping their descrizione with a label

mapping file is located in:
- dati/topic_mapping.csv for Tema
- dati/nature_mapping.csv for Nature

Usage:

`django-admin.py slugify --reset --type=topic
`django-admin.py slugify --type=topic
`django-admin.py slugify --reset --type=nature
`django-admin.py slugify --type=nature
`django-admin.py slugify --reset --type=loc
`django-admin.py slugify --type=loc

NOTE:
%_mapping.csv files has 'DB,SLUG' as Header (first line)


"""
import csv
from optparse import make_option
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.template.defaultfilters import slugify
from django.db import transaction
from progetti.models import Tema, ClassificazioneAzione, Progetto
from territori.models import Territorio
from soggetti.models import Soggetto
from blog.models import Entry
from open_coesione.models import Pillola

import logging



class Command(BaseCommand):
    help = 'Create slugs'
    logger = logging.getLogger('csvimport')

    option_list = BaseCommand.option_list + (
        make_option('--type',
                    dest='type',
                    default='proj',
                    help='Type of import: proj|loc|rec|blog|pillola|nature|topic'),
        make_option('--file',
            default='dati/{0}_mapping.csv',
            help='CSV file containing mapping for short_labels [dati/topic_mapping.csv|dati/nature_mapping.csv]'),

        make_option('--reset',
            default=False,
            action='store_true',
            help='Remove all slugs'),
    )

#    @transaction.commit_on_success
    def handle(self, *args, **options):
        if options['type'] == 'proj':
            self.handle_proj(*args, **options)
        elif options['type'] == 'loc':
            self.handle_loc(*args, **options)
        elif options['type'] == 'rec':
            self.handle_rec(*args, **options)
        elif options['type'] in ['blog', 'pillola']:
            self.handle_blog_pillola(*args, **options)
        elif options['type'] in ['nature', 'topic']:
            self.handle_short_labels(*args, **options)
        else:
            self.logger.error('Wrong type %s. Select among proj, loc, rec, blog, pillola, nature, topic' % options['type'])
            exit(1)

    @transaction.commit_manually
    def handle_proj(self, *args, **options):
        if options['reset']:
            Progetto.fullobjects.update(slug=None)
            transaction.commit()
            self.logger.info(u'Progetti slugs have been reset. Now exiting.')
            return

        progetti = Progetto.fullobjects.filter(slug__isnull=True)
        progetti_cnt = progetti.count()

        self.logger.info(u'{0} progetti will be slugified'.format(progetti_cnt))

        n = 0
        for progetto in progetti:
            n += 1

            slug = slugify(u'{0}'.format(progetto.codice_locale))
            cnt = 0
            ok = False
            while not ok:
                if cnt == 0:
                    progetto.slug = slug
                else:
                    progetto.slug = u'{0}-{1}'.format(slug, cnt)

                try:
                    sid = transaction.savepoint()
                    progetto.save()
                    transaction.savepoint_commit(sid)
                except:
                    transaction.savepoint_rollback(sid)
                    cnt += 1
                else:
                    ok = True

            if n % 100 == 0:
                self.logger.debug(u'{0}/{1}'.format(n, progetti_cnt))

            if (n % 5000 == 0) or (n == progetti_cnt):
                self.logger.info(u'{0} -----------------> Committing.'.format(n))
                transaction.commit()

        self.logger.info(u'Done!')


    def handle_loc(self, *args, **options):
        if options['reset']:
            Territorio.objects.update(slug=None)
            self.logger.info('territori slugs have been reset. now exiting')
            return

        territori = Territorio.objects.filter(slug__isnull=True)
        slug_utilizzati = {}
        self.logger.info('{0} territori will be slugified'.format(territori.count()))
        for n, territorio in enumerate(territori):
            slug = slugify(u'{0}-{1}'.format(territorio.denominazione, territorio.get_territorio_display() ))
            if slug in slug_utilizzati:
                # li differenzio aggiungendo la provincia alla fine
                # inizio modificando lo slug dell'altro territorio
                altro_territorio = slug_utilizzati[slug]
                altro_territorio.slug = u'{0}-{1}'.format(
                    altro_territorio.slug,
                    slugify(Territorio.objects.provincie().get(cod_prov=altro_territorio.cod_prov ))
                )
                altro_territorio.save()
                # a infine modifico lo slug corrente
                slug = u'{0}-{1}'.format(
                    slug,
                    slugify(Territorio.objects.provincie().get(cod_prov=territorio.cod_prov ))
                )
                self.logger.debug('found two Territori with same slug {0} - {1}'.format(territorio, altro_territorio) )
                self.logger.debug('-> changed to {0} - {1}'.format(slug, altro_territorio.slug) )
            else:
                slug_utilizzati[slug] = territorio

            territorio.slug = slug
            territorio.save()
            if n%100 == 0:
                self.logger.debug(n)

        self.logger.info('done!')



    def handle_rec(self, *args, **options):
        if options['reset']:
            Soggetto.objects.update(slug=None)
            self.logger.info('soggetti slugs have been reset. now exiting')
            return

        soggetti = Soggetto.objects.filter(slug__isnull=True)
        self.logger.info('{0} soggetti will be slugified'.format(soggetti.count()))
        for n, soggetto in enumerate(soggetti):

            if soggetto.codice_fiscale.strip() == '' or soggetto.codice_fiscale.strip() == '*CODICE FISCALE*':

                # handles non-existing or masked codice_fiscale cases

                # get the basic slug, from the denominazione field
                slug = slugify(u'{0}'.format(soggetto.denominazione))

                try:

                    # look for soggetti starting with the same basic slug
                    # in case no other soggetti are found, raise ObjectDoesNotExist
                    latest_slug = Soggetto.objects.filter(slug__contains=slug).latest('slug').slug

                    # transform the last bit of the slug into an integer
                    # in case it's not an integer, raise a ValueError if not an integer
                    # may happen for slugs generated in different ways, before this algorithm was implemented
                    last_index = int(latest_slug.split('-')[-1:][0])

                    # set slug, with increased last_index
                    soggetto.slug = '{0}-{1}'.format(slug, last_index+1)

                except (ValueError, ObjectDoesNotExist):

                    # generate slug, with an added '-1', to start the series
                    soggetto.slug = '{0}-1'.format(slug)
            else:

                # generate the slug using the codice_fiscale field
                soggetto.slug = slugify(u'{0}-{1}'.format(soggetto.denominazione, soggetto.codice_fiscale.strip() ))


            cnt = 0
            ok = False
            while not ok:
                if cnt == 0:
                    soggetto.slug = slug
                else:
                    soggetto.slug = u"{0}--{1}".format(slug, cnt)

                try:
                    sid = transaction.savepoint()
                    soggetto.save()
                    transaction.savepoint_commit(sid)
                except:
                    transaction.savepoint_rollback(sid)
                    cnt += 1
                else:
                    ok = True

            if n%100 == 0:
                self.logger.debug(n)

        self.logger.info('done!')


    def handle_blog_pillola(self, *args, **options):
        if options['type'] == 'blog':
            model = Entry
        else:
            model = Pillola

        if options['reset']:
            model.objects.update(slug=None)
            self.logger.info('{0} slugs have been reset. now exiting'.format(options['type']))
            return

        objects = model.objects.filter(slug__isnull=True)
        self.logger.info('{0} {1} will be slugified'.format(objects.count(), options['type']))
        for n, object in enumerate(objects):
            object.slug = slugify(u'{0}'.format(object.title))
            object.save()
            if n%100 == 0:
                self.logger.debug(n)

        self.logger.info('done!')



    def handle_short_labels(self, *args, **options):
        with open( options['file'].format(options['type']), 'rb' ) as f:

            reader = csv.DictReader(f, delimiter=',')

            model = {
                'topic': Tema,
                'nature': ClassificazioneAzione
            }[ options['type'] ]

            for row in reader:

                self.logger.debug('* try to retrieve "{0}" from {1}s'.format(row['DB'], options['type']))

                instance = [
                    # takes all objects with this descrizione
                    x for x in model.objects.filter( descrizione = row['DB'] )
                    # and filter by is_root property
                    if x.is_root
                ][0] # we wants only one instance...

                instance.short_label = row['SLUG']
                instance.slug = slugify('{0}'.format(row['SLUG']))
                instance.save()

                self.logger.debug('- seek "{0}": "{1}"'.format( row[ 'SLUG' ], instance if instance else 'NOT FOUND' ))


        self.logger.debug('{0} {1} have been slugified\n'.format(reader.line_num,options['type']))
