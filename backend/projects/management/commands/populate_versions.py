from django.core.management.base import BaseCommand
from django.utils import timezone
from projects.models import Project, Version


class Command(BaseCommand):
    help = 'Populate Version table with existing project data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--project-id',
            type=int,
            help='Specific project ID to populate versions for',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating',
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
                self.style.WARNING('No projects found to populate versions for.')
            )
            return

        created_count = 0
        skipped_count = 0

        for project in projects:
            # Check if versions already exist for this project
            if project.versions.exists():
                self.stdout.write(
                    f'Skipping project {project.id} ({project.name}) - versions already exist'
                )
                skipped_count += 1
                continue

            # Create initial version based on project creation
            version_data = {
                'project': project,
                'start_date': project.created_at,
                'status': project.status,
                'version': 1,  # First version is always 1
            }

            # If project is closed, set end_date to updated_at
            if project.status == 'closed':
                version_data['end_date'] = project.updated_at

            if dry_run:
                self.stdout.write(
                    f'Would create version for project {project.id} ({project.name}): '
                    f'start={version_data["start_date"]}, status={version_data["status"]}, version={version_data["version"]}'
                )
            else:
                Version.objects.create(**version_data)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created version {version_data["version"]} for project {project.id} ({project.name})'
                    )
                )
            
            created_count += 1

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would create {created_count} versions, skip {skipped_count} projects'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created {created_count} versions, skipped {skipped_count} projects'
                )
            ) 