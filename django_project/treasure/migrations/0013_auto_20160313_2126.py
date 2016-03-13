# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('treasure', '0012_teacherratespack_teacherwantstotalkpack'),
    ]

    operations = [
        migrations.AlterField(
            model_name='board',
            name='boardtype',
            field=models.CharField(max_length=32, choices=[('resource', 'resource'), ('level', 'level'), ('general', 'general'), ('pack', 'pack')]),
        ),
    ]
