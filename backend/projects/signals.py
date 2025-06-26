from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Project, Version

@receiver(post_save, sender=Project)
def create_or_update_version(sender, instance, created, **kwargs):
    # Quando um projeto é criado, cria uma versão aberta
    if created:
        Version.objects.create(
            project=instance,
            status=instance.status
        )
    else:
        # Sempre que o status mudar, cria uma nova versão ou fecha a anterior
        last_version = Version.objects.filter(project=instance).order_by('-start_date').first()
        if last_version:
            if last_version.status != instance.status:
                # Se mudou de open para closed, fecha a versão
                if instance.status == 'closed' and last_version.status == 'open':
                    from django.utils import timezone
                    last_version.status = 'closed'
                    last_version.end_date = timezone.now()
                    last_version.save()
                # Se mudou de closed para open, cria nova versão aberta
                elif instance.status == 'open' and last_version.status == 'closed':
                    Version.objects.create(
                        project=instance,
                        status='open'
                    ) 