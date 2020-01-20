# Generated by Django 2.2.6 on 2020-01-13 13:53

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meal',
            name='gihoType',
            field=models.IntegerField(blank=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)]),
        ),
    ]
