# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Progetto.fin_totale'
        db.add_column('mct_progetti_progetto', 'fin_totale',
                      self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=14, decimal_places=2),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Progetto.fin_totale'
        db.delete_column('mct_progetti_progetto', 'fin_totale')


    models = {
        'mct_progetti.classificazioneazione': {
            'Meta': {'object_name': 'ClassificazioneAzione'},
            'classificazione_superiore': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'classificazione_set'", 'db_column': "'classificazione_superiore'", 'default': 'None', 'to': "orm['mct_progetti.ClassificazioneAzione']", 'blank': 'True', 'null': 'True'}),
            'codice': ('django.db.models.fields.CharField', [], {'max_length': '8', 'primary_key': 'True'}),
            'descrizione': ('django.db.models.fields.TextField', [], {}),
            'tipo_classificazione': ('django.db.models.fields.CharField', [], {'max_length': '16'})
        },
        'mct_progetti.classificazioneoggetto': {
            'Meta': {'object_name': 'ClassificazioneOggetto'},
            'classificazione_superiore': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'classificazione_set'", 'db_column': "'classificazione_superiore'", 'default': 'None', 'to': "orm['mct_progetti.ClassificazioneOggetto']", 'blank': 'True', 'null': 'True'}),
            'codice': ('django.db.models.fields.CharField', [], {'max_length': '16', 'primary_key': 'True'}),
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
            'classificazione_oggetto': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'progetto_set'", 'db_column': "'classificazione_oggetto'", 'to': "orm['mct_progetti.ClassificazioneOggetto']"}),
            'classificazione_qsn': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'progetto_set'", 'db_column': "'classificazione_qsn'", 'to': "orm['mct_progetti.ClassificazioneQSN']"}),
            'codice_locale': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True', 'db_column': "'cod_locale_progetto'"}),
            'cup': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'data_aggiornamento': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'fin_totale': ('django.db.models.fields.DecimalField', [], {'max_digits': '14', 'decimal_places': '2'}),
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