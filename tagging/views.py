class TagFilterMixin(object):
    model = None

    def _get_tag_filter_value(self):
        return self.request.GET.get('tag', None)

    def _apply_tag_filter(self, qs):
        filter_value = self._get_tag_filter_value()
        if filter_value is not None:
            qs = qs.filter(tagged_items__tag__slug=filter_value)
        return qs

    def _get_tag_choices(self):
        choices = []
        if self.model is not None:
            for used_tag in self.model.model_tags.all():
                choices.append(
                    {
                        'name': used_tag.name,
                        'param': used_tag.slug,
                        'selected': used_tag.slug == self._get_tag_filter_value()
                    }
                )
        return choices
