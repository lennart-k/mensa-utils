# Generated by Django 2.0.4 on 2018-04-27 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('canteen', '0014_auto_20161209_2142'),
    ]

    operations = [
        migrations.AddField(
            model_name='canteen',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]