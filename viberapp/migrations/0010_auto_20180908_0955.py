# Generated by Django 2.1.1 on 2018-09-08 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viberapp', '0009_auto_20180224_1816'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tokentosnapping',
            name='messanger',
            field=models.CharField(default='telegram', max_length=24),
        ),
    ]