# Generated by Django 3.2.5 on 2024-05-08 02:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authorisation', '0005_user_is_verified'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='uuid',
            field=models.UUIDField(),
        ),
    ]