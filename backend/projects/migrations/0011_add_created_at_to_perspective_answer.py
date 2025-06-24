# Generated manually to add created_at field to PerspectiveAnswer

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0010_perspectiveanswer_example"),
    ]

    operations = [
        migrations.AddField(
            model_name="perspectiveanswer",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ] 