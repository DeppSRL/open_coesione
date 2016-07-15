# -*- coding: utf-8 -*-
from django.contrib import admin
from .models import Term


class TermAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('term',)}


admin.site.register(Term, TermAdmin)
