# Generated by Django 3.1.2 on 2020-10-24 12:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='place',
            name='times_visited',
        ),
    ]
