# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-25 18:48
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('canteen', '0004_auto_20161124_2043'),
    ]

    operations = [
        migrations.CreateModel(
            name='InofficialDeprecation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reporter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deprecation_reports', to=settings.AUTH_USER_MODEL)),
                ('serving', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='deprecation_reports', to='canteen.Serving')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='inofficialdeprecation',
            unique_together=set([('serving', 'reporter')]),
        ),
    ]
