# Generated by Django 5.2.2 on 2025-06-12 12:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book_app', '0014_alter_timeslot_service'),
    ]

    operations = [
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('appointment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='book_app.appointment')),
            ],
        ),
    ]
