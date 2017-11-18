# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-09 06:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ambulance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amb_id', models.IntegerField()),
                ('LAT', models.FloatField()),
                ('LONG', models.FloatField()),
                ('AVAILABLE', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='EMS_Calls',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('LAT', models.FloatField()),
                ('LONG', models.FloatField()),
                ('time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Predictions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('zcta', models.CharField(max_length=5)),
                ('year', models.IntegerField()),
                ('month', models.IntegerField()),
                ('day_of_month', models.IntegerField()),
                ('hour_of_day', models.IntegerField()),
                ('day_of_year', models.IntegerField()),
                ('week_of_year', models.IntegerField()),
                ('day_of_week', models.IntegerField()),
                ('is_weekend', models.BooleanField()),
                ('Call_counts', models.FloatField()),
            ],
        ),
        migrations.DeleteModel(
            name='Prob',
        ),
    ]