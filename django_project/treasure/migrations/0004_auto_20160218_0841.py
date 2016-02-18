# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('treasure', '0003_auto_20160218_0717'),
    ]

    operations = [
        migrations.AddField(
            model_name='board',
            name='restricted',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='teacher',
            name='verified',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='thread',
            name='restricted',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='filesresource',
            name='path',
            field=models.FileField(upload_to='resources/%Y/%m/%d/11a/'),
        ),
    ]
