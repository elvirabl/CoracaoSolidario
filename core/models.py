from django.db import models
import random
import string

def generate_pickup_code():
    """
    Gera um código de retirada no formato CS-1234.
    """
    digits = ''.join(random.choices(string.digits, k=4))
    return f"CS-{digits}"


class ReferencePost(models.Model):
    TYPE_CHOICES = [
        ('UBS', 'UBS'),
        ('CRAS', 'CRAS'),
        ('ASSOCIACAO', 'Associação'),
        ('ONG', 'ONG'),
        ('OUTRO', 'Outro'),
    ]

    name = models.CharField("Nome do posto/entidade", max_length=150)
    type = models.CharField("Tipo", max_length=20, choices=TYPE_CHOICES)
    address = models.CharField("Endereço", max_length=255, blank=True)
    city = models.CharField("Cidade", max_length=100)
    neighborhood_coverage = models.CharField(
        "Bairros atendidos (texto livre)", max_length=255, blank=True
    )
    phone = models.CharField("Telefone/WhatsApp", max_length=50, blank=True)
    contact_name = models.CharField("Responsável", max_length=100, blank=True)
    opening_hours = models.CharField("Dias/horários de atendimento", max_length=255, blank=True)
    can_receive_donations = models.BooleanField("Recebe doações neste local?", default=False)
    public = models.BooleanField("Pode aparecer no site/app?", default=True)

    def __str__(self):
        return f"{self.name} - {self.city}"


class Donor(models.Model):
    KIT_CHOICES = [
        ('KIT_BASICO', 'Kit Básico'),
        ('KIT_BASICO_ALERGICA', 'Kit Básico Alérgica'),
        ('KIT_COMPLETO', 'Kit Completo'),
        ('KIT_COMPLETO_ALERGICA', 'Kit Completo Alérgica'),
    ]

    name = models.CharField("Nome completo", max_length=150)
    whatsapp = models.CharField("WhatsApp", max_length=50)
    email = models.EmailField("E-mail", blank=True)
    city = models.CharField("Cidade", max_length=100)
    neighborhood = models.CharField("Bairro", max_length=100)
    allow_whatsapp = models.BooleanField("Autoriza contato por WhatsApp?", default=True)
    preferred_kit = models.CharField(
        "Tipo de kit que deseja doar",
        max_length=40,
        choices=KIT_CHOICES,
        blank=True,
    )
    reference_post = models.ForeignKey(
        ReferencePost,
        verbose_name="Posto de referência do bairro",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    active = models.BooleanField("Ativo", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Doadora"
        verbose_name_plural = "Doadoras"

    def __str__(self):
        return f"{self.name} ({self.city} - {self.neighborhood})"


class Receiver(models.Model):
    KIT_CHOICES = [
        ('KIT_BASICO', 'Kit Básico'),
        ('KIT_BASICO_ALERGICA', 'Kit Básico Alérgica'),
        ('KIT_COMPLETO', 'Kit Completo'),
        ('KIT_COMPLETO_ALERGICA', 'Kit Completo Alérgica'),
    ]

    name = models.CharField("Nome", max_length=150)
    whatsapp = models.CharField("WhatsApp", max_length=50)
    city = models.CharField("Cidade", max_length=100)
    neighborhood = models.CharField("Bairro", max_length=100)
    is_breast_cancer_patient = models.BooleanField(
        "Pós-cirurgia / em tratamento de câncer de mama",
        default=True,
    )
    needed_kit = models.CharField(
        "Kit necessário",
        max_length=40,
        choices=KIT_CHOICES,
    )
    reference_post = models.ForeignKey(
        ReferencePost,
        verbose_name="Posto de referência do bairro",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    notes = models.TextField("Observações internas", blank=True)
    active = models.BooleanField("Ativa", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Receptora"
        verbose_name_plural = "Receptoras"

    def __str__(self):
        return f"{self.name} ({self.city} - {self.neighborhood})"


class Match(models.Model):
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('CONFIRMADO', 'Confirmado'),
        ('ENTREGUE', 'Entregue'),
        ('CANCELADO', 'Cancelado'),
    ]

    KIT_CHOICES = [
        ('KIT_BASICO', 'Kit Básico'),
        ('KIT_BASICO_ALERGICA', 'Kit Básico Alérgica'),
        ('KIT_COMPLETO', 'Kit Completo'),
        ('KIT_COMPLETO_ALERGICA', 'Kit Completo Alérgica'),
    ]

    donor = models.ForeignKey(
        'Donor',
        verbose_name="Doadora",
        on_delete=models.CASCADE,
    )
    receiver = models.ForeignKey(
        'Receiver',
        verbose_name="Receptora",
        on_delete=models.CASCADE,
    )
    kit_type = models.CharField(
        "Tipo de Kit",
        max_length=40,
        choices=KIT_CHOICES,
    )
    quantity = models.PositiveIntegerField("Quantidade", default=1)
    status = models.CharField(
        "Status",
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDENTE',
    )

    # 🌸 Campos do código de retirada
    pickup_code = models.CharField(
        "Código de retirada",
        max_length=10,
        unique=True,
        blank=True
    )
    pickup_used = models.BooleanField("Código já utilizado?", default=False)
    pickup_used_at = models.DateTimeField("Data/hora da retirada", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField("Observações internas", blank=True)

    class Meta:
        verbose_name = "Match (Doação)"
        verbose_name_plural = "Matches (Doações)"

    def __str__(self):
        return f"{self.donor.name} → {self.receiver.name} ({self.kit_type})"

    def save(self, *args, **kwargs):
        """
        Gera automaticamente um código de retirada se ainda não houver.
        Garante unicidade tentando novos códigos até achar um livre.
        """
        if not self.pickup_code:
            while True:
                code = generate_pickup_code()
                if not Match.objects.filter(pickup_code=code).exists():
                    self.pickup_code = code
                    break
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Match (Doação)"
        verbose_name_plural = "Matches (Doações)"

    def __str__(self):
        return f"{self.donor.name} → {self.receiver.name} ({self.kit_type})"
