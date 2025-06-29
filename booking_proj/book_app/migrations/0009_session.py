# Generated by Django 5.2.2 on 2025-06-08 16:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book_app', '0008_rename_sessionday_serviceday_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveIntegerField()),
                ('appointment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='book_app.appointment')),
            ],
        ),
    ]
