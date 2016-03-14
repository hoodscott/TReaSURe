# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('treasure', '0015_auto_20160313_2319'),
    ]

    operations = [
        migrations.AddField(
            model_name='pendingverification',
            name='evidence',
            field=models.TextField(default='no evidence given'),
        ),
    ]
