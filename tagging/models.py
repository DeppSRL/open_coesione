from django.db import models
from django_extensions.db.fields import AutoSlugField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

class Tag(models.Model):
    name = models.CharField(max_length=100, verbose_name='Termine')
    slug = AutoSlugField(populate_from='name')

    def __unicode__(self):
        return self.name

class TaggedItem(models.Model):
    tag = models.ForeignKey(Tag, related_name='tagged_items')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()

    class Meta:
        verbose_name = 'Tag'

class ModelTagManager(models.Manager):
    def get_query_set(self):
        ctype = ContentType.objects.get_for_model(self.model)
        return Tag.objects.filter(tagged_items__content_type=ctype).distinct()

class TagMixin(models.Model):
    tagged_items = generic.GenericRelation(TaggedItem)
    objects = models.Manager()
    model_tags = ModelTagManager()

    def tags(self):
        tag_ids = []
        for tagged_item in self.tagged_items.all():
            tag_ids.append(tagged_item.tag_id)
        return Tag.objects.filter(id__in=tag_ids)

    class Meta:
        abstract = True
