from django.contrib import admin
from django.urls import path
#from . import views
from django.conf import settings
from django.conf.urls.static import static

from core.views import (
    home,
    doar,
    receber,
    obrigada,
    admin_reports,
    admin_reports_csv,
    api_matches,          # ← ADICIONAR ESTA LINHA
)
#                                     ^^^^^^^^^

urlpatterns = [
    path("", home, name="home"),
    path("doar/", doar, name="doar"),
    path("receber/", receber, name="receber"),
    path("obrigada/", obrigada, name="obrigada"),

    path("admin/reports/csv/", admin_reports_csv, name="admin-reports-csv"),
    path("admin/reports/", admin_reports, name="admin-reports"),

    path("admin/", admin.site.urls),
    path("api/matches/", api_matches, name="api_matches"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.BASE_DIR / "core" / "static",
    )