# Generated by Django 5.1.3 on 2024-11-09 06:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='roomservicerequest',
            name='service_type',
            field=models.CharField(choices=[('cleaning', 'Cleaning'), ('repair', 'Repair'), ('room_service', 'Room Service')], default=1, max_length=20),
            preserve_default=False,
        ),
    ]
