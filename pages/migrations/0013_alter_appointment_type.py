# Generated by Django 5.0.1 on 2024-03-10 20:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0012_alter_appointment_patient_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='type',
            field=models.CharField(blank=True, choices=[('NEW_PATIENT', 'new patient'), ('FOLLOW_UP', 'follow up'), ('NEW_COND', 'new condition')], max_length=100),
        ),
    ]
