# Generated manually to add created_at field to PerspectiveAnswer

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0015_project_project_version_project_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='perspectiveanswer',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ] 