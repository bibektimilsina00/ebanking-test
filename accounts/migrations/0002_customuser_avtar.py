# Generated by Django 4.2.13 on 2024-06-28 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="avtar",
            field=models.ImageField(blank=True, null=True, upload_to="avatars/"),
        ),
    ]
