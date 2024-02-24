# Generated by Django 5.0 on 2024-02-24 12:57

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('spotify_api', '0012_rename_image_url_trackfeatures_track_img'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserInterestedTracks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('track_id', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='spotify_api.trackfeatures', verbose_name='Track ID')),
                ('username', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('username', 'track_id')},
            },
        ),
        migrations.CreateModel(
            name='UserLikedTracks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('track_id', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='spotify_api.trackfeatures', verbose_name='Track ID')),
                ('username', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('username', 'track_id')},
            },
        ),
        migrations.CreateModel(
            name='UserPlaylists',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('playlist_name', models.CharField(max_length=255, verbose_name='Playlist Name')),
                ('username', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Username')),
            ],
            options={
                'unique_together': {('username', 'playlist_name')},
            },
        ),
        migrations.CreateModel(
            name='UserTrackPlaylist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('playlist_name', models.CharField(max_length=255, verbose_name='Playlist Name')),
                ('track_id', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='spotify_api.trackfeatures', verbose_name='Track ID')),
                ('username', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('username', 'playlist_name', 'track_id')},
            },
        ),
    ]
