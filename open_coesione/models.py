# coding=utf-8
from django.db import models

class ContactMessage(models.Model):

    REASON_CHOICES = (
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

class PressReview(models.Model):

    title = models.CharField(max_length=200, verbose_name='Titolo')
    source = models.CharField(max_length=200, verbose_name='Fonte')
    author = models.CharField(max_length=200, verbose_name='Autore')

    file = models.FileField(upload_to='press', blank=True, null=True)
    url = models.URLField(blank=True, null=True)

    published_at = models.DateField(verbose_name='Data di pubblicazione')

    class Meta:
        verbose_name_plural = "Rassegna stampa"
        verbose_name = "Articolo"


class Pillola(models.Model):

    title = models.CharField(max_length=200, verbose_name='Titolo')
    description = models.TextField(max_length=1024, verbose_name='Descrizione', blank=True, null=True)
    file = models.FileField(upload_to='pillole', blank=True, null=True)

    published_at = models.DateField(verbose_name='Data di pubblicazione')

    class Meta:
        verbose_name_plural = "Pillole"
        verbose_name = "Pillola"
