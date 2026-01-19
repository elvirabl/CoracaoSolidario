from django.contrib import admin
from .models import Donor, Receiver, Match, ReferencePost


@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ("name", "whatsapp", "kit_type", "active", "created_at")
    list_filter = ("kit_type", "active", "created_at")
    search_fields = ("name", "whatsapp")
    ordering = ("-created_at",)


@admin.register(Receiver)
class ReceiverAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "whatsapp",
        "city",
        "neighborhood",
        "needed_kit",
        "reference_post",
        "active",
        "created_at",
    )
    list_filter = ("city", "needed_kit", "reference_post", "active", "created_at")
    search_fields = ("name", "whatsapp", "city", "neighborhood")
    ordering = ("-created_at",)


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ("pickup_code", "donor", "receiver", "reference_post", "is_completed", "created_at")
    list_filter = ("reference_post", "is_completed", "created_at")
    search_fields = (
        "pickup_code",
        "donor__name",
        "donor__whatsapp",
        "receiver__name",
        "receiver__whatsapp",
    )
    ordering = ("-created_at",)


@admin.register(ReferencePost)
class ReferencePostAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "type", "can_receive_donations", "public", "contact_name", "contact_phone")
    list_filter = ("city", "type", "can_receive_donations", "public")
    search_fields = ("name", "city", "neighborhood_coverage", "contact_name", "contact_phone")
    ordering = ("city", "name")
