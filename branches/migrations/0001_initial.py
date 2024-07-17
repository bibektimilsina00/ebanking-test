# Generated by Django 4.2.13 on 2024-07-17 07:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('organizations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('available_accounts', models.CharField(blank=True, max_length=1000, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('member_number', models.CharField(blank=True, max_length=255)),
                ('created_by', models.ForeignKey(limit_choices_to={'role': 'organization'}, on_delete=django.db.models.deletion.CASCADE, related_name='created_branches', to=settings.AUTH_USER_MODEL)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='branches', to='organizations.organization')),
                ('owner', models.ForeignKey(blank=True, limit_choices_to={'role': 'branch'}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='branches', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
