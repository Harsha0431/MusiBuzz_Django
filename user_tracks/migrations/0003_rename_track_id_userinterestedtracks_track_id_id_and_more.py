# Generated by Django 5.0 on 2024-02-24 13:14

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spotify_api', '0012_rename_image_url_trackfeatures_track_img'),
        ('user_tracks', '0002_alter_userinterestedtracks_track_id'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name='userinterestedtracks',
            old_name='track_id',
            new_name='track_id_id',
        ),
        migrations.AlterUniqueTogether(
            name='userinterestedtracks',
            unique_together={('username', 'track_id_id')},
        ),
    ]
