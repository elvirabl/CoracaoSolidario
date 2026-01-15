# core/admin.py
from datetime import timedelta

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Donor, Receiver, Match, ReferencePost


# --------------------------------------------------
# ReferencePost
# --------------------------------------------------
@admin.register(ReferencePost)
class ReferencePostAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "public", "can_receive_donations")
    list_filter = ("city", "public", "can_receive_donations")
    search_fields = ("name", "city")


# --------------------------------------------------
# Donor
# --------------------------------------------------
@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "whatsapp",
        "preferred_kit",
        "reference_post",
        "active",
        "created_at",
    )
    list_filter = ("active", "preferred_kit", "reference_post")
    search_fields = ("name", "whatsapp")
    readonly_fields = ("created_at",)


# --------------------------------------------------
# Receiver
# --------------------------------------------------
@admin.register(Receiver)
class ReceiverAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "whatsapp",
        "needed_kit",
        "reference_post",
        "active",
        "created_at",
    )
    list_filter = ("active", "needed_kit", "reference_post")
    search_fields = ("name", "whatsapp")
    readonly_fields = ("created_at",)


# --------------------------------------------------
# Match  ⭐ CORAÇÃO DO MVP
# --------------------------------------------------
@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "reference_post",
        "donor",
        "receiver",
        "pickup_code",
        "is_completed",
        "created_at",
    )
    list_filter = ("reference_post", "is_completed")
    search_fields = (
        "pickup_code",
        "donor__name",
        "receiver__name",
        "donor__whatsapp",
        "receiver__whatsapp",
    )
    readonly_fields = ("pickup_code", "created_at")

    def save_model(self, request, obj, form, change):
        """
        Regras MVP aplicadas no Admin:
        1) Uma receptora só pode ter 1 match a cada 7 dias
        2) Donor e Receiver precisam pertencer ao mesmo posto
        3) Ao salvar o match, a doadora é automaticamente desativada
        """

        # --------------------------------------------------
        # Regra 1 — 1 match por receptora a cada 7 dias
        # --------------------------------------------------
        if obj.receiver_id:
            week_ago = timezone.now() - timedelta(days=7)

            qs = Match.objects.filter(
                receiver_id=obj.receiver_id,
                created_at__gte=week_ago,
            )

            if obj.pk:
                qs = qs.exclude(pk=obj.pk)

            if qs.exists():
                raise ValidationError(
                    "Esta receptora já possui um match criado nos últimos 7 dias. "
                    "Aguarde completar 1 semana para criar um novo match."
                )

        # --------------------------------------------------
        # Regra 2 — Mesmo posto de referência
        # --------------------------------------------------
        if obj.reference_post_id:
            if obj.donor_id and obj.donor.reference_post_id != obj.reference_post_id:
                raise ValidationError(
                    "O posto de referência da doadora é diferente do posto do match."
                )

            if obj.receiver_id and obj.receiver.reference_post_id != obj.reference_post_id:
                raise ValidationError(
                    "O posto de referência da receptora é diferente do posto do match."
                )

        # Salva o match
        super().save_model(request, obj, form, change)

        # --------------------------------------------------
        # Regra 3 — Doadora fica indisponível após o match
        # --------------------------------------------------
        if obj.donor_id and obj.donor.active:
            obj.donor.active = False
            obj.donor.save(update_fields=["active"])
