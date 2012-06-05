# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Localita.denominazione_ted'
        db.add_column('localita_localita', 'denominazione_ted',
                      self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True),
                      keep_default=False)


        # Changing field 'Localita.cod_prov'
        db.alter_column('localita_localita', 'cod_prov', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'Localita.cod_com'
        db.alter_column('localita_localita', 'cod_com', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'Localita.cod_reg'
        db.alter_column('localita_localita', 'cod_reg', self.gf('django.db.models.fields.IntegerField')(null=True))

    def backwards(self, orm):
        # Deleting field 'Localita.denominazione_ted'
        db.delete_column('localita_localita', 'denominazione_ted')


        # Changing field 'Localita.cod_prov'
        db.alter_column('localita_localita', 'cod_prov', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'Localita.cod_com'
        db.alter_column('localita_localita', 'cod_com', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'Localita.cod_reg'
        db.alter_column('localita_localita', 'cod_reg', self.gf('django.db.models.fields.IntegerField')())

    models = {
        'localita.localita': {
            'Meta': {'object_name': 'Localita'},
            'cod_com': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'cod_prov': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'cod_reg': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'denominazione': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'denominazione_ted': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'territorio': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        }
    }

    complete_apps = ['localita']