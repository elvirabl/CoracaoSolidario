from django.contrib import admin
from .models import ReferencePost, Donor, Receiver, Match


@admin.register(ReferencePost)
class ReferencePostAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "city",
        "neighborhood_coverage",
        "public",
        "can_receive_donations",
    )
    list_filter = ("city", "public", "can_receive_donations")
    search_fields = ("name", "city", "neighborhood_coverage")
    ordering = ("city", "name")


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
    list_filter = ("preferred_kit", "active", "reference_post")
    search_fields = ("name", "whatsapp")
    ordering = ("-created_at",)


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
    list_filter = ("needed_kit", "active", "reference_post")
    search_fields = ("name", "whatsapp")
    ordering = ("-created_at",)


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "pickup_code",
        "donor",
        "receiver",
        "reference_post",
        "is_completed",
        "created_at",
    )
    list_filter = ("is_completed", "reference_post")
    search_fields = (
        "pickup_code",
        "donor__name",
        "receiver__name",
        "reference_post__name",
    )
    ordering = ("-created_at",)
