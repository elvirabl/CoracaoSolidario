from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from core.views import home, doar, receber, admin_reports, admin_reports_csv

urlpatterns = [
    # página pública
    path("", home, name="home"),

    # telas públicas de cadastro
    path("doar/", doar, name="doar"),
    path("receber/", receber, name="receber"),

    # relatórios do admin
    path("admin/reports/csv/", admin_reports_csv, name="admin-reports-csv"),
    path("admin/reports/", admin_reports, name="admin-reports"),

    # admin
    path("admin/", admin.site.urls),
]

# servir arquivos estáticos (logo, CSS) em modo DEBUG
if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.BASE_DIR / "core" / "static",
    )
