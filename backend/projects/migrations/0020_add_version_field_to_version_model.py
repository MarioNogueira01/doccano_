# Generated manually for adding version field to Version model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0019_create_version_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='version',
            name='version',
            field=models.IntegerField(default=1, help_text='Version number for this project version'),
        ),
    ] 