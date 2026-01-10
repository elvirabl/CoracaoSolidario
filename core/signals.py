from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Match
from core.services.match_notify import notify_match


@receiver(post_save, sender=Match)
def notificar_match_criado(sender, instance, created, **kwargs):
    """
    Dispara notificação apenas quando o Match é criado.
    O pickup_code é gerado no Match.save() (Jeito A), não aqui.
    """
    if created:
        notify_match(instance)