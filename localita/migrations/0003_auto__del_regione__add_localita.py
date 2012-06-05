# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Regione'
        db.delete_table('localita_regione')

        # Adding model 'Localita'
        db.create_table('localita_localita', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cod_reg', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('cod_prov', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('cod_com', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('denominazione', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('territorio', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('geom', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')()),
        ))
        db.send_create_signal('localita', ['Localita'])


    def backwards(self, orm):
        # Adding model 'Regione'
        db.create_table('localita_regione', (
            ('nome_reg', self.gf('django.db.models.fields.CharField')(max_length=123)),
            ('geom', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')()),
            ('shape_leng', self.gf('django.db.models.fields.FloatField')()),
            ('shape_area', self.gf('django.db.models.fields.FloatField')()),
            ('field_2', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cod_reg', self.gf('django.db.models.fields.IntegerField')()),
            ('field_1', self.gf('django.db.models.fields.CharField')(max_length=80)),
        ))
        db.send_create_signal('localita', ['Regione'])

        # Deleting model 'Localita'
        db.delete_table('localita_localita')


    models = {
        'localita.localita': {
            'Meta': {'object_name': 'Localita'},
            'cod_com': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'cod_prov': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'cod_reg': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'denominazione': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'geom': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'territorio': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        }
    }

    complete_apps = ['localita']