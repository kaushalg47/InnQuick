# Generated by Django 5.1.3 on 2025-03-08 11:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('rooms', '0004_room_qr_code'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('price', models.DecimalField(decimal_places=2, max_digits=6)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='menu', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Completed', 'Completed')], default='Pending', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rooms.room')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField()),
                ('menu_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='menu.menuitem')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='menu.order')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='items',
            field=models.ManyToManyField(through='menu.OrderItem', to='menu.menuitem'),
        ),
    ]
