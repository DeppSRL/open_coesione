# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Soggetto'
        db.create_table('mct_progetti_soggetto', (
            ('codice_fiscale', self.gf('django.db.models.fields.CharField')(max_length=16, primary_key=True)),
            ('denominazione', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ruolo', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('mct_progetti', ['Soggetto'])


        # Changing field 'Localizzazione.indirizzo'
        db.alter_column('mct_progetti_localizzazione', 'indirizzo', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))
        # Adding M2M table for field soggetto_set on 'Progetto'
        db.create_table('mct_progetti_progetto_soggetto_set', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('progetto', models.ForeignKey(orm['mct_progetti.progetto'], null=False)),
            ('soggetto', models.ForeignKey(orm['mct_progetti.soggetto'], null=False))
        ))
        db.create_unique('mct_progetti_progetto_soggetto_set', ['progetto_id', 'soggetto_id'])


    def backwards(self, orm):
        # Deleting model 'Soggetto'
        db.delete_table('mct_progetti_soggetto')


        # Changing field 'Localizzazione.indirizzo'
        db.alter_column('mct_progetti_localizzazione', 'indirizzo', self.gf('django.db.models.fields.CharField')(max_length=64, null=True))
        # Removing M2M table for field soggetto_set on 'Progetto'
        db.delete_table('mct_progetti_progetto_soggetto_set')


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
        'mct_progetti.localita': {
            'Meta': {'object_name': 'Localita'},
            'codice': ('django.db.models.fields.CharField', [], {'max_length': '16', 'primary_key': 'True'}),
            'denominazione': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'territorio': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        'mct_progetti.localizzazione': {
            'Meta': {'object_name': 'Localizzazione'},
            'cap': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'dps_flag_cap': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'indirizzo': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'localita': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mct_progetti.Localita']", 'db_column': "'codice_localita'"}),
            'progetto': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mct_progetti.Progetto']", 'db_column': "'codice_progetto'"})
        },
        'mct_progetti.progetto': {
            'Meta': {'object_name': 'Progetto'},
            'classificazione_azione': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'progetto_set'", 'db_column': "'classificazione_azione'", 'to': "orm['mct_progetti.ClassificazioneAzione']"}),
            'classificazione_oggetto': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'progetto_set'", 'db_column': "'classificazione_oggetto'", 'to': "orm['mct_progetti.ClassificazioneOggetto']"}),
            'classificazione_qsn': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'progetto_set'", 'db_column': "'classificazione_qsn'", 'to': "orm['mct_progetti.ClassificazioneQSN']"}),
            'codice_locale': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True', 'db_column': "'cod_locale_progetto'"}),
            'costo': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2'}),
            'costo_ammesso': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2'}),
            'cup': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'data_aggiornamento': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'data_fine_effettiva': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'data_fine_prevista': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'data_inizio_effettiva': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'data_inizio_info': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'data_inizio_prevista': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'dps_date': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'dps_flag_cup': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'dps_flag_date_effettive': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'dps_flag_date_previste': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'fin_altro_pubblico': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2'}),
            'fin_comune': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2'}),
            'fin_da_reperire': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2'}),
            'fin_privato': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2'}),
            'fin_provincia': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2'}),
            'fin_regione': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2'}),
            'fin_stato_altri_provvedimenti': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2'}),
            'fin_stato_estero': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2'}),
            'fin_stato_fondo_rotazione': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2'}),
            'fin_stato_fsc': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2'}),
            'fin_totale': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2'}),
            'fin_totale_pubblico': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2'}),
            'fin_ue': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2'}),
            'fondo_comunitario': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'intesa_istituzionale': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'progetto_set'", 'db_column': "'intesa_istituzionale'", 'to': "orm['mct_progetti.Intesa']"}),
            'localita_set': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['mct_progetti.Localita']", 'through': "orm['mct_progetti.Localizzazione']", 'symmetrical': 'False'}),
            'obiettivo_sviluppo': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'pagamento': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2'}),
            'pagamento_ammesso': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2'}),
            'pagamento_fsc': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2'}),
            'programma_asse_obiettivo': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'progetto_set'", 'db_column': "'programma_asse_progetto'", 'to': "orm['mct_progetti.ProgrammaAsseObiettivo']"}),
            'soggetto_set': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['mct_progetti.Soggetto']", 'symmetrical': 'False'}),
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
        'mct_progetti.soggetto': {
            'Meta': {'object_name': 'Soggetto'},
            'codice_fiscale': ('django.db.models.fields.CharField', [], {'max_length': '16', 'primary_key': 'True'}),
            'denominazione': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'ruolo': ('django.db.models.fields.CharField', [], {'max_length': '1'})
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