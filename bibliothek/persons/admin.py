# -*- coding: utf-8 -*-

from django.contrib import admin
from django.db.models import Count
from django.forms import TextInput
from persons.models import Person, TextFieldSingleLine


class PersonAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return Person.objects.annotate(paper_count=Count('papers'))


    def show_paper_count(self, inst):
        return inst.paper_count


    list_display = ('last_name', 'first_name', 'show_paper_count', 'updated_at')
    readonly_fields = ('slug',)
    search_fields = ('last_name', 'first_name')
    show_paper_count.admin_order_field = 'paper_count'
    show_paper_count.short_description = 'Number of Papers'


    formfield_overrides = {
        TextFieldSingleLine: {'widget': TextInput(attrs={'autocomplete':'off'})},
    }

    fieldsets = [
        (None, {'fields': ['slug', 'first_name', 'last_name']}),
        ('Links', {'fields': ['links']}),
    ]

    filter_horizontal = ('links',)


admin.site.register(Person, PersonAdmin)
