# Generated by Django 4.1.2 on 2022-10-18 18:06

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("employee_finder_api", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(model_name="employees", name="data",),
        migrations.AddField(
            model_name="employees",
            name="date",
            field=models.DateTimeField(
                default=datetime.datetime(2022, 10, 18, 21, 6, 46, 821980)
            ),
        ),
    ]
