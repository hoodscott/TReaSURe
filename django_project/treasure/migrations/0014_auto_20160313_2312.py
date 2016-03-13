# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('treasure', '0013_auto_20160313_2126'),
    ]

    operations = [
        migrations.AddField(
            model_name='board',
            name='pack',
            field=models.ForeignKey(blank=True, to='treasure.Pack', null=True),
        ),
        migrations.AlterField(
            model_name='thread',
            name='rating',
            field=models.OneToOneField(null=True, blank=True, to='treasure.TeacherRatesPack'),
        ),
    ]
