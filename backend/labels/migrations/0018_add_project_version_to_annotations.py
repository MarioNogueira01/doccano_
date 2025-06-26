# Generated manually for adding project_version to annotation models

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("labels", "0017_boundingbox_version_category_version_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="boundingbox",
            name="project_version",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name="category",
            name="project_version",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name="relation",
            name="project_version",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name="segmentation",
            name="project_version",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name="span",
            name="project_version",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name="textlabel",
            name="project_version",
            field=models.PositiveIntegerField(default=1),
        ),
    ] 