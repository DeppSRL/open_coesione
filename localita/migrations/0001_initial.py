# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Regione'
        db.create_table('localita_regione', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cod_reg', self.gf('django.db.models.fields.IntegerField')()),
            ('nome_reg', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('shape_leng', self.gf('django.db.models.fields.FloatField')()),
            ('shape_area', self.gf('django.db.models.fields.FloatField')()),
            ('field_1', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('field_2', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('geom', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')()),
        ))
        db.send_create_signal('localita', ['Regione'])


    def backwards(self, orm):
        # Deleting model 'Regione'
        db.delete_table('localita_regione')


    models = {
        'localita.regione': {
            'Meta': {'object_name': 'Regione'},
            'cod_reg': ('django.db.models.fields.IntegerField', [], {}),
            'field_1': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'field_2': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nome_reg': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'shape_area': ('django.db.models.fields.FloatField', [], {}),
            'shape_leng': ('django.db.models.fields.FloatField', [], {})
        }
    }

    complete_apps = ['localita']