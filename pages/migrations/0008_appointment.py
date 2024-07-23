# Generated by Django 5.0.1 on 2024-03-06 01:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0007_feedback'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField()),
                ('type', models.CharField(blank=True, choices=[('new patient', 'New Patient'), ('follow up', 'Follow Up'), ('new condition', 'New Condition')], max_length=100)),
                ('canceled', models.BooleanField(default=False)),
                ('canceled_reason', models.TextField(blank=True, null=True)),
                ('patient_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='patient', to=settings.AUTH_USER_MODEL)),
                ('provider_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='provider', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
