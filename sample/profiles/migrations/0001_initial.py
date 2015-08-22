# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('family_name', models.CharField(max_length=20, verbose_name='Family Name')),
                ('first_name', models.CharField(max_length=20, verbose_name='First Name')),
                ('birth_year', models.IntegerField(default=None, null=True, verbose_name='Birth Year', blank=True)),
                ('birth_month', models.IntegerField(default=None, null=True, verbose_name='Birth Month', blank=True)),
                ('birth_day', models.IntegerField(default=None, null=True, verbose_name='Birth Day', blank=True)),
                ('gender', models.IntegerField(default=0, verbose_name='Gender', choices=[(0, 'Gender N/A'), (1, 'Gender Female'), (2, 'Gender Male')])),
                ('user', models.ForeignKey(verbose_name='System User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Profile',
                'verbose_name_plural': 'Profile',
            },
        ),
    ]
