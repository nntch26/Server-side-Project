# Generated by Django 4.2.16 on 2024-10-16 03:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boardgame', '0008_playsession_created_at_alter_playsession_end_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='boardgames',
            name='status',
            field=models.CharField(choices=[('Available', 'Available'), ('Reserved', 'Reserved')], default='Available', max_length=15),
        ),
    ]
