# Generated by Django 5.0 on 2024-01-05 09:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spotify_api', '0011_trackfeatures_image_url'),
    ]

    operations = [
        migrations.RenameField(
            model_name='trackfeatures',
            old_name='image_url',
            new_name='track_img',
        ),
    ]
