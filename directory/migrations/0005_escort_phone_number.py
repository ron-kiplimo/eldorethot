# Generated by Django 5.2 on 2025-05-03 22:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('directory', '0004_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='escort',
            name='phone_number',
            field=models.CharField(blank=True, help_text='Enter a valid phone number, e.g., +254712345678', max_length=20, null=True),
        ),
    ]
