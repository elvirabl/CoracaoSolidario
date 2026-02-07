from django.utils import timezone

def notify_match(match):
    """
    Envia/gera a mensagem de notificação de Match sem depender de campos antigos.
    Fonte do kit:
      - donor.kit_type (doadora)
      - receiver.needed_kit (receptora)
    """

    # Evita duplicar notificação
    if getattr(match, "notified", False):
        return

    donor = match.donor
    receiver = match.receiver
    post = match.reference_post

    # Tipo de kit (compatível com seu modelo)
    kit_label = donor.get_kit_type_display()  # ✅ CERTO pro seu Donor

    # Mensagem base (você adapta pro WhatsApp depois)
    message = (
        f"✅ Match gerado!\n"
        f"📦 Kit: {kit_label}\n"
        f"🔑 Código de retirada: {match.pickup_code}\n"
        f"🏥 Posto: {post.name} - {post.city}\n"
        f"👤 Doadora: {donor.name}\n"
        f"🤍 Receptora: {receiver.name}\n"
    )

    # Aqui você chamaria seu envio real (quando quiser):
    # send_whatsapp(donor.whatsapp, message)
    # send_whatsapp(receiver.whatsapp, message)

    # Marca como notificado (se você adicionou notified/notified_at no model)
    if hasattr(match, "notified"):
        match.notified = True
    if hasattr(match, "notified_at"):
        match.notified_at = timezone.now()

    # Salva somente os campos que existem
    update_fields = []
    if hasattr(match, "notified"):
        update_fields.append("notified")
    if hasattr(match, "notified_at"):
        update_fields.append("notified_at")

    if update_fields:
        match.save(update_fields=update_fields)

    return message  # útil pra debug