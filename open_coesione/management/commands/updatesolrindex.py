from optparse import make_option
from haystack.management.commands.update_index import do_update, do_remove, get_site, build_queryset, worker
from django.core.management.base import AppCommand
from django.conf import settings
from django.utils.encoding import smart_str

DEFAULT_BATCH_SIZE = getattr(settings, 'HAYSTACK_BATCH_SIZE', 1000)
DEFAULT_AGE = None

class Command(AppCommand):
    help = "Freshens the index for the given app(s)."
    base_options = (
        make_option('-a', '--age', action='store', dest='age',
            default=DEFAULT_AGE, type='int',
            help='Number of hours back to consider objects new.'
        ),
        make_option('-b', '--batch-size', action='store', dest='batchsize',
            default=DEFAULT_BATCH_SIZE, type='int',
            help='Number of items to index at once.'
        ),
        make_option('-s', '--site', action='store', dest='site',
            type='string', help='The site object to use when reindexing (like `search_sites.mysite`).'
        ),
        make_option('-k', '--workers', action='store', dest='workers',
            default=0, type='int', 
            help='Allows for the use multiple workers to parallelize indexing. Requires multiprocessing.'
        ),
        make_option('-l', '--limit', action='store', dest='limit',
            default=0, type='int',
            help='Upper limit to the number of items to index.'
        ),
        make_option('-o', '--offset', action='store', dest='offset',
            default=0, type='int',
            help='Offset of items to index.'
        ),
    )
    option_list = AppCommand.option_list + base_options
    
    # Django 1.0.X compatibility.
    verbosity_present = False
    
    for option in option_list:
        if option.get_opt_string() == '--verbosity':
            verbosity_present = True
    
    if verbosity_present is False:
        option_list = option_list + (
            make_option('--verbosity', action='store', dest='verbosity', default='1',
                type='choice', choices=['0', '1', '2'],
                help='Verbosity level; 0=minimal output, 1=normal output, 2=all output'
            ),
        )
    
    def handle(self, *apps, **options):
        self.verbosity = int(options.get('verbosity', 1))
        self.batchsize = options.get('batchsize', DEFAULT_BATCH_SIZE)
        self.age = options.get('age', DEFAULT_AGE)
        self.site = options.get('site')
        self.limit = int(options.get('limit', 0))
        self.offset = int(options.get('offset', 0))

        if not apps:
            from django.db.models import get_app
            # Do all, in an INSTALLED_APPS sorted order.
            apps = []
            
            for app in settings.INSTALLED_APPS:
                try:
                    app_label = app.split('.')[-1]
                    loaded_app = get_app(app_label)
                    apps.append(app_label)
                except:
                    # No models, no problem.
                    pass
            
        return super(Command, self).handle(*apps, **options)
    
    def handle_app(self, app, **options):
        from django.db.models import get_models
        from haystack.exceptions import NotRegistered
        
        site = get_site(self.site)
        
        for model in get_models(app):
            try:
                index = site.get_index(model)
                # Manually set the ``site`` on the backend to the correct one.
                index.backend.site = site
            except NotRegistered:
                if self.verbosity >= 2:
                    print "Skipping '%s' - no index." % model
                continue
                

            qs = build_queryset(index, model, age=self.age, verbosity=self.verbosity)
            total = qs.count()
            if self.limit == 0 and self.offset == 0:
                pass
            else:
                if self.limit == 0:
                    qs = qs[self.offset:]
                    total = total - self.offset
                else:
                    qs = qs[self.offset:(self.offset + self.limit)]
                    total = self.limit

            if self.verbosity >= 1:
                print "Indexing %d %s." % (total, smart_str(model._meta.verbose_name_plural))
            
            pks_seen = set([smart_str(pk) for pk in qs.values_list('pk', flat=True)])
            
            for start in range(0, total, self.batchsize):
                end = min(start + self.batchsize, total)
                
                do_update(index, qs, start, end, total, self.verbosity)

