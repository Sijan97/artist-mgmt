# Generated by Django 5.0.3 on 2024-03-12 07:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='musicartists',
            old_name='artistprofile_id',
            new_name='artistprofile',
        ),
        migrations.RenameField(
            model_name='musicartists',
            old_name='music_id',
            new_name='music',
        ),
    ]
