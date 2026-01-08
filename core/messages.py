# core/messages.py
# Textos padrão para envio via WhatsApp (fase manual / futura automação)


def whatsapp_donor_confirmation(name, kit_label):
    """
    Mensagem de confirmação para DOADORA após cadastro ou match.
    kit_label = donor.get_preferred_kit_display()
    """
    return (
        f"Olá {name}! 💗\n"
        f"Aqui é do *Coração Solidário*.\n"
        f"Recebemos o seu cadastro como doadora e ficamos muito felizes com a sua disponibilidade em ajudar.\n"
        f"Assim que encontrarmos alguém compatível com o kit ({kit_label}) e definirmos o posto de referência, "
        f"vamos te avisar por aqui com todos os detalhes.\n\n"
        f"Obrigada por colocar amor em movimento. 🌷"
    )


def whatsapp_receiver_confirmation(name):
    """
    Mensagem de confirmação para RECEPTORA (após cadastro do pedido).
    """
    return (
        f"Oi, {name}! 💗\n"
        f"Aqui é do *Coração Solidário*.\n"
        f"Seu pedido foi cadastrado com sucesso.\n"
        f"Agora vamos procurar uma doação compatível com o kit que você precisa e, assim que houver um match, "
        f"vamos te avisar com o posto de referência e o seu código de retirada.\n\n"
        f"Estamos torcendo para que essa ajuda chegue logo até você. 🌻"
    )


def whatsapp_receiver_match(name, reference_post, address, withdrawal_code):
    """
    Mensagem para RECEPTORA quando já existe match + posto + código.
    """
    return (
        f"Oi, {name}! 💗\n"
        f"Boas notícias: encontramos uma doação compatível com o kit que você pediu! 🎉\n\n"
        f"Você poderá retirar em:\n"
        f"Posto: {reference_post}\n"
        f"Endereço: {address}\n\n"
        f"📌 Código de retirada: {withdrawal_code}\n\n"
        f"Leve este código e um documento com foto até o posto de referência.\n"
        f"Qualquer dúvida, pode responder esta mensagem.\n\n"
        f"Um abraço do Coração Solidário. 🫶"
    )


def whatsapp_donor_after_match(name):
    """
    Mensagem opcional para DOADORA depois que a doação dela foi utilizada.
    """
    return (
        f"Oi, {name}! 💗\n"
        f"Passando pra te contar que a sua doação já foi pareada com uma pessoa que precisava muito desse kit.\n"
        f"Ela vai retirar no posto de referência nos próximos dias.\n\n"
        f"Obrigada por fazer parte dessa corrente de cuidado.\n"
        f"Hoje você fez a diferença na vida de alguém. 🌸"
    )
