import logging
from optparse import make_option
from django.core.management import BaseCommand
from progetti.models import Progetto


class Command(BaseCommand):
    """
    All projects having CLP in the list read from the CSV file,
    are **de-activated**.

    De-activation means that the ``active_flag`` is set to False.

    This is performed through a bulk update.
    """
    help = "Deactivate progetti, read data from csv"

    option_list = BaseCommand.option_list + (
        make_option('--csv-file',
                    dest='csvfile',
                    default='./clp_deactivate.csv',
                    help='Select csv file'),
        make_option('--limit',
                    dest='limit',
                    default=0,
                    help='Limit of records to import'),
        make_option('--offset',
                    dest='offset',
                    default=0,
                    help='Offset of records to import'),
        make_option('--dryrun',
                    dest='dryrun',
                    action='store_true',
                    help='Offset of records to import'),
    )

    logger = logging.getLogger('csvimport')

    def handle(self, *args, **options):
        self.csv_file = options['csvfile']

        f = None

        # read csv file
        try:
            f = open(self.csv_file, 'r')
        except IOError:
            self.logger.error("It was impossible to open file %s" % self.csv_file)
            exit(1)

        offset = options['offset']
        limit = options['limit']

        verbosity = options['verbosity']
        if verbosity == '0':
            self.logger.setLevel(logging.ERROR)
        elif verbosity == '1':
            self.logger.setLevel(logging.WARNING)
        elif verbosity == '2':
            self.logger.setLevel(logging.INFO)
        elif verbosity == '3':
            self.logger.setLevel(logging.DEBUG)

        # put lines of csv file into a list
        clps = f.readlines()
        self.logger.info('{0} lines read from {1}'.format(len(clps), self.csv_file))

        # remove \n and quotes from each line
        clps = map(lambda x: x.rstrip()[1:-1], clps)
        self.logger.debug('lines stripped of CR and quotes')

        # consider offset and limit, if given
        if limit:
            clps = clps[offset:limit]
        else:
            clps = clps[offset:]

        # get all listed progetti, among the active, excluding CIPE
        p = Progetto.objects.filter(pk__in=clps).exclude(cipe_flag=True)
        self.logger.info('{0} progetti matching'.format(p.count()))

        # bulk update, if not dryrun
        if not options['dryrun']:
            res = p.update(active_flag=False)
            self.logger.info('{0} progetti updated'.format(res))

