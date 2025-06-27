# Generated manually for populating version numbers

from django.db import migrations


def populate_version_numbers(apps, schema_editor):
    """Populate version numbers for existing Version records."""
    Version = apps.get_model('projects', 'Version')
    Project = apps.get_model('projects', 'Project')
    
    for project in Project.objects.all():
        # Get all versions for this project ordered by start_date
        versions = Version.objects.filter(project=project).order_by('start_date')
        
        # Update version numbers sequentially
        for index, version in enumerate(versions, 1):
            version.version = index
            version.save()


def reverse_populate_version_numbers(apps, schema_editor):
    """Reverse operation - set all version numbers back to 1."""
    Version = apps.get_model('projects', 'Version')
    Version.objects.all().update(version=1)


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0020_add_version_field_to_version_model'),
    ]

    operations = [
        migrations.RunPython(
            populate_version_numbers,
            reverse_populate_version_numbers
        ),
    ] 