# Generated by Django 4.1.12 on 2023-10-10 11:33

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("trains", "0002_alter_ticketreservation_to_date"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="ticketreservation",
            name="to_date",
        ),
    ]
