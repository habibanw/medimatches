# Generated by Django 5.0.1 on 2024-02-24 15:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0002_alter_customuser_managers_remove_customuser_username_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='provider',
            old_name='hospital',
            new_name='facility_name',
        ),
    ]
