from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Match, UserProfile
from core.services.match_notify import notify_match


# =========================
# Match: notificação ao criar
# =========================
@receiver(post_save, sender=Match)
def notificar_match_criado(sender, instance, created, **kwargs):
    """
    Dispara notificação apenas quando o Match é criado.
    O pickup_code é gerado no Match.save() (Jeito A), não aqui.
    """
    if created:
        notify_match(instance)


# =========================
# User: cria UserProfile automático
# =========================
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def garantir_userprofile(sender, instance, created, **kwargs):
    """
    Garante que todo User tenha um UserProfile.
    - Se for usuário novo, cria.
    - Se for usuário antigo sem profile, cria também.
    """
    UserProfile.objects.get_or_create(user=instance)