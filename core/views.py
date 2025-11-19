from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import render

from .models import Match, Donor, Receiver, ReferencePost


def home(request):
    return render(request, "core/home.html")


# --------- TELAS PÚBLICAS: DOAR / RECEBER --------- #
def doar(request):
    from .models import Donor, ReferencePost

    reference_posts = ReferencePost.objects.filter(
        can_receive_donations=True,
        public=True
    ).order_by("city", "name")

    if request.method == "POST":
        name = request.POST.get("name")
        whatsapp = request.POST.get("whatsapp")
        city = request.POST.get("city")
        neighborhood = request.POST.get("neighborhood")
        preferred_kit = request.POST.get("preferred_kit")
        reference_post_id = request.POST.get("reference_post") or None

        Donor.objects.create(
            name=name,
            whatsapp=whatsapp,
            city=city,
            neighborhood=neighborhood,
            preferred_kit=preferred_kit,
            reference_post_id=reference_post_id,
            active=True,
        )

        return render(request, "core/obrigada.html", {"tipo": "doadora"})

    return render(request, "core/doar.html", {
        "reference_posts": reference_posts,
    })

def receber(request):
    from .models import Receiver, ReferencePost

    reference_posts = ReferencePost.objects.filter(
        can_receive_donations=True,
        public=True
    ).order_by("city", "name")

    if request.method == "POST":
        name = request.POST.get("name")
        whatsapp = request.POST.get("whatsapp")
        city = request.POST.get("city")
        neighborhood = request.POST.get("neighborhood")
        needed_kit = request.POST.get("needed_kit")
        reference_post_id = request.POST.get("reference_post") or None

        Receiver.objects.create(
            name=name,
            whatsapp=whatsapp,
            city=city,
            neighborhood=neighborhood,
            needed_kit=needed_kit,
            reference_post_id=reference_post_id,
            is_breast_cancer_patient=True,
            active=True,
        )

        return render(request, "core/obrigada.html", {"tipo": "receptora"})

    return render(request, "core/receber.html", {
        "reference_posts": reference_posts,
    })

# --------- RELATÓRIOS DO ADMIN --------- #

@staff_member_required
def admin_reports(request):
    # Totais por tipo de kit
    kits = (
        Match.objects.values('kit_type')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    # Totais por status do match
    status = (
        Match.objects.values('status')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    # Contadores gerais
    totals = {
        'donors_active': Donor.objects.filter(active=True).count(),
        'receivers_active': Receiver.objects.filter(active=True).count(),
        'matches_total': Match.objects.count(),
        'matches_delivered': Match.objects.filter(status='ENTREGUE').count(),
        'matches_pending': Match.objects.filter(status='PENDENTE').count(),
    }

    # Últimos 10 matches (para auditoria rápida)
    recent = Match.objects.select_related('donor', 'receiver').order_by('-created_at')[:10]

    ctx = {
        'kits': kits,
        'status': status,
        'totals': totals,
        'recent': recent,
        'title': 'Relatórios do Coração Solidário',
    }
    return render(request, 'admin/reports.html', ctx)


@staff_member_required
def admin_reports_csv(request):
    # Exporta um CSV simples de matches
    rows = Match.objects.select_related('donor', 'receiver').values_list(
        'created_at', 'donor__name', 'receiver__name', 'kit_type', 'quantity', 'status'
    )

    def csv_escape(s):
        if s is None:
            return ''
        s = str(s)
        return '"' + s.replace('"', '""') + '"'

    content = ['"data","doadora","receptora","kit","quantidade","status"']
    for r in rows:
        line = ','.join(csv_escape(x) for x in r)
        content.append(line)

    resp = HttpResponse('\n'.join(content), content_type='text/csv; charset=utf-8')
    resp['Content-Disposition'] = 'attachment; filename="relatorios_matches.csv"'
    return resp
