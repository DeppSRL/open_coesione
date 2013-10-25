from django.core.urlresolvers import reverse
from django import forms
from django.template.loader import render_to_string


__author__ = 'daniele'


class Widget(object):

    code = None

    def __init__(self, request):
        super(Widget, self).__init__()
        self.request = request
        self.form = None

    def build_form(self):
        if len(self.request.GET.items()) > 0:
            form = forms.Form(self.request.GET)
        else:
            form = forms.Form()
        form.fields['title'] = forms.CharField(required=False)
        form.fields['height'] = forms.IntegerField(initial=400, min_value=300, max_value=768, required=False)
        form.fields['width'] = forms.IntegerField(initial=460, min_value=300, max_value=1024, required=False)
        return form

    def get_form(self):
        if self.form is None:
            self.form = self.build_form()
        return self.form

    def get_embed_code(self):
        if self.form.is_bound and not self.form.is_valid():
            return ''
        return render_to_string('widgets/embed_code.html', {'widget': self})

    def get_template_name(self):
        if hasattr(self, 'template_name'):
            return self.template_name
        return "widgets/{0}_widget.html".format(self.code)

    def get_context_data(self):
        data = {
            'widget': self,
            'params': self.request.GET
        }
        return data

    def render(self):
        return render_to_string(self.get_template_name(), self.get_context_data())

    def get_absolute_url(self):
        return reverse('widgets-detail', kwargs={'widget': self.code})