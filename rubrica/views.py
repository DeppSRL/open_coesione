# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, BadHeaderError, HttpResponse
from forms import NLContactForm


class NLContactView(TemplateView):
    """
    Handles the form to subscribe to the Newsletter.
    The form is a custom one, since fields are mapped to a set of three different model classes.
    """

    def get_context_data(self, **kwargs):
        return {
            'nl_form': NLContactForm() if self.request.method == 'GET' else NLContactForm(self.request.POST),
            'nl_form_submitted': self.request.GET.get('completed', '') == 'true'
        }

    def post(self, request, *args, **kwargs):
        form = NLContactForm(self.request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            try:
                # Process the data in form.cleaned_data
                form.execute()
            except BadHeaderError:
                return HttpResponse('Invalid header found.')

            return HttpResponseRedirect('{}?completed=true'.format(reverse('newsletter')))  # Redirect after POST

        return self.get(request, *args, **kwargs)
