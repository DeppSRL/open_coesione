# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Indicatore'
        db.create_table(u'charts_indicatore', (
            ('codice', self.gf('django.db.models.fields.CharField')(max_length=3, primary_key=True)),
            ('titolo', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('sottotitolo', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('tema', self.gf('django.db.models.fields.related.ForeignKey')(related_name='indicatori', to=orm['progetti.Tema'])),
        ))
        db.send_create_signal(u'charts', ['Indicatore'])

        # Adding model 'Ripartizione'
        db.create_table(u'charts_ripartizione', (
            ('id', self.gf('django.db.models.fields.PositiveSmallIntegerField')(primary_key=True)),
            ('descrizione', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'charts', ['Ripartizione'])

        # Adding model 'IndicatoreRegionale'
        db.create_table(u'charts_indicatoreregionale', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('indicatore', self.gf('django.db.models.fields.related.ForeignKey')(related_name='indicatori_regionali', to=orm['charts.Indicatore'])),
            ('ripartizione', self.gf('django.db.models.fields.related.ForeignKey')(related_name='indicatori_regionali', to=orm['charts.Ripartizione'])),
            ('anno', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('valore', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('da_eliminare', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
        ))
        db.send_create_signal(u'charts', ['IndicatoreRegionale'])

        # Adding unique constraint on 'IndicatoreRegionale', fields ['indicatore', 'ripartizione', 'anno']
        db.create_unique(u'charts_indicatoreregionale', ['indicatore_id', 'ripartizione_id', 'anno'])

        # Adding index on 'IndicatoreRegionale', fields ['indicatore', 'ripartizione', 'anno']
        db.create_index(u'charts_indicatoreregionale', ['indicatore_id', 'ripartizione_id', 'anno'])


    def backwards(self, orm):
        # Removing index on 'IndicatoreRegionale', fields ['indicatore', 'ripartizione', 'anno']
        db.delete_index(u'charts_indicatoreregionale', ['indicatore_id', 'ripartizione_id', 'anno'])

        # Removing unique constraint on 'IndicatoreRegionale', fields ['indicatore', 'ripartizione', 'anno']
        db.delete_unique(u'charts_indicatoreregionale', ['indicatore_id', 'ripartizione_id', 'anno'])

        # Deleting model 'Indicatore'
        db.delete_table(u'charts_indicatore')

        # Deleting model 'Ripartizione'
        db.delete_table(u'charts_ripartizione')

        # Deleting model 'IndicatoreRegionale'
        db.delete_table(u'charts_indicatoreregionale')


    models = {
        u'charts.indicatore': {
            'Meta': {'object_name': 'Indicatore'},
            'codice': ('django.db.models.fields.CharField', [], {'max_length': '3', 'primary_key': 'True'}),
            'sottotitolo': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'tema': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'indicatori'", 'to': u"orm['progetti.Tema']"}),
            'titolo': ('django.db.models.fields.CharField', [], {'max_length': '150'})
        },
        u'charts.indicatoreregionale': {
            'Meta': {'unique_together': "(('indicatore', 'ripartizione', 'anno'),)", 'object_name': 'IndicatoreRegionale', 'index_together': "[['indicatore', 'ripartizione', 'anno']]"},
            'anno': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'da_eliminare': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indicatore': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'indicatori_regionali'", 'to': u"orm['charts.Indicatore']"}),
            'ripartizione': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'indicatori_regionali'", 'to': u"orm['charts.Ripartizione']"}),
            'valore': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'charts.ripartizione': {
            'Meta': {'object_name': 'Ripartizione'},
            'descrizione': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.PositiveSmallIntegerField', [], {'primary_key': 'True'})
        },
        u'progetti.tema': {
            'Meta': {'ordering': "['priorita', 'codice']", 'object_name': 'Tema'},
            'codice': ('django.db.models.fields.CharField', [], {'max_length': '16', 'primary_key': 'True'}),
            'descrizione': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'descrizione_estesa': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'priorita': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'short_label': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'slug': ('django_extensions.db.fields.AutoSlugField', [], {'null': 'True', 'populate_from': "'descrizione'", 'allow_duplicates': 'False', 'max_length': '64', 'separator': "u'-'", 'blank': 'True', 'unique': 'True', 'overwrite': 'False'}),
            'tema_superiore': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tema_set'", 'db_column': "'tema_superiore'", 'default': 'None', 'to': u"orm['progetti.Tema']", 'blank': 'True', 'null': 'True'}),
            'tipo_tema': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        }
    }

    complete_apps = ['charts']