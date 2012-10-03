# coding=utf-8
from django.db import models

class ContactMessage(models.Model):

    REASON_CHOICES = (
        (u'', u'--------------'),
        (1, u'domanda sui dati'),
        (2, u'domanda sul sito'),
        (3, u'esempio di riuso: applicazioni'),
        (4, u'esempio di riuso: visualizzazioni'),
        (5, u'esempio di riuso: analisi'),
        (6, u'segnalazione errore nei dati'),
        (7, u'segnalazione relativa a un progetto'),
        (8, u'suggerimenti e consigli'),
    )

    sender = models.CharField(max_length= 50, verbose_name='Autore')
    email = models.EmailField()
    organization = models.CharField(max_length= 100, verbose_name='Organizzazione')
    location = models.CharField(max_length=300, verbose_name='Luogo')
    reason = models.CharField(choices=REASON_CHOICES, max_length=1, verbose_name='Motivo del contatto')

    body = models.TextField( verbose_name='Messaggio' )

    sent_at = models.DateTimeField( auto_now_add=True, verbose_name="Data di invio" )

    class Meta:
        verbose_name_plural = "Messaggi"
        verbose_name = "Messaggio"

