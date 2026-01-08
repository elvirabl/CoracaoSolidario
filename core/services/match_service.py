def create_match(donor, receiver):
    """
    Cria um Match válido.
    O tipo de kit vem do donor / receiver, não do Match.
    """
    return {
        "donor": donor,
        "receiver": receiver,
        "kit": donor.get_preferred_kit_display()
    }