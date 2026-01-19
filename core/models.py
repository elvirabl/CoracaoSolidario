import uuid
from django.db import models
#from django.utils import timezone


class ReferencePost(models.Model):
    name = models.CharField("Nome do posto", max_length=150)
    city = models.CharField("Cidade", max_length=100)

    neighborhood_coverage = models.CharField(
        "Bairros atendidos",
        max_length=200
    )

    can_receive_donations = models.BooleanField(default=True)
    public = models.BooleanField(default=True)

    contact_name = models.CharField(
        "Responsável",
        max_length=100
    )

    contact_phone = models.CharField(
        "Telefone",
        max_length=30
    )

    type = models.CharField(
        "Tipo de posto",
        max_length=20,
        choices=[
            ("ubs", "UBS"),
            ("cras", "CRAS"),
            ("hospital", "Hospital"),
            ("ong", "ONG"),
        ]
    )

    def __str__(self):
        return f"{self.name} - {self.city}"


class Donor(models.Model):
    KIT_CHOICES = (
        ("BASICO", "Kit Básico"),
        ("ALERGIA", "Kit Alergia"),
    )

    name = models.CharField("Nome", max_length=120)
    whatsapp = models.CharField("WhatsApp", max_length=20)

    kit_type = models.CharField(
        "Tipo de kit doado",
        max_length=30,
        choices=KIT_CHOICES
    )

    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_kit_type_display()})"

class Receiver(models.Model):
    KIT_CHOICES = Donor.KIT_CHOICES

    name = models.CharField("Nome", max_length=120)
    whatsapp = models.CharField("WhatsApp", max_length=20)
    city = models.CharField("Cidade", max_length=100)
    neighborhood = models.CharField("Bairro", max_length=100)

    needed_kit = models.CharField(
        "Tipo de kit necessário",
        max_length=30,
        choices=KIT_CHOICES
    )

    reference_post = models.ForeignKey(
        ReferencePost,
        on_delete=models.PROTECT,
        verbose_name="Posto de referência"
    )

    is_breast_cancer_patient = models.BooleanField(
        "Paciente com câncer de mama",
        default=False
    )

    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_needed_kit_display()})"


class Match(models.Model):
    donor = models.ForeignKey(
        Donor,
        on_delete=models.PROTECT,
        verbose_name="Doador"
    )

    receiver = models.ForeignKey(
        Receiver,
        on_delete=models.PROTECT,
        verbose_name="Receptora"
    )

    reference_post = models.ForeignKey(
        ReferencePost,
        on_delete=models.PROTECT,
        verbose_name="Posto de retirada"
    )

    pickup_code = models.CharField(
        "Código de retirada",
        max_length=20,
        unique=True,
        blank=True
    )

    is_completed = models.BooleanField(
        "Entrega concluída",
        default=False
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pickup_code:
            while True:
                code = f"CS-{uuid.uuid4().hex[:8].upper()}"
                if not Match.objects.filter(pickup_code=code).exists():
                    self.pickup_code = code
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        status = "ENTREGUE" if self.is_completed else "PENDENTE"
        return f"{self.receiver.name} ← {self.donor.name} ({self.pickup_code}) [{status}]"
