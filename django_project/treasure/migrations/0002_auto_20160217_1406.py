# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('treasure', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filesresource',
            name='path',
            field=models.FileField(upload_to='resources/%Y/%m/%d/15b/'),
        ),
    ]
