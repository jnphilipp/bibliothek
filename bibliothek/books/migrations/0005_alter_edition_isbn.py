# Generated by Django 4.0.1 on 2022-02-25 07:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("books", "0004_edition_persons"),
    ]

    operations = [
        migrations.AlterField(
            model_name="edition",
            name="isbn",
            field=models.CharField(
                blank=True, max_length=13, null=True, unique=True, verbose_name="ISBN"
            ),
        ),
    ]
