from optparse import make_option

from django.core.management.base import BaseCommand
from django.db import transaction
from django.template.defaultfilters import slugify
from territori.models import Territorio

class Command(BaseCommand):
    help = "Create slugs for Territori"

    option_list = BaseCommand.option_list + (
        make_option('--reset',
            default=False,
            help='Remove all slugs'),
    )

    def handle(self, *args, **options):

        with transaction.commit_on_success():
            if options['reset']:
                Territorio.objects.update(slug='')
                return

            count = 0
            for territorio in Territorio.objects.all():
                # skipping already populated
                if territorio.slug:
                    continue
                territorio.slug = slugify(territorio.denominazione)
                territorio.save()
                count += 1

        self.stdout.write("{0} territori has been slugified\n".format(count))
