# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('treasure', '0004_auto_20160218_0841'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filesresource',
            name='path',
            field=models.FileField(upload_to='resources/%Y/%m/%d/23i/'),
        ),
    ]
