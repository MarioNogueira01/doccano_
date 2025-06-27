from django.core.management.base import BaseCommand
from projects.models import Project, Version


class Command(BaseCommand):
    help = 'Populate version numbers for existing Version records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--project-id',
            type=int,
            help='Specific project ID to populate version numbers for',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without actually updating',
        )

    def handle(self, *args, **options):
        project_id = options.get('project_id')
        dry_run = options.get('dry_run')

        if project_id:
            projects = Project.objects.filter(id=project_id)
        else:
            projects = Project.objects.all()

        if not projects.exists():
            self.stdout.write(
                self.style.WARNING('No projects found to populate version numbers for.')
            )
            return

        updated_count = 0
        skipped_count = 0

        for project in projects:
            # Get all versions for this project ordered by start_date
            versions = Version.objects.filter(project=project).order_by('start_date')
            
            if not versions.exists():
                self.stdout.write(
                    f'Skipping project {project.id} ({project.name}) - no versions found'
                )
                skipped_count += 1
                continue

            # Update version numbers sequentially
            for index, version in enumerate(versions, 1):
                if version.version != index:
                    if dry_run:
                        self.stdout.write(
                            f'Would update version {version.id} for project {project.id} ({project.name}): '
                            f'version {version.version} -> {index}'
                        )
                    else:
                        version.version = index
                        version.save()
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Updated version {version.id} for project {project.id} ({project.name}): '
                                f'version {version.version}'
                            )
                        )
                    updated_count += 1
                else:
                    if dry_run:
                        self.stdout.write(
                            f'Version {version.id} for project {project.id} ({project.name}) already has correct version number: {version.version}'
                        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would update {updated_count} versions, skip {skipped_count} projects'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated {updated_count} versions, skipped {skipped_count} projects'
                )
            ) 