# Generated by Django 4.2.13 on 2024-06-17 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0008_rename_baseurl_organization_base_url_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="branch",
            name="available_accounts",
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
