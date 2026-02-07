from django.contrib import admin
from django.urls import path

from core.views import (
    home,
    doar,
    receber,
    obrigada,
    pickup_screen,
    pickup_check,
    pickup_confirm,
)

urlpatterns = [
    # público
    path("", home, name="home"),
    path("doar/", doar, name="doar"),
    path("receber/", receber, name="receber"),
    path("obrigada/", obrigada, name="obrigada"),

    # retirada (dupla confirmação)
    path("pickup/", pickup_screen, name="pickup-screen"),
    path("pickup/check/", pickup_check, name="pickup-check"),
    path("pickup/confirm/", pickup_confirm, name="pickup-confirm"),

    # admin
    path("admin/", admin.site.urls),
]
