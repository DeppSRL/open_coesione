from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django import forms
from django.http import QueryDict
from django.template.loader import render_to_string
from widgets.forms import WidgetForm


__author__ = 'daniele'


def dict_to_querydict(dictionary):
    query = QueryDict('', mutable=True)
    for key, val in dictionary.items():
        if isinstance(val, (set, list)):
            query.setlist(key, val)
        else:
            query.setdefault(key, val)
    return query


class Widget(object):

    code = None
    title = 'Widget'
    form_class = WidgetForm

    def __init__(self, request):
        super(Widget, self).__init__()
        self.request = request
        self.form = None

    def get_form_class(self):
        return self.form_class

    def build_form(self):
        form_class = self.get_form_class()
        if len(self.request.GET.items()) > 0:
            form = form_class(self.request.GET)
        else:
            form = form_class(self.get_defaults(), initial=self.get_initial())
        self.build_form_fields(form)
        return form

    def build_form_fields(self, form):
        form.fields['title'] = forms.CharField(label='Titolo', max_length=200)
        form.fields['height'] = forms.IntegerField(label='Altezza', min_value=100, initial=460, required=False)
        form.fields['width'] = forms.IntegerField(label='Larghezza', min_value=100, initial=400, required=False)

    def get_title(self):
        return self.title

    def get_initial(self):
        return {
            'title': self.get_title(),
            'height': 460,
            'width': 400
        }

    def get_defaults(self):
        return dict_to_querydict(self.get_initial())

    def get_form(self):
        if self.form is None:
            self.form = self.build_form()
        return self.form

    def get_embed_code(self):
        form = self.get_form()
        if form.is_bound and not form.is_valid():
            return ''
        data = {}
        for key, val in form.cleaned_data.items():
            if isinstance(val, (list, set)):
                if not key.endswith('_set'):
                    raise ImproperlyConfigured("Multi value form field '{0}.{1}' "
                                               "needs a name with '_set' as suffix.".format(self.__class__, key))
                val = ",".join(val)
            elif isinstance(val, bool):
                val = int(val)
            data[key] = val
        return render_to_string('widgets/embed_code.html', {'widget': self, 'data': data})

    def get_template_name(self):
        if hasattr(self, 'template_name'):
            return self.template_name
        return "widgets/{0}_widget.html".format(self.code)

    def get_context_data(self):
        params = {}
        if self.get_form().is_valid():
            params = self.get_form().cleaned_data
        data = {
            'widget': self,
            'params': params
        }
        return data

    def render(self):
        return render_to_string(self.get_template_name(), self.get_context_data())

    def get_absolute_url(self):
        return reverse('widgets-detail', kwargs={'widget': self.code})