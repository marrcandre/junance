from cards.models import Card, Invoice


def family_cards(family):
    return Card.objects.filter(family=family, active=True)


def family_invoices(family):
    return Invoice.objects.filter(family=family).select_related("card")
