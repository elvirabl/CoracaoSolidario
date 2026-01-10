from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("doar/", views.doar, name="doar"),
    path("receber/", views.receber, name="receber"),

    path("retirar/<str:pickup_code>/", views.retirar, name="retirar"),
    path("retirar/<str:pickup_code>/confirmar/", views.confirmar_retirada, name="confirmar_retirada"),

    path("qr/<str:pickup_code>.png", views.qr_pickup_png, name="qr_pickup_png"),
]
