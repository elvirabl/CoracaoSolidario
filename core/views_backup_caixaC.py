# core/views.py
import re

from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from .permissions import role_required

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
    - remove HTML (sem usar strip_tags pra manter mínimo)
    - normaliza espaços
    - limita tamanho
    """
    if not raw:
        return ""
    txt = str(raw)
    txt = re.sub(r"<[^>]*?>", "", txt)      # remove tags simples
    txt = re.sub(r"\s+", " ", txt).strip()  # normaliza espaços
    return txt[:max_len]


# ---------------- HOME ---------------- #

def home(request):
    return render(request, "core/home.html")


# ---------------- TELA OBRIGADA (reutilizável) ---------------- #

def obrigada(request):
    return render(request, "core/obrigada.html")


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

        # captura + sanitização
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

        # validações
        if not name:
            errors.append("Nome é obrigatório.")
        if not whatsapp:
            errors.append("WhatsApp inválido. Ex: (15) 99123-4567")
        if not kit_type:
            errors.append("Selecione o tipo de kit.")
        if not reference_post_id:
            errors.append("Selecione o posto de referência.")

        if contains_bad_words(name, kit_type, whatsapp_raw):
            errors.append("Por segurança, revise o texto informado.")

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
                {"reference_posts": reference_posts, "errors": errors, "form": request.POST},
            )

        donor = Donor.objects.create(
            name=name,
            whatsapp=whatsapp,
            kit_type=kit_type,
            active=True,
        )

        # se por algum motivo ele já tem match em aberto
        if donor_has_open_match(donor):
            messages.info(
                request,
                "💛 Doação já registrada: você já possui uma doação em andamento. Assim que ela for concluída, poderá doar novamente."
            )
            return redirect("obrigada")

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

            # ✅ Notificação (Caixa B)
            messages.success(
                request,
                f"✨ Doação confirmada! Seu código de retirada é: {match.pickup_code}"
            )
            return redirect("obrigada")

        # ✅ Notificação (Caixa B)
        messages.success(
            request,
            "💛 Doação registrada! Assim que houver uma receptora compatível no posto escolhido, o match será feito."
        )
        return redirect("obrigada")

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
                {"reference_posts": reference_posts, "errors": errors, "form": request.POST},
            )

        Receiver.objects.create(
            name=name,
            whatsapp=whatsapp,
            city=city,
            neighborhood=neighborhood,
            needed_kit=needed_kit,
            reference_post=reference_post,
            active=True,
        )

        # ✅ Notificação (Caixa B)
        messages.success(
            request,
            "💛 Pedido registrado! Assim que houver uma doação compatível no posto escolhido, o match será feito."
        )
        return redirect("obrigada")

    return render(request, "core/receber.html", {"reference_posts": reference_posts})


# ---------------- RETIRADA (Dupla confirmação) ---------------- #

@role_required("admin", "manager", "operator")
def pickup_screen(request):
    return render(request, "core/pickup.html")


@role_required("admin", "manager", "operator")
@require_http_methods(["POST"])
def pickup_check(request):
    pickup_code = (request.POST.get("pickup_code") or "").strip()

    if not pickup_code:
        return render(request, "core/pickup.html", {
            "msg": "Informe um código de retirada.",
            "msg_class": "bad",
        })

    match = Match.objects.select_related("donor", "receiver", "reference_post").filter(
        pickup_code=pickup_code
    ).first()

    if not match:
        return render(request, "core/pickup.html", {
            "pickup_code": pickup_code,
            "msg": "Código não encontrado. Confira e tente novamente.",
            "msg_class": "bad",
        })

    # 🔒 Regra: operador/gestor só pode ver do próprio posto
    profile = request.user.profile
    if profile.role in ("manager", "operator"):
        if not profile.reference_post or match.reference_post_id != profile.reference_post_id:
            return render(request, "core/pickup.html", {
                "pickup_code": pickup_code,
                "msg": "Sem permissão: este código não pertence ao seu posto.",
                "msg_class": "bad",
            })

    return render(request, "core/pickup.html", {
        "pickup_code": pickup_code,
        "match": match,
        "msg": "Código válido. Confira os dados e confirme a retirada.",
        "msg_class": "ok",
    })


@role_required("admin", "manager", "operator")
@require_http_methods(["POST"])
def pickup_confirm(request):
    match_id = request.POST.get("match_id")
    pickup_code = (request.POST.get("pickup_code") or "").strip()

    if not match_id or not pickup_code:
        return render(request, "core/pickup.html", {
            "msg": "Dados incompletos para confirmar.",
            "msg_class": "bad",
        })

    match = Match.objects.select_related("donor", "receiver", "reference_post").filter(
        id=match_id,
        pickup_code=pickup_code,
    ).first()

    if not match:
        return render(request, "core/pickup.html", {
            "msg": "Não foi possível confirmar: match/código inválidos.",
            "msg_class": "bad",
        })

    # 🔒 Regra: operador/gestor só pode confirmar no próprio posto
    profile = request.user.profile
    if profile.role in ("manager", "operator"):
        if not profile.reference_post or match.reference_post_id != profile.reference_post_id:
            return render(request, "core/pickup.html", {
                "pickup_code": pickup_code,
                "msg": "Sem permissão: este match não pertence ao seu posto.",
                "msg_class": "bad",
            })

    if match.is_completed:
        return render(request, "core/pickup.html", {
            "pickup_code": pickup_code,
            "match": match,
            "msg": "Este código já foi usado. Retirada já concluída.",
            "msg_class": "bad",
        })

    match.is_completed = True
    match.save()

    messages.success(request, "✅ Retirada confirmada com sucesso.")

    return render(request, "core/pickup.html", {
        "pickup_code": pickup_code,
        "match": match,
        "msg": "Retirada confirmada com sucesso ✅",
        "msg_class": "ok",
    })