# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2018-01-04 21:45
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viberapp', '0007_auto_20180103_1418'),
    ]

    operations = [
        migrations.CreateModel(
            name='QueueReceipt',
            fields=[
                ('chatid', models.CharField(max_length=24, primary_key=True, serialize=False)),
                ('ls', models.CharField(max_length=10)),
                ('datetime', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('month', models.DateField()),
                ('ready', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Receipt',
            fields=[
                ('chatid', models.CharField(max_length=24, primary_key=True, serialize=False)),
                ('ls', models.CharField(max_length=10)),
                ('file_id', models.DateTimeField(max_length=10)),
                ('datetime', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('month', models.DateField()),
            ],
        ),
        migrations.AlterField(
            model_name='messagestatus',
            name='dtime',
            field=models.DateTimeField(default=datetime.datetime(2018, 1, 5, 0, 45, 11, 46462)),
        ),
        migrations.AlterField(
            model_name='tokentosnapping',
            name='lschet',
            field=models.IntegerField(primary_key=True),
        ),
    ]
