# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Regione.nome_reg'
        db.alter_column('localita_regione', 'nome_reg', self.gf('django.db.models.fields.CharField')(max_length=123))

    def backwards(self, orm):

        # Changing field 'Regione.nome_reg'
        db.alter_column('localita_regione', 'nome_reg', self.gf('django.db.models.fields.CharField')(max_length=128))

    models = {
        'localita.regione': {
            'Meta': {'object_name': 'Regione'},
            'cod_reg': ('django.db.models.fields.IntegerField', [], {}),
            'field_1': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'field_2': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome_reg': ('django.db.models.fields.CharField', [], {'max_length': '123'}),
            'shape_area': ('django.db.models.fields.FloatField', [], {}),
            'shape_leng': ('django.db.models.fields.FloatField', [], {})
        }
    }

    complete_apps = ['localita']