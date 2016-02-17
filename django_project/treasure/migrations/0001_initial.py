# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import geoposition.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Board',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=128)),
                ('boardtype', models.CharField(max_length=32, choices=[('resource', 'resource'), ('level', 'level'), ('general', 'general')])),
            ],
        ),
        migrations.CreateModel(
            name='EnglandPostcodes',
            fields=[
                ('Postcode', models.TextField(serialize=False, primary_key=True)),
                ('Latitude', models.FloatField()),
                ('Longitude', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='FilesResource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('path', models.FileField(upload_to='resources/%Y/%m/%d/16u/')),
            ],
        ),
        migrations.CreateModel(
            name='Hub',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('address', models.TextField()),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='NorthernIrelandPostcodes',
            fields=[
                ('Postcode', models.TextField(serialize=False, primary_key=True)),
                ('Latitude', models.FloatField()),
                ('Longitude', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Pack',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('explore', models.IntegerField()),
                ('name', models.CharField(max_length=128)),
                ('image', models.ImageField(null=True, upload_to='images/%Y/%m/%d', blank=True)),
                ('description', models.TextField()),
                ('summary', models.CharField(max_length=128)),
                ('hidden', models.IntegerField()),
                ('restricted', models.IntegerField()),
                ('datetime', models.DateTimeField()),
            ],
            options={
                'db_table': 'treasure_pack',
            },
        ),
        migrations.CreateModel(
            name='POI',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('position', geoposition.fields.GeopositionField(max_length=42)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime', models.DateTimeField()),
                ('content', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('tree', models.TextField()),
                ('description', models.TextField()),
                ('summary', models.CharField(max_length=128)),
                ('evolution_type', models.CharField(max_length=128)),
                ('evolution_explanation', models.TextField(null=True)),
                ('hidden', models.IntegerField()),
                ('restricted', models.IntegerField()),
                ('resource_type', models.CharField(max_length=128)),
                ('datetime', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('town', models.CharField(max_length=128)),
                ('address', models.TextField()),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='ScotlandPostcodes',
            fields=[
                ('Postcode', models.TextField(serialize=False, primary_key=True)),
                ('Latitude', models.FloatField()),
                ('Longitude', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('tagtype', models.CharField(max_length=1, choices=[('0', 'level'), ('1', 'topic'), ('2', 'other')])),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('firstname', models.CharField(max_length=128)),
                ('surname', models.CharField(max_length=128)),
                ('datetime', models.DateTimeField()),
                ('hubs', models.ManyToManyField(to='treasure.Hub', blank=True)),
                ('school', models.ForeignKey(blank=True, to='treasure.School', null=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TeacherDownloadsResource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('used', models.IntegerField()),
                ('datetime', models.DateTimeField()),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('rated', models.IntegerField()),
                ('resource', models.ForeignKey(to='treasure.Resource')),
                ('teacher', models.ForeignKey(to='treasure.Teacher')),
            ],
        ),
        migrations.CreateModel(
            name='TeacherRatesResource',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('measure1', models.CharField(max_length=128)),
                ('measure2', models.CharField(max_length=128)),
                ('measure3', models.CharField(max_length=128)),
                ('comment', models.TextField()),
                ('datetime', models.DateTimeField()),
                ('resource', models.ForeignKey(to='treasure.Resource')),
                ('teacher', models.ForeignKey(to='treasure.Teacher')),
            ],
        ),
        migrations.CreateModel(
            name='TeacherSubbedToBoard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('board', models.ForeignKey(to='treasure.Board')),
                ('teacher', models.ForeignKey(to='treasure.Teacher')),
            ],
        ),
        migrations.CreateModel(
            name='TeacherSubbedToThread',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('teacher', models.ForeignKey(to='treasure.Teacher')),
            ],
        ),
        migrations.CreateModel(
            name='TeacherWantstoTalkResource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.TextField()),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('datetime', models.DateTimeField()),
                ('disable', models.IntegerField()),
                ('resource', models.ForeignKey(to='treasure.Resource')),
                ('teacher', models.ForeignKey(to='treasure.Teacher')),
            ],
        ),
        migrations.CreateModel(
            name='Thread',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime', models.DateTimeField()),
                ('title', models.CharField(max_length=128)),
                ('content', models.TextField(null=True)),
                ('threadtype', models.CharField(max_length=1, choices=[('0', 'Rating'), ('1', 'Question'), ('2', 'Discuss')])),
                ('author', models.ForeignKey(to='treasure.Teacher')),
                ('board', models.ForeignKey(to='treasure.Board')),
                ('rating', models.OneToOneField(null=True, blank=True, to='treasure.TeacherRatesResource')),
            ],
        ),
        migrations.CreateModel(
            name='WalesPostcodes',
            fields=[
                ('Postcode', models.TextField(serialize=False, primary_key=True)),
                ('Latitude', models.FloatField()),
                ('Longitude', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='WebResource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField()),
                ('resource', models.OneToOneField(to='treasure.Resource')),
            ],
        ),
        migrations.AddField(
            model_name='teachersubbedtothread',
            name='thread',
            field=models.ForeignKey(to='treasure.Thread'),
        ),
        migrations.AddField(
            model_name='resource',
            name='author',
            field=models.ForeignKey(to='treasure.Teacher'),
        ),
        migrations.AddField(
            model_name='resource',
            name='packs',
            field=models.ManyToManyField(to='treasure.Pack', blank=True),
        ),
        migrations.AddField(
            model_name='resource',
            name='tags',
            field=models.ManyToManyField(to='treasure.Tag'),
        ),
        migrations.AddField(
            model_name='post',
            name='author',
            field=models.ForeignKey(to='treasure.Teacher'),
        ),
        migrations.AddField(
            model_name='post',
            name='thread',
            field=models.ForeignKey(to='treasure.Thread'),
        ),
        migrations.AddField(
            model_name='pack',
            name='author',
            field=models.ForeignKey(to='treasure.Teacher'),
        ),
        migrations.AddField(
            model_name='pack',
            name='tags',
            field=models.ManyToManyField(to='treasure.Tag'),
        ),
        migrations.AddField(
            model_name='filesresource',
            name='resource',
            field=models.OneToOneField(to='treasure.Resource'),
        ),
        migrations.AddField(
            model_name='board',
            name='resource',
            field=models.ForeignKey(blank=True, to='treasure.Resource', null=True),
        ),
    ]
