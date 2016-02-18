# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('treasure', '0002_auto_20160217_1406'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filesresource',
            name='path',
            field=models.FileField(upload_to='resources/%Y/%m/%d/34g/'),
        ),
    ]
