# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-24 09:52
from __future__ import unicode_literals

import bibliothek.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated at')),
                ('slug', models.SlugField(max_length=2048, unique=True, verbose_name='Slug')),
                ('name', bibliothek.fields.SingleLineTextField(unique=True, verbose_name='Name')),
            ],
            options={
                'verbose_name': 'Language',
                'ordering': ('name',),
                'verbose_name_plural': 'Languages',
            },
        ),
    ]
