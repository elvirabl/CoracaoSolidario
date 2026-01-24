# core/views.py
from io import BytesIO
import qrcode
import re

from django.core.cache import cache
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.html import strip_tags
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from django.contrib.admin.views.decorators import staff_member_required

from .models import Donor, Match, Receiver, ReferencePost
from .utils.validators import normalize_phone_br, contains_bad_words


# ---------------- UTILIDADES ---------------- #

def donor_has_open_match(donor: Donor) -> bool:
    return Match.objects.filter(donor=donor, is_completed=False).exists()


def receiver_has_open_match(receiver: Receiver) -> bool:
    return Match.objects.filter(receiver=receiver, is_completed=False).exists()


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
            cache.set(key, int(current) + 1, timeout=window_sec)

    return False


def clean_text(raw: str, max_len: int = 120) -> str:
    """
    Sanitização simples (MVP):
    - remove HTML
    - normaliza espaços
    - limita tamanho
    """
    if not raw:
        return ""
    txt = strip_tags(str(raw))
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt[:max_len]


# ---------------- HOME ---------------- #

def home(request):
    return render(request, "core/home.html")


# ---------------- DOAR ---------------- #

@require_http_methods(["GET", "POST"])
def doar(request):
    reference_posts = ReferencePost.objects.filter(
        can_receive_donations=True,
        public=True
    ).order_by("city", "name")

    if request.method == "POST":
        if rate_limit_or_429(request, "form_doar", limit=5, window_sec=300):
            return HttpResponse(
                "Muitas tentativas. Aguarde alguns minutos e tente novamente.",
                status=429
            )

        # --- CAPTURA + SANITIZAÇÃO (item 2) ---
        name = clean_text(request.POST.get("name"), max_len=80)
        whatsapp_raw = clean_text(request.POST.get("whatsapp"), max_len=30)
        whatsapp = normalize_phone_br(whatsapp_raw)

        kit_type = clean_text(
            request.POST.get("preferred_kit")
            or request.POST.get("kit_type")
            or request.POST.get("kit")
            or "",
            max_len=40
        )

        reference_post_id = (
            request.POST.get("reference_post")
            or request.POST.get("reference_post_id")
        )

        errors = []

        # --- VALIDAÇÕES ---
        if not name:
            errors.append("Nome é obrigatório.")
        if not whatsapp:
            errors.append("WhatsApp inválido. Ex: (15) 99123-4567")
        if not kit_type:
            errors.append("Selecione o tipo de kit.")
        if not reference_post_id:
            errors.append("Selecione o posto de referência.")

        # filtro anti-abuso (você já tem)
        if contains_bad_words(name, kit_type, whatsapp_raw):
            errors.append("Por segurança, revise o texto informado.")

        # duplicidade simples (MVP)
        if whatsapp and Donor.objects.filter(whatsapp=whatsapp, active=True).exists():
            errors.append("Este WhatsApp já está cadastrado como doador.")

        reference_post = None
        if reference_post_id:
            reference_post = ReferencePost.objects.filter(id=reference_post_id).first()
            if not reference_post:
                errors.append("Posto de referência inválido.")

        if errors:
            return render(
                request,
                "core/doar.html",
                {
                    "reference_posts": reference_posts,
                    "errors": errors,
                    "form": request.POST,
                },
            )

        # cria doador
        donor = Donor.objects.create(
            name=name,
            whatsapp=whatsapp,
            kit_type=kit_type,
            active=True,
        )

        # bloqueio: doador já tem match pendente
        # (OBS: com o check de duplicidade acima, isso aqui fica quase sempre desnecessário,
        # mas mantive para não mudar seu fluxo)
        if donor_has_open_match(donor):
            return render(request, "core/obrigada.html", {
                "tipo": "doacao",
                "title": "Doação já registrada 💛",
                "message": "Você já possui uma doação em andamento. Assim que ela for concluída, poderá doar novamente.",
            })

        # procura receptora compatível
        receiver = (
            Receiver.objects
            .filter(
                active=True,
                needed_kit=donor.kit_type,
                reference_post=reference_post,
            )
            .exclude(
                id__in=Match.objects.filter(is_completed=False)
                .values_list("receiver_id", flat=True)
            )
            .order_by("created_at")
            .first()
        )

        if receiver:
            match = Match.objects.create(
                donor=donor,
                receiver=receiver,
                reference_post=reference_post,
            )
            return render(request, "core/obrigada.html", {
                "tipo": "doacao",
                "title": "Doação confirmada 💛",
                "message": f"Seu código de retirada é:",
                "pickup_code": match.pickup_code,
            })

        # se não achou receptora agora
        return render(request, "core/obrigada.html", {
            "tipo": "doacao",
            "title": "Doação registrada 💛",
            "message": "Assim que houver uma receptora compatível no posto escolhido, o match será feito.",
        })

    return render(request, "core/doar.html", {"reference_posts": reference_posts})


# ---------------- RECEBER ---------------- #

@require_http_methods(["GET", "POST"])
def receber(request):
    reference_posts = ReferencePost.objects.filter(
        can_receive_donations=True,
        public=True
    ).order_by("city", "name")

    if request.method == "POST":
        if rate_limit_or_429(request, "form_receber", limit=5, window_sec=300):
            return HttpResponse(
                "Muitas tentativas. Aguarde alguns minutos e tente novamente.",
                status=429
            )

        # --- CAPTURA + SANITIZAÇÃO (item 2) ---
        name = clean_text(request.POST.get("name"), max_len=80)
        whatsapp_raw = clean_text(request.POST.get("whatsapp"), max_len=30)
        whatsapp = normalize_phone_br(whatsapp_raw)

        city = clean_text(request.POST.get("city"), max_len=40)
        neighborhood = clean_text(request.POST.get("neighborhood"), max_len=60)

        needed_kit = clean_text(
            request.POST.get("needed_kit")
            or request.POST.get("kit_type")
            or request.POST.get("kit")
            or "",
            max_len=40
        )

        reference_post_id = (
            request.POST.get("reference_post")
            or request.POST.get("reference_post_id")
        )

        errors = []

        # --- VALIDAÇÕES ---
        if not name:
            errors.append("Nome é obrigatório.")
        if not whatsapp:
            errors.append("WhatsApp inválido.")
        if not city:
            errors.append("Cidade é obrigatória.")
        if not neighborhood:
            errors.append("Bairro é obrigatório.")
        if not needed_kit:
            errors.append("Selecione o tipo de kit.")
        if not reference_post_id:
            errors.append("Selecione o posto de referência.")

        if contains_bad_words(name, needed_kit, whatsapp_raw):
            errors.append("Por segurança, revise o texto informado.")

        # duplicidade simples (MVP)
        if whatsapp and Receiver.objects.filter(whatsapp=whatsapp, active=True).exists():
            errors.append("Este WhatsApp já está cadastrado como receptora.")

        reference_post = None
        if reference_post_id:
            reference_post = ReferencePost.objects.filter(id=reference_post_id).first()
            if not reference_post:
                errors.append("Posto de referência inválido.")

        if errors:
            return render(
                request,
                "core/receber.html",
                {
                    "reference_posts": reference_posts,
                    "errors": errors,
                    "form": request.POST,
                },
            )

        receiver = Receiver.objects.create(
            name=name,
            whatsapp=whatsapp,
            city=city,
            neighborhood=neighborhood,
            needed_kit=needed_kit,
            reference_post=reference_post,
            active=True,
        )

        return render(request, "core/obrigada.html", {"tipo": "recebimento"})

    return render(request, "core/receber.html", {"reference_posts": reference_posts})


# ---------------- RETIRADA ---------------- #

@require_GET
@staff_member_required
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
@staff_member_required
@require_POST
def confirmar_retirada(request, pickup_code: str):
    match = get_object_or_404(Match, pickup_code=pickup_code)

    if not match.is_completed:
        match.is_completed = True
        match.save(update_fields=["is_completed"])

    return redirect("core:retirar", pickup_code=pickup_code)


# ---------------- QR CODE PNG ---------------- #

@require_GET
def qr_pickup_png(request, pickup_code: str):
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
