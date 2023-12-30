# Generated by Django 5.0 on 2023-12-27 11:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_tracks', '0002_userplaylists_alter_usertrackplaylist_playlist_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='userplaylists',
            name='username',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Username'),
        ),
        migrations.AlterField(
            model_name='usertrackplaylist',
            name='playlist_name',
            field=models.ForeignKey(default='playlist', on_delete=django.db.models.deletion.CASCADE, to='user_tracks.userplaylists', verbose_name='Playlist Name'),
        ),
    ]