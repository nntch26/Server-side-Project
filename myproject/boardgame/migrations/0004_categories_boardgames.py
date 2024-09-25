# Generated by Django 4.2.16 on 2024-09-25 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boardgame', '0003_userdetail_birth_date_userdetail_gender_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Categories',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='BoardGames',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('min_players', models.IntegerField()),
                ('max_players', models.IntegerField(blank=True, null=True)),
                ('play_time', models.IntegerField()),
                ('image', models.FileField(upload_to='upload')),
                ('video_url', models.URLField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('category', models.ManyToManyField(to='boardgame.categories')),
            ],
        ),
    ]
