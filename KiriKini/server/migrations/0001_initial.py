# Generated by Django 2.2.6 on 2019-10-30 14:47

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Meal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('countType', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('mealType', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(3)])),
                ('gihoType', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('picURL', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('name', models.CharField(max_length=20)),
                ('token', models.CharField(max_length=255)),
                ('accessToken', models.CharField(max_length=255)),
                ('refreshToken', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('countType', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('feedback', models.TextField()),
                ('analysis', models.TextField()),
                ('createdAt', models.DateField(auto_now_add=True)),
                ('userId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='server.User')),
            ],
        ),
        migrations.CreateModel(
            name='MealRate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)])),
                ('mealId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='server.Meal')),
                ('userId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='server.User')),
            ],
        ),
        migrations.AddField(
            model_name='meal',
            name='userId',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='server.User'),
        ),
    ]
