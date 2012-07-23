"""
This command extracts a list of non-localized projects

Usage:

`django-admin.py extractnonlocprojects

"""
from django.core.management.base import BaseCommand
from progetti.models import Progetto

import logging

class Command(BaseCommand):
    help = "Create slugs for Territori"
    logger = logging.getLogger('csvimport')

    option_list = BaseCommand.option_list

    #    @transaction.commit_on_success
    def handle(self, *args, **options):
        nlp = Progetto.objects.filter(territorio_set__isnull=True)
        print "codice_locale,cup"
        for p in nlp:
            print "\"{0}\",{1}".format(p.codice_locale.strip(), p.cup.strip())



