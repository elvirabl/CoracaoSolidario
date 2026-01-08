from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_GET

from .models import Match, Donor, Receiver, ReferencePost


def home(request):
    return render(request, "core/home.html")


# --------- TELAS PÚBLICAS: DOAR / RECEBER --------- #

def doar(request):
    reference_posts = ReferencePost.objects.filter(
        can_receive_donations=True,
        public=True
    ).order_by("city", "name")

    if request.method == "POST":
        Donor.objects.create(
            name=request.POST.get("name"),
            whatsapp=request.POST.get("whatsapp"),
            city=request.POST.get("city"),
            neighborhood=request.POST.get("neighborhood"),
            preferred_kit=request.POST.get("preferred_kit"),
            reference_post_id=request.POST.get("reference_post"),
            allow_whatsapp=True,
            active=True,
        )

        url = reverse("obrigada") + "?tipo=doadora"
        return redirect(url)

    return render(request, "core/doar.html", {
        "reference_posts": reference_posts,
    })


def receber(request):
    reference_posts = ReferencePost.objects.filter(
        can_receive_donations=True,
        public=True
    ).order_by("city", "name")

    if request.method == "POST":
        Receiver.objects.create(
            name=request.POST.get("name"),
            whatsapp=request.POST.get("whatsapp"),
            city=request.POST.get("city"),
            neighborhood=request.POST.get("neighborhood"),
            needed_kit=request.POST.get("needed_kit"),
            reference_post_id=request.POST.get("reference_post"),
            is_breast_cancer_patient=bool(request.POST.get("is_breast_cancer_patient")),
            active=True,
        )

        url = reverse("obrigada") + "?tipo=receptora"
        return redirect(url)

    return render(request, "core/receber.html", {
        "reference_posts": reference_posts,
    })


def obrigada(request):
    tipo = request.GET.get("tipo")  # "doadora" ou "receptora"
    return render(request, "core/obrigada.html", {"tipo": tipo})


# --------- RELATÓRIOS DO ADMIN --------- #

@staff_member_required
def admin_reports(request):
    # Totais por tipo de kit (baseado no kit da doadora)
    kits = (
        Match.objects.select_related("donor")
        .values("donor__preferred_kit")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    # Lista simples para “auditoria”: quem com quem e qual kit
    status = (
        Match.objects.select_related("donor", "receiver")
        .values(
            "donor__name",
            "receiver__name",
            "donor__preferred_kit",
            "is_completed",
            "pickup_code",
            "created_at",
        )
        .order_by("-created_at")[:200]
    )

    totals = {
        "donors_active": Donor.objects.filter(active=True).count(),
        "receivers_active": Receiver.objects.filter(active=True).count(),
        "matches_total": Match.objects.count(),
        "matches_delivered": Match.objects.filter(is_completed=True).count(),
        "matches_pending": Match.objects.filter(is_completed=False).count(),
    }

    recent = (
        Match.objects.select_related("donor", "receiver")
        .order_by("-created_at")[:10]
    )

    ctx = {
        "kits": kits,
        "status": status,
        "totals": totals,
        "recent": recent,
        "title": "Relatórios do Coração Solidário",
    }
    return render(request, "admin/reports.html", ctx)


@staff_member_required
def admin_reports_csv(request):
    """
    Exporta um CSV simples de matches (modelo atual).
    """
    rows = Match.objects.select_related("donor", "receiver").values_list(
        "created_at",
        "donor__name",
        "receiver__name",
        "donor__preferred_kit",
        "pickup_code",
        "is_completed",
    )

    def csv_escape(s):
        if s is None:
            return ""
        s = str(s)
        return '"' + s.replace('"', '""') + '"'

    # Cabeçalho
    content = ['"data","doadora","receptora","kit","codigo_retirada","retirado"']

    for created_at, donor_name, receiver_name, kit_key, pickup_code, is_completed in rows:
        # kit_key é tipo "basic", "complete" etc.
        # Se quiser, dá pra traduzir aqui depois.
        line = ",".join(csv_escape(x) for x in [
            created_at,
            donor_name,
            receiver_name,
            kit_key,
            pickup_code,
            "SIM" if is_completed else "NAO",
        ])
        content.append(line)

    resp = HttpResponse("\n".join(content), content_type="text/csv; charset=utf-8")
    resp["Content-Disposition"] = 'attachment; filename="relatorios_matches.csv"'
    return resp


# ----------------------------------------------------------- #
# API PARA AUTOMAÇÃO DO WHATSAPP (FASE 2 - PLANEJAMENTO)     #
# ----------------------------------------------------------- #

def montar_mensagem_receptora(match):
    """
    Monta o texto de WhatsApp para a receptora,
    com base no match + posto + código de retirada.
    """
    receiver = match.receiver
    reference_post = receiver.reference_post if receiver else None
    pickup_code = match.pickup_code

    mensagem = (
        f"🌷 Olá, {receiver.name}!\n"
        f"Seu pedido foi pareado com uma doação compatível. 🫶\n\n"
        f"Você já pode retirar o seu kit em:\n"
        f"📍 {reference_post.name if reference_post else 'Posto não informado'}\n"
        f"🔢 Código de retirada: {pickup_code}\n\n"
        f"Apresente esse código no posto para receber o seu kit.\n"
        f"Qualquer problema na retirada, fale com a gente por aqui. 💗"
    )

    return mensagem


@require_GET
def api_matches(request):
    """
    Endpoint simples que retorna os últimos matches
    para consumo pelo robô de WhatsApp.
    """
    queryset = (
        Match.objects
        .select_related("receiver")
        .order_by("-id")[:50]
    )

    data = []
    for match in queryset:
        receiver = match.receiver
        if not receiver or not receiver.whatsapp:
            continue

        data.append({
            "name": receiver.name,
            "phone": receiver.whatsapp,
            "message": montar_mensagem_receptora(match),
            "pickup_code": match.pickup_code,
        })

    return JsonResponse(
        {"matches": data},
        json_dumps_params={"ensure_ascii": False},
    )
