# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('treasure', '0014_auto_20160313_2312'),
    ]

    operations = [
        migrations.AddField(
            model_name='thread',
            name='rating_pack',
            field=models.OneToOneField(null=True, blank=True, to='treasure.TeacherRatesPack'),
        ),
        migrations.AlterField(
            model_name='thread',
            name='rating',
            field=models.OneToOneField(null=True, blank=True, to='treasure.TeacherRatesResource'),
        ),
    ]
