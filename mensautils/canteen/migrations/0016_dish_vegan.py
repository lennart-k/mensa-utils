# Generated by Django 2.1 on 2018-08-09 20:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('canteen', '0015_canteen_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='dish',
            name='vegan',
            field=models.BooleanField(default=False),
            preserve_default=False
        ),
    ]
