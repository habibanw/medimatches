# Generated by Django 5.0.1 on 2024-03-06 01:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0009_alter_appointment_canceled'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='canceled',
            field=models.BooleanField(default=False),
        ),
    ]
