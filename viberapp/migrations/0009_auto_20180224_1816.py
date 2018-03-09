# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2018-02-24 15:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viberapp', '0008_auto_20180105_0045'),
    ]

    operations = [
        migrations.DeleteModel(
            name='accounts',
        ),
        migrations.DeleteModel(
            name='messages',
        ),
        migrations.DeleteModel(
            name='messagestatus',
        ),
        migrations.DeleteModel(
            name='telegrammchatid',
        ),
        migrations.DeleteModel(
            name='viberid',
        ),
        migrations.AlterField(
            model_name='accountlinktoid',
            name='lschet',
            field=models.CharField(max_length=24, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='sessionstate',
            name='id',
            field=models.CharField(max_length=24, primary_key=True, serialize=False),
        ),
    ]
