# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('treasure', '0011_auto_20160229_1958'),
    ]

    operations = [
        migrations.CreateModel(
            name='TeacherRatesPack',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('measure1', models.CharField(max_length=128)),
                ('measure2', models.CharField(max_length=128)),
                ('measure3', models.CharField(max_length=128)),
                ('comment', models.TextField()),
                ('datetime', models.DateTimeField()),
                ('pack', models.ForeignKey(to='treasure.Pack')),
                ('teacher', models.ForeignKey(to='treasure.Teacher')),
            ],
        ),
        migrations.CreateModel(
            name='TeacherWantstoTalkPack',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.TextField()),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('datetime', models.DateTimeField()),
                ('disable', models.IntegerField()),
                ('pack', models.ForeignKey(to='treasure.Pack')),
                ('teacher', models.ForeignKey(to='treasure.Teacher')),
            ],
        ),
    ]
