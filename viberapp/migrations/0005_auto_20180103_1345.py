# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2018-01-03 10:45
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viberapp', '0004_auto_20180103_1342'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contacts',
            name='latGPS',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='contacts',
            name='longGPS',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='messagestatus',
            name='dtime',
            field=models.DateTimeField(default=datetime.datetime(2018, 1, 3, 13, 45, 39, 804135)),
        ),
    ]
