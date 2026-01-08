def send_whatsapp_message(phone, message):
    """
    Mock de envio de WhatsApp.
    Depois conectamos API oficial.
    """
    print(f"[WHATSAPP MOCK] {phone}: {message}")
    return True
