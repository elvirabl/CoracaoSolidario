from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import ReferencePost, Donor, Receiver, Match, UserProfile


@admin.register(ReferencePost)
class ReferencePostAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "type", "public", "can_receive_donations", "contact_name", "contact_phone")
    list_filter = ("city", "type", "public", "can_receive_donations")
    search_fields = ("name", "city", "neighborhood_coverage", "contact_name", "contact_phone")


@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ("name", "whatsapp", "kit_type", "active", "created_at")
    list_filter = ("kit_type", "active", "created_at")
    search_fields = ("name", "whatsapp")
    readonly_fields = ("created_at",)


@admin.register(Receiver)
class ReceiverAdmin(admin.ModelAdmin):
    list_display = ("name", "whatsapp", "city", "neighborhood", "needed_kit", "reference_post", "active", "created_at")
    list_filter = ("city", "needed_kit", "reference_post", "active", "created_at", "is_breast_cancer_patient")
    search_fields = ("name", "whatsapp", "city", "neighborhood")
    readonly_fields = ("created_at",)


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ("pickup_code", "donor", "receiver", "reference_post", "is_completed", "created_at")
    list_filter = ("reference_post", "is_completed", "created_at")
    search_fields = ("pickup_code", "donor__name", "receiver__name")
    readonly_fields = ("created_at",)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "reference_post", "created_at")
    list_filter = ("role", "reference_post", "created_at")
    search_fields = ("user__username", "user__first_name", "user__last_name", "user__email")
    readonly_fields = ("created_at",)


# ---- Inline do perfil dentro do User (fica chique e prático) ----
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    fk_name = "user"
    extra = 0


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)