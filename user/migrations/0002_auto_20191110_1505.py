# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2019-11-10 07:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='age',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='user',
            name='head',
            field=models.ImageField(default='../1.jpg', upload_to=''),
        ),
        migrations.AddField(
            model_name='user',
            name='sex',
            field=models.IntegerField(default=0),
        ),
    ]
