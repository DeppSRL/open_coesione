# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ClassificazioneQSN'
        db.create_table('mct_progetti_classificazioneqsn', (
            ('classificazione_superiore', self.gf('django.db.models.fields.related.ForeignKey')(related_name='classificazione_set', db_column='classificazione_superiore', default=None, to=orm['mct_progetti.ClassificazioneQSN'], blank=True, null=True)),
            ('codice', self.gf('django.db.models.fields.CharField')(max_length=16, primary_key=True)),
            ('descrizione', self.gf('django.db.models.fields.TextField')()),
            ('tipo_classificazione', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal('mct_progetti', ['ClassificazioneQSN'])

        # Adding model 'ProgrammaAsseObiettivo'
        db.create_table('mct_progetti_programmaasseobiettivo', (
            ('classificazione_superiore', self.gf('django.db.models.fields.related.ForeignKey')(related_name='classificazione_set', db_column='classificazione_superiore', default=None, to=orm['mct_progetti.ProgrammaAsseObiettivo'], blank=True, null=True)),
            ('codice', self.gf('django.db.models.fields.CharField')(max_length=32, primary_key=True)),
            ('descrizione', self.gf('django.db.models.fields.TextField')()),
            ('tipo_classificazione', self.gf('django.db.models.fields.CharField')(max_length=32)),
        ))
        db.send_create_signal('mct_progetti', ['ProgrammaAsseObiettivo'])

        # Adding model 'Tema'
        db.create_table('mct_progetti_tema', (
            ('tema_superiore', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tema_set', db_column='tema_superiore', default=None, to=orm['mct_progetti.Tema'], blank=True, null=True)),
            ('codice', self.gf('django.db.models.fields.CharField')(max_length=16, primary_key=True)),
            ('descrizione', self.gf('django.db.models.fields.TextField')()),
            ('tipo_tema', self.gf('django.db.models.fields.CharField')(max_length=16)),
        ))
        db.send_create_signal('mct_progetti', ['Tema'])

        # Adding model 'Intesa'
        db.create_table('mct_progetti_intesa', (
            ('codice', self.gf('django.db.models.fields.CharField')(max_length=8, primary_key=True)),
            ('descrizione', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('mct_progetti', ['Intesa'])

        # Adding model 'ClassificazioneAzione'
        db.create_table('mct_progetti_classificazioneazione', (
            ('classificazione_superiore', self.gf('django.db.models.fields.related.ForeignKey')(related_name='classificazione_set', db_column='classificazione_superiore', default=None, to=orm['mct_progetti.ClassificazioneAzione'], blank=True, null=True)),
            ('codice', self.gf('django.db.models.fields.CharField')(max_length=8, primary_key=True)),
            ('descrizione', self.gf('django.db.models.fields.TextField')()),
            ('tipo_classificazione', self.gf('django.db.models.fields.CharField')(max_length=16)),
        ))
        db.send_create_signal('mct_progetti', ['ClassificazioneAzione'])

        # Adding model 'Progetto'
        db.create_table('mct_progetti_progetto', (
            ('codice_locale', self.gf('django.db.models.fields.CharField')(max_length=100, primary_key=True, db_column='cod_locale_progetto')),
            ('cup', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('titolo_progetto', self.gf('django.db.models.fields.TextField')()),
            ('classificazione_qsn', self.gf('django.db.models.fields.related.ForeignKey')(related_name='progetto_set', db_column='classificazione_qsn', to=orm['mct_progetti.ClassificazioneQSN'])),
            ('stato_fs', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('stato_fsc', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('stato_dps', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('programma_asse_obiettivo', self.gf('django.db.models.fields.related.ForeignKey')(related_name='progetto_set', db_column='programma_asse_progetto', to=orm['mct_progetti.ProgrammaAsseObiettivo'])),
            ('data_aggiornamento', self.gf('django.db.models.fields.DateField')(null=True)),
            ('obiettivo_sviluppo', self.gf('django.db.models.fields.CharField')(max_length=16, null=True, blank=True)),
            ('tipo_operazione', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('fondo_comunitario', self.gf('django.db.models.fields.CharField')(max_length=4, null=True, blank=True)),
            ('tema', self.gf('django.db.models.fields.related.ForeignKey')(related_name='progetto_set', db_column='tema', to=orm['mct_progetti.Tema'])),
            ('intesa_istituzionale', self.gf('django.db.models.fields.related.ForeignKey')(related_name='progetto_set', db_column='intesa_istituzionale', to=orm['mct_progetti.Intesa'])),
            ('classificazione_azione', self.gf('django.db.models.fields.related.ForeignKey')(related_name='progetto_set', db_column='classificazione_azione', to=orm['mct_progetti.ClassificazioneAzione'])),
        ))
        db.send_create_signal('mct_progetti', ['Progetto'])


    def backwards(self, orm):
        # Deleting model 'ClassificazioneQSN'
        db.delete_table('mct_progetti_classificazioneqsn')

        # Deleting model 'ProgrammaAsseObiettivo'
        db.delete_table('mct_progetti_programmaasseobiettivo')

        # Deleting model 'Tema'
        db.delete_table('mct_progetti_tema')

        # Deleting model 'Intesa'
        db.delete_table('mct_progetti_intesa')

        # Deleting model 'ClassificazioneAzione'
        db.delete_table('mct_progetti_classificazioneazione')

        # Deleting model 'Progetto'
        db.delete_table('mct_progetti_progetto')


    models = {
        'mct_progetti.classificazioneazione': {
            'Meta': {'object_name': 'ClassificazioneAzione'},
            'classificazione_superiore': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'classificazione_set'", 'db_column': "'classificazione_superiore'", 'default': 'None', 'to': "orm['mct_progetti.ClassificazioneAzione']", 'blank': 'True', 'null': 'True'}),
            'codice': ('django.db.models.fields.CharField', [], {'max_length': '8', 'primary_key': 'True'}),
            'descrizione': ('django.db.models.fields.TextField', [], {}),
            'tipo_classificazione': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        },
        'mct_progetti.classificazioneqsn': {
            'Meta': {'object_name': 'ClassificazioneQSN'},
            'classificazione_superiore': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'classificazione_set'", 'db_column': "'classificazione_superiore'", 'default': 'None', 'to': "orm['mct_progetti.ClassificazioneQSN']", 'blank': 'True', 'null': 'True'}),
            'codice': ('django.db.models.fields.CharField', [], {'max_length': '16', 'primary_key': 'True'}),
            'descrizione': ('django.db.models.fields.TextField', [], {}),
            'tipo_classificazione': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'mct_progetti.intesa': {
            'Meta': {'object_name': 'Intesa'},
            'codice': ('django.db.models.fields.CharField', [], {'max_length': '8', 'primary_key': 'True'}),
            'descrizione': ('django.db.models.fields.TextField', [], {})
        },
        'mct_progetti.progetto': {
            'Meta': {'object_name': 'Progetto'},
            'classificazione_azione': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'progetto_set'", 'db_column': "'classificazione_azione'", 'to': "orm['mct_progetti.ClassificazioneAzione']"}),
            'classificazione_qsn': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'progetto_set'", 'db_column': "'classificazione_qsn'", 'to': "orm['mct_progetti.ClassificazioneQSN']"}),
            'codice_locale': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True', 'db_column': "'cod_locale_progetto'"}),
            'cup': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'data_aggiornamento': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'fondo_comunitario': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'intesa_istituzionale': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'progetto_set'", 'db_column': "'intesa_istituzionale'", 'to': "orm['mct_progetti.Intesa']"}),
            'obiettivo_sviluppo': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'programma_asse_obiettivo': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'progetto_set'", 'db_column': "'programma_asse_progetto'", 'to': "orm['mct_progetti.ProgrammaAsseObiettivo']"}),
            'stato_dps': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'stato_fs': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'stato_fsc': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'tema': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'progetto_set'", 'db_column': "'tema'", 'to': "orm['mct_progetti.Tema']"}),
            'tipo_operazione': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'titolo_progetto': ('django.db.models.fields.TextField', [], {})
        },
        'mct_progetti.programmaasseobiettivo': {
            'Meta': {'object_name': 'ProgrammaAsseObiettivo'},
            'classificazione_superiore': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'classificazione_set'", 'db_column': "'classificazione_superiore'", 'default': 'None', 'to': "orm['mct_progetti.ProgrammaAsseObiettivo']", 'blank': 'True', 'null': 'True'}),
            'codice': ('django.db.models.fields.CharField', [], {'max_length': '32', 'primary_key': 'True'}),
            'descrizione': ('django.db.models.fields.TextField', [], {}),
            'tipo_classificazione': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'mct_progetti.tema': {
            'Meta': {'object_name': 'Tema'},
            'codice': ('django.db.models.fields.CharField', [], {'max_length': '16', 'primary_key': 'True'}),
            'descrizione': ('django.db.models.fields.TextField', [], {}),
            'tema_superiore': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tema_set'", 'db_column': "'tema_superiore'", 'default': 'None', 'to': "orm['mct_progetti.Tema']", 'blank': 'True', 'null': 'True'}),
            'tipo_tema': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        }
    }

    complete_apps = ['mct_progetti']