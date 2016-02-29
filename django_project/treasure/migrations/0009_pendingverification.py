# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('treasure', '0008_help'),
    ]

    operations = [
        migrations.CreateModel(
            name='pendingVerification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reviewed', models.IntegerField()),
                ('datetimeOfRequest', models.DateTimeField()),
                ('datetimeOfReview', models.DateTimeField(null=True, blank=True)),
                ('teacher', models.ForeignKey(to='treasure.Teacher')),
            ],
        ),
    ]
