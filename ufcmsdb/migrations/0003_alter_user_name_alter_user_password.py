# Generated by Django 5.1.5 on 2025-01-20 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ufcmsdb', '0002_rename_roles_user_role_alter_user_cnicno'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='name',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(max_length=200),
        ),
    ]
