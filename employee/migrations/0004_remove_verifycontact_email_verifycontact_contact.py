# Generated by Django 4.1.7 on 2023-03-09 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("employee", "0003_auto_20230309_1241"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="verifycontact",
            name="Email",
        ),
        migrations.AddField(
            model_name="verifycontact",
            name="contact",
            field=models.CharField(default="N/A", max_length=15),
        ),
    ]
