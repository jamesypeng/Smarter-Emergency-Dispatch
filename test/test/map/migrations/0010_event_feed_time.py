# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-02 03:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('map', '0009_auto_20171201_1905'),
    ]

    operations = [
        migrations.AddField(
            model_name='event_feed',
            name='time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]