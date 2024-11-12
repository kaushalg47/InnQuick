# Generated by Django 5.1.3 on 2024-11-06 19:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='roomservicerequest',
            old_name='requested_at',
            new_name='created_at',
        ),
        migrations.RemoveField(
            model_name='room',
            name='name',
        ),
        migrations.RemoveField(
            model_name='room',
            name='room_number',
        ),
        migrations.AddField(
            model_name='room',
            name='number',
            field=models.CharField(default=0, max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='room',
            name='url',
            field=models.CharField(default=0, max_length=255, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='roomservicerequest',
            name='is_serviced',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='roomservicerequest',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rooms.room'),
        ),
    ]
