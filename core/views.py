# core/views.py
from io import BytesIO

import qrcode
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .models import Donor, Match, Receiver, ReferencePost
from .utils.validators import normalize_phone_br, contains_bad_words


def rate_limit_or_429(request, key_prefix: str, limit: int = 5, window_sec: int = 300) -> bool:
    """
    True = BLOQUEAR (excedeu limite)
    False = OK
    """
    ip = request.META.get("REMOTE_ADDR", "unknown")
    key = f"{key_prefix}:{ip}"
    current = cache.get(key, 0)

    if current >= limit:
        return True

    if current == 0:
        cache.set(key, 1, timeout=window_sec)
    else:
        try:
            cache.incr(key)
        except Exception:
            # caso o backend de cache não suporte incr
            cache.set(key, int(current) + 1, timeout=window_sec)

    return False


# ---------------- HOME ---------------- #
def home(request):
    return render(request, "core/home.html")


# --------- TELAS PÚBLICAS: DOAR ---------------- #
@require_http_methods(["GET", "POST"])
def doar(request):
    reference_posts = ReferencePost.objects.filter(
        can_receive_donations=True,
        public=True
    ).order_by("city", "name")

    if request.method == "POST":
        # Anti-spam: 5 tentativas por 5 minutos por IP
        if rate_limit_or_429(request, "form_doar", limit=5, window_sec=300):
            return HttpResponse(
            "Muitas tentativas. Aguarde alguns minutos e tente novamente.",
            status=429
)


        name = (request.POST.get("name") or "").strip()

        whatsapp_raw = (request.POST.get("whatsapp") or "").strip()
        whatsapp = normalize_phone_br(whatsapp_raw)

        # Aceita qualquer name usado no HTML
        preferred_kit = (
            request.POST.get("preferred_kit")
            or request.POST.get("kit_type")
            or request.POST.get("kit")
            or ""
        ).strip()

        reference_post_id = (
            request.POST.get("reference_post")
            or request.POST.get("reference_post_id")
        )

        errors = []
        if not name:
            errors.append("Nome é obrigatório.")
        if not whatsapp:
            errors.append("WhatsApp inválido. Ex: (15) 99123-4567")
        if not preferred_kit:
            errors.append("Selecione o tipo de kit.")
        if not reference_post_id:
            errors.append("Selecione o posto de referência.")

        # Proteção contra palavras maliciosas/ofensivas
        if contains_bad_words(name, preferred_kit, whatsapp_raw):
            errors.append("Por segurança, revise o texto informado.")

        reference_post = None
        if reference_post_id:
            reference_post = ReferencePost.objects.filter(id=reference_post_id).first()
            if not reference_post:
                errors.append("Posto de referência inválido.")

        if not errors:
            Donor.objects.create(
                name=name,
                whatsapp=whatsapp,  # <- normalizado (só dígitos)
                preferred_kit=preferred_kit,
                reference_post=reference_post,
                active=True,
            )
            return render(request, "core/obrigada.html", {"tipo": "doacao"})

        return render(
            request,
            "core/doar.html",
            {
                "reference_posts": reference_posts,
                "errors": errors,
                "form": request.POST,
            },
        )

    return render(request, "core/doar.html", {"reference_posts": reference_posts})


# --------- TELAS PÚBLICAS: RECEBER ---------------- #
@require_http_methods(["GET", "POST"])
def receber(request):
    reference_posts = ReferencePost.objects.filter(
        can_receive_donations=True,
        public=True
    ).order_by("city", "name")

    if request.method == "POST":
        # Anti-spam: 5 tentativas por 5 minutos por IP
        if rate_limit_or_429(request, "form_receber", limit=5, window_sec=300):
            return HttpResponse(
              "Muitas tentativas. Aguarde alguns minutos e tente novamente.",
               status=429
)


        name = (request.POST.get("name") or "").strip()

        whatsapp_raw = (request.POST.get("whatsapp") or "").strip()
        whatsapp = normalize_phone_br(whatsapp_raw)

        needed_kit = (
            request.POST.get("needed_kit")
            or request.POST.get("kit_type")
            or request.POST.get("kit")
            or ""
        ).strip()

        reference_post_id = (
            request.POST.get("reference_post")
            or request.POST.get("reference_post_id")
        )

        errors = []
        if not name:
            errors.append("Nome é obrigatório.")
        if not whatsapp:
            errors.append("WhatsApp inválido. Ex: (15) 99123-4567")
        if not needed_kit:
            errors.append("Selecione o tipo de kit.")
        if not reference_post_id:
            errors.append("Selecione o posto de referência.")

        # Proteção contra palavras maliciosas/ofensivas
        if contains_bad_words(name, needed_kit, whatsapp_raw):
            errors.append("Por segurança, revise o texto informado.")

        reference_post = None
        if reference_post_id:
            reference_post = ReferencePost.objects.filter(id=reference_post_id).first()
            if not reference_post:
                errors.append("Posto de referência inválido.")

        if not errors:
            Receiver.objects.create(
                name=name,
                whatsapp=whatsapp,  # <- normalizado (só dígitos)
                needed_kit=needed_kit,
                reference_post=reference_post,
                active=True,
            )
            return render(request, "core/obrigada.html", {"tipo": "recebimento"})

        return render(
            request,
            "core/receber.html",
            {
                "reference_posts": reference_posts,
                "errors": errors,
                "form": request.POST,
            },
        )

    return render(request, "core/receber.html", {"reference_posts": reference_posts})


# ---------------- RETIRADA (PÚBLICA) ---------------- #
@require_GET
def retirar(request, pickup_code: str):
    match = get_object_or_404(
        Match.objects.select_related("donor", "receiver", "reference_post"),
        pickup_code=pickup_code,
    )

    qr_png_url = reverse("core:qr_pickup_png", args=[pickup_code])

    return render(
        request,
        "core/retirar.html",
        {
            "match": match,
            "qr_png_url": qr_png_url,
        },
    )


@require_POST
def confirmar_retirada(request, pickup_code: str):
    match = get_object_or_404(Match, pickup_code=pickup_code)

    if not match.is_completed:
        match.is_completed = True
        if hasattr(match, "completed_at"):
            match.completed_at = timezone.now()
            match.save(update_fields=["is_completed", "completed_at"])
        else:
            match.save(update_fields=["is_completed"])

    return redirect("core:retirar", pickup_code=pickup_code)


# ---------------- QR CODE PNG ---------------- #
@require_GET
def qr_pickup_png(request, pickup_code: str):
    """
    Retorna um PNG do QR Code que aponta para a página pública /retirar/<pickup_code>/
    """
    get_object_or_404(Match, pickup_code=pickup_code)

    retirar_url = request.build_absolute_uri(
        reverse("core:retirar", args=[pickup_code])
    )

    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(retirar_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    png_bytes = buffer.getvalue()

    response = HttpResponse(png_bytes, content_type="image/png")
    response["Cache-Control"] = "no-store, max-age=0"
    return response
