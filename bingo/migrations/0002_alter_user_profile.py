# Generated by Django 5.1.6 on 2025-02-22 19:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bingo", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="profile",
            field=models.CharField(default="Player", max_length=20),
        ),
    ]
