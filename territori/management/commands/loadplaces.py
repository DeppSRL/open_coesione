# -*- coding: utf-8 -*-
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.db.models.signals import pre_save
from django.contrib.gis.utils import LayerMapping
from django.conf import settings
from territori.models import Territorio
import os

class Command(BaseCommand):
    help = "Load places from specified shapefiles"
    option_list = BaseCommand.option_list + (
        make_option('--geolevel',
                    action='store',
                    dest='geolevel'),
    )

    regione_mapping = {
        'cod_reg' :       'COD_REG',
        'denominazione' : 'NOME_REG',
        'geom' :          'MULTIPOLYGON',
    }
    regione_shp = os.path.abspath(os.path.join(settings.REPO_ROOT, 'dati/reg2011_g/regioni_stats.shp'))

    provincia_mapping = {
        'cod_reg' :       'COD_REG',
        'cod_prov' :      'COD_PRO',
        'denominazione' : 'NOME_PRO',
        'geom' :          'MULTIPOLYGON',
    }
    provincia_shp = os.path.abspath(os.path.join(settings.REPO_ROOT, 'dati/prov2011_g/prov2011_g.shp'))

    comune_mapping = {
        'cod_reg' :           'COD_REG',
        'cod_prov' :          'COD_PRO',
        'cod_com' :           'PRO_COM',
        'denominazione' :     'NOME_COM',
        'denominazione_ted' : 'NOME_TED',
        'geom' :              'MULTIPOLYGON',
    }
    comune_shp = os.path.abspath(os.path.join(settings.REPO_ROOT, 'dati/com2011_g/com2011_g.shp'))

    def handle(self, *args, **options):
        if options['geolevel']:
            # swap keys and values in TERRITORIO
            # use --geolevel=regione
            geolevels = dict((value.lower(), key) for key, value in dict(Territorio.TERRITORIO).iteritems())
            geolevel = geolevels[options['geolevel'].lower()]


            def _set_geolevel(sender, instance, **kwargs):
                """
                Signal callback to set the geolevel for a
                place
                """
                instance.territorio = geolevel

            pre_save.connect(_set_geolevel, sender=Territorio)


            # based, on geolevel, define source, mapping and reference system ID
            if geolevel == 'C':
                shapefile = self.comune_shp
                mapping = self.comune_mapping
                source_srs = 23032
            elif geolevel == 'P':
                shapefile = self.provincia_shp
                mapping = self.provincia_mapping
                source_srs = 23032
            elif geolevel == 'R':
                shapefile = self.regione_shp
                mapping = self.regione_mapping
                source_srs = 900913
            else:
                raise CommandError("supported geolevels: regione, comune")

            lm = LayerMapping(Territorio, shapefile, mapping, source_srs=source_srs)
            lm.save(verbose=True)

        else:
            raise CommandError("geolevel must be specified")