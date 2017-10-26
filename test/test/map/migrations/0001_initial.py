# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-26 05:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Prob',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prob_id', models.IntegerField()),
                ('zipcode', models.CharField(max_length=5)),
                ('predicted_ems', models.FloatField()),
            ],
        ),
    ]
