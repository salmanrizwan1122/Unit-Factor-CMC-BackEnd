# Generated by Django 5.1.5 on 2025-01-23 13:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ufcmsdb', '0009_remove_user_groups_remove_user_is_active_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='user_name',
            new_name='username',
        ),
    ]
