# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('treasure', '0009_pendingverification'),
    ]

    operations = [
        migrations.AddField(
            model_name='pendingverification',
            name='reviewer',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
