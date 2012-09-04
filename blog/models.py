from datetime import datetime
from django.db import models

class Entry(models.Model):

    title= models.CharField(max_length=255)
    body= models.TextField()
    body_plain= models.TextField()
    published_at= models.DateTimeField(auto_now_add=True)
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.title

    class Meta():
        ordering= ['-published_at']


class Blog(object):

    @staticmethod
    def get_latest_entries(qnt=10, end_date=None, start_date=None, single=False):
        end_date = end_date or datetime.now()
        qnt = qnt if not single else 1

        if start_date:
            entries = Entry.objects.filter(published_at__range=(start_date, end_date))[:qnt]
        else :
            entries = Entry.objects.filter(published_at__lte=end_date)[:qnt]

        if single :
            return entries[0] if entries else None

        return entries

