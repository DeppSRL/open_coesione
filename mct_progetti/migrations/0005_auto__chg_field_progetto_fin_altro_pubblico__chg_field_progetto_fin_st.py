# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Progetto.fin_altro_pubblico'
        db.alter_column('mct_progetti_progetto', 'fin_altro_pubblico', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=14, decimal_places=2))

        # Changing field 'Progetto.fin_stato_altri_provvedimenti'
        db.alter_column('mct_progetti_progetto', 'fin_stato_altri_provvedimenti', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=14, decimal_places=2))

        # Changing field 'Progetto.fin_ue'
        db.alter_column('mct_progetti_progetto', 'fin_ue', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=14, decimal_places=2))

        # Changing field 'Progetto.fin_stato_fsc'
        db.alter_column('mct_progetti_progetto', 'fin_stato_fsc', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=14, decimal_places=2))

        # Changing field 'Progetto.pagamento_fsc'
        db.alter_column('mct_progetti_progetto', 'pagamento_fsc', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=14, decimal_places=2))

        # Changing field 'Progetto.costo_ammesso'
        db.alter_column('mct_progetti_progetto', 'costo_ammesso', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=14, decimal_places=2))

        # Changing field 'Progetto.fin_stato_fondo_rotazione'
        db.alter_column('mct_progetti_progetto', 'fin_stato_fondo_rotazione', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=14, decimal_places=2))

        # Changing field 'Progetto.pagamento_ammesso'
        db.alter_column('mct_progetti_progetto', 'pagamento_ammesso', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=14, decimal_places=2))

        # Changing field 'Progetto.fin_stato_estero'
        db.alter_column('mct_progetti_progetto', 'fin_stato_estero', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=14, decimal_places=2))

        # Changing field 'Progetto.fin_totale'
        db.alter_column('mct_progetti_progetto', 'fin_totale', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=14, decimal_places=2))

        # Changing field 'Progetto.fin_provincia'
        db.alter_column('mct_progetti_progetto', 'fin_provincia', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=14, decimal_places=2))

        # Changing field 'Progetto.fin_da_reperire'
        db.alter_column('mct_progetti_progetto', 'fin_da_reperire', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=14, decimal_places=2))

        # Changing field 'Progetto.fin_privato'
        db.alter_column('mct_progetti_progetto', 'fin_privato', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=14, decimal_places=2))

        # Changing field 'Progetto.fin_comune'
        db.alter_column('mct_progetti_progetto', 'fin_comune', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=14, decimal_places=2))

        # Changing field 'Progetto.fin_regione'
        db.alter_column('mct_progetti_progetto', 'fin_regione', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=14, decimal_places=2))

        # Changing field 'Progetto.costo'
        db.alter_column('mct_progetti_progetto', 'costo', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=14, decimal_places=2))

        # Changing field 'Progetto.fin_totale_pubblico'
        db.alter_column('mct_progetti_progetto', 'fin_totale_pubblico', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=14, decimal_places=2))

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Progetto.fin_altro_pubblico'
        raise RuntimeError("Cannot reverse this migration. 'Progetto.fin_altro_pubblico' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Progetto.fin_stato_altri_provvedimenti'
        raise RuntimeError("Cannot reverse this migration. 'Progetto.fin_stato_altri_provvedimenti' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Progetto.fin_ue'
        raise RuntimeError("Cannot reverse this migration. 'Progetto.fin_ue' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Progetto.fin_stato_fsc'
        raise RuntimeError("Cannot reverse this migration. 'Progetto.fin_stato_fsc' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Progetto.pagamento_fsc'
        raise RuntimeError("Cannot reverse this migration. 'Progetto.pagamento_fsc' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Progetto.costo_ammesso'
        raise RuntimeError("Cannot reverse this migration. 'Progetto.costo_ammesso' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Progetto.fin_stato_fondo_rotazione'
        raise RuntimeError("Cannot reverse this migration. 'Progetto.fin_stato_fondo_rotazione' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Progetto.pagamento_ammesso'
        raise RuntimeError("Cannot reverse this migration. 'Progetto.pagamento_ammesso' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Progetto.fin_stato_estero'
        raise RuntimeError("Cannot reverse this migration. 'Progetto.fin_stato_estero' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Progetto.fin_totale'
        raise RuntimeError("Cannot reverse this migration. 'Progetto.fin_totale' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Progetto.fin_provincia'
        raise RuntimeError("Cannot reverse this migration. 'Progetto.fin_provincia' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Progetto.fin_da_reperire'
        raise RuntimeError("Cannot reverse this migration. 'Progetto.fin_da_reperire' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Progetto.fin_privato'
        raise RuntimeError("Cannot reverse this migration. 'Progetto.fin_privato' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Progetto.fin_comune'
        raise RuntimeError("Cannot reverse this migration. 'Progetto.fin_comune' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Progetto.fin_regione'
        raise RuntimeError("Cannot reverse this migration. 'Progetto.fin_regione' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Progetto.costo'
        raise RuntimeError("Cannot reverse this migration. 'Progetto.costo' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Progetto.fin_totale_pubblico'
        raise RuntimeError("Cannot reverse this migration. 'Progetto.fin_totale_pubblico' and its values cannot be restored.")

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
            'costo': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2'}),
            'costo_ammesso': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2'}),
            'cup': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'data_aggiornamento': ('django.db.models.fields.DateField', [], {'null': 'True'}),
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
            'obiettivo_sviluppo': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'pagamento_ammesso': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2'}),
            'pagamento_fsc': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '14', 'decimal_places': '2'}),
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