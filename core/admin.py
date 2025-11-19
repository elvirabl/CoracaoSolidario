from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import ReferencePost, Donor, Receiver, Match


@admin.register(ReferencePost)
class ReferencePostAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "city", "can_receive_donations", "public")
    list_filter = ("type", "city", "can_receive_donations", "public")
    search_fields = ("name", "city", "neighborhood_coverage")


@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "neighborhood", "preferred_kit", "active")
    list_filter = ("city", "preferred_kit", "active")
    search_fields = ("name", "whatsapp", "neighborhood")
    actions = ["criar_receptoras_correspondentes"]

    def criar_receptoras_correspondentes(self, request, queryset):
        """
        Para cada Doadora selecionada, cria (se ainda não existir)
        uma Receptora com os mesmos dados básicos.
        """
        from .models import Receiver  # import local para evitar loops

        criadas = 0
        for donor in queryset:
            # evita duplicar se já houver receptora com mesmo nome + whatsapp
            exists = Receiver.objects.filter(
                name=donor.name,
                whatsapp=donor.whatsapp
            ).exists()
            if exists:
                continue

            Receiver.objects.create(
                name=donor.name,
                whatsapp=donor.whatsapp,
                city=donor.city,
                neighborhood=donor.neighborhood,
                is_breast_cancer_patient=True,
                needed_kit=donor.preferred_kit or "KIT_BASICO",
                reference_post=donor.reference_post,
                notes="Criada automaticamente a partir do cadastro de Doadora.",
                active=True,
            )
            criadas += 1

        self.message_user(
            request,
            f"{criadas} Receptoras criadas a partir das Doadoras selecionadas."
        )

    criar_receptoras_correspondentes.short_description = "Criar Receptoras correspondentes"


@admin.register(Receiver)
class ReceiverAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "neighborhood", "needed_kit", "active")
    list_filter = ("city", "needed_kit", "active")
    search_fields = ("name", "whatsapp", "neighborhood")
    actions = ["criar_doadoras_correspondentes"]

    def criar_doadoras_correspondentes(self, request, queryset):
        """
        Para cada Receptora selecionada, cria (se ainda não existir)
        uma Doadora com os mesmos dados básicos.
        """
        from .models import Donor  # import local para evitar loops

        criadas = 0
        for receiver in queryset:
            exists = Donor.objects.filter(
                name=receiver.name,
                whatsapp=receiver.whatsapp
            ).exists()
            if exists:
                continue

            Donor.objects.create(
                name=receiver.name,
                whatsapp=receiver.whatsapp,
                email="",
                city=receiver.city,
                neighborhood=receiver.neighborhood,
                allow_whatsapp=True,
                preferred_kit=receiver.needed_kit,
                reference_post=receiver.reference_post,
                active=True,
            )
            criadas += 1

        self.message_user(
            request,
            f"{criadas} Doadoras criadas a partir das Receptoras selecionadas."
        )

    criar_doadoras_correspondentes.short_description = "Criar Doadoras correspondentes"


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = (
        "donor",
        "receiver",
        "kit_type",
        "status_colored",
        "pickup_code_badge",
        "pickup_used",
        "created_at",
        "relatorios_link",
    )
    list_filter = ("status", "pickup_used", "kit_type", "created_at")
    search_fields = ("donor__name", "receiver__name", "pickup_code")
    readonly_fields = (
        "pickup_code",
        "created_at",
        "updated_at",
        "pickup_used_at",
        "whatsapp_message",
    )

    fieldsets = (
        (None, {
            "fields": ("donor", "receiver", "kit_type", "quantity", "status")
        }),
        ("Retirada", {
            "fields": ("pickup_code", "pickup_used", "pickup_used_at", "whatsapp_message"),
        }),
        ("Outros", {
            "fields": ("notes", "created_at", "updated_at"),
        }),
    )

    # --- Campos "bonitões" na lista ---

    def status_colored(self, obj):
        colors = {
            "PENDENTE": "#f1c40f",   # amarelo
            "CONFIRMADO": "#3498db", # azul
            "ENTREGUE": "#2ecc71",   # verde
            "CANCELADO": "#e74c3c",  # vermelho
        }
        color = colors.get(obj.status, "#7f8c8d")
        return format_html(
            '<span style="padding:2px 8px; border-radius:12px; '
            'background-color:{}; color:white; font-size:11px;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_colored.short_description = "Status"
    status_colored.admin_order_field = "status"

    def pickup_code_badge(self, obj):
        if not obj.pickup_code:
            return "—"
        return format_html(
            '<span style="padding:2px 8px; border-radius:12px; '
            'border:1px solid #888; font-family:monospace; font-size:11px;">'
            '{}</span>',
            obj.pickup_code,
        )

    pickup_code_badge.short_description = "Código de retirada"
    pickup_code_badge.admin_order_field = "pickup_code"

    def whatsapp_message(self, obj):
        """
        Mensagem pronta para copiar e colar no WhatsApp,
        com o código de retirada já encaixado.
        """
        if not obj.receiver or not obj.pickup_code:
            return "Preencha doadora, receptora e salve o Match para gerar a mensagem."

        kit_label = obj.get_kit_type_display() if hasattr(obj, "get_kit_type_display") else obj.kit_type
        text = (
            f"Olá, {obj.receiver.name}! "
            f"Seu kit {kit_label} está disponível no posto de referência. "
            f"Código de retirada: {obj.pickup_code}."
        )
        # textarea bonitinho para facilitar copiar
        return format_html(
            '<textarea rows="3" cols="60" readonly style="font-size:12px;">{}</textarea>',
            text
        )

    whatsapp_message.short_description = "Mensagem para WhatsApp"

    def relatorios_link(self, obj):
        url = reverse("admin-reports")
        return format_html('<a class="button" href="{}">Relatórios</a>', url)

    relatorios_link.short_description = "Relatórios"
