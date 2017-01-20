# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-05 20:47
from __future__ import unicode_literals

from django.db import migrations, models
import persons.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('links', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('slug', models.SlugField(max_length=2048, unique=True)),
                ('first_name', persons.models.TextFieldSingleLine()),
                ('last_name', persons.models.TextFieldSingleLine(blank=True, null=True)),
                ('links', models.ManyToManyField(blank=True, related_name='persons', to='links.Link')),
            ],
            options={
                'ordering': ('last_name', 'first_name'),
            },
        ),
        migrations.AlterUniqueTogether(
            name='person',
            unique_together=set([('last_name', 'first_name')]),
        ),
    ]
