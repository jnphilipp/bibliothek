# -*- coding: utf-8 -*-

from django.contrib import admin
from django.db.models import Count
from django.forms import TextInput
from journals.models import Journal, TextFieldSingleLine


class JournalAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return Journal.objects.annotate(paper_count=Count('papers'))


    def show_paper_count(self, inst):
        return inst.paper_count


    list_display = ('name', 'show_paper_count', 'updated_at')
    readonly_fields = ('slug',)
    search_fields = ('name',)
    show_paper_count.admin_order_field = 'paper_count'
    show_paper_count.short_description = 'Number of Papers'


    formfield_overrides = {
        TextFieldSingleLine: {'widget': TextInput(attrs={'autocomplete':'off'})},
    }

    fieldsets = [
        (None, {'fields': ['slug', 'name']}),
        ('Links', {'fields': ['links']}),
    ]

    filter_horizontal = ('links',)


admin.site.register(Journal, JournalAdmin)
