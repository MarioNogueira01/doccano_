# Generated by Django 4.0.4 on 2022-06-30 02:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("labels", "0015_create_boundingbox_table"),
        ("data_export", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ExportedBoundingBox",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("labels.boundingbox",),
        ),
    ]
