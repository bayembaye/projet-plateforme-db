# Generated by Django 5.1.7 on 2025-04-19 23:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plagiarism', '0002_alter_plagiarismscan_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plagiarismscan',
            name='similarity_score',
            field=models.FloatField(default=0.0),
        ),
    ]
