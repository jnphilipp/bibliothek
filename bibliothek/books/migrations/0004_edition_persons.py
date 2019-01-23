# Generated by Django 2.1.1 on 2018-09-20 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('persons', '0001_initial'),
        ('books', '0003_edition_links'),
    ]

    operations = [
        migrations.AddField(
            model_name='edition',
            name='persons',
            field=models.ManyToManyField(blank=True, related_name='editions', to='persons.Person', verbose_name='Persons'),
        ),
    ]