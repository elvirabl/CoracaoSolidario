from django.contrib import admin
from .models import ReferencePost, Donor, Receiver, Match
from .models import Match

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


@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ("name", "preferred_kit", "reference_post", "active")
    list_filter = ("preferred_kit", "active")
    search_fields = ("name", "whatsapp")


@admin.register(Receiver)
class ReceiverAdmin(admin.ModelAdmin):
    list_display = ("name", "needed_kit", "reference_post", "active")
    list_filter = ("needed_kit", "active")
    search_fields = ("name", "whatsapp")

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "donor",
        "receiver",
        "reference_post",
        "is_completed",
        "created_at",
    )

    list_filter = (
        "is_completed",
        "reference_post",
    )

    search_fields = (
        "donor__name",
        "receiver__name",
        "reference_post__name",
    )
