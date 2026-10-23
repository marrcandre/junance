from calendar import monthrange
from datetime import date
from decimal import Decimal

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from cards.models import Installment, Invoice, InvoicePayment, Purchase
from identity.services import require_family_membership
from ledger.models import Category


def _month_offset(value, offset):
    month_index = value.year * 12 + value.month - 1 + offset
    year, month_index = divmod(month_index, 12)
    return date(year, month_index + 1, 1)


def _due_date(competence_date, due_day):
    next_month = _month_offset(competence_date, 1)
    day = min(due_day, monthrange(next_month.year, next_month.month)[1])
    return next_month.replace(day=day)


def _ensure_family(family, obj):
    if obj.family_id != family.id:
        raise PermissionDenied("O objeto não pertence à família autorizada.")


def _positive_amount(amount):
    if not isinstance(amount, Decimal):
        amount = Decimal(str(amount))
    if amount <= Decimal("0.00"):
        raise ValidationError("O valor deve ser positivo.")
    return amount


@transaction.atomic
def record_card_purchase(
    actor,
    family,
    card,
    category,
    amount,
    *,
    purchase_date,
    installments=1,
    description="",
):
    require_family_membership(actor, family)
    _ensure_family(family, card)
    _ensure_family(family, category)
    if category.kind != Category.Kind.EXPENSE:
        raise ValidationError("A compra precisa usar uma categoria de despesa.")
    if installments < 1:
        raise ValidationError("A compra precisa ter ao menos uma parcela.")
    amount = _positive_amount(amount)
    purchase = Purchase.objects.create(
        family=family,
        card=card,
        category=category,
        amount=amount,
        purchase_date=purchase_date,
        description=description,
        installments_count=installments,
    )
    cents = int(amount * 100)
    base_cents, remainder = divmod(cents, installments)
    for number in range(1, installments + 1):
        competence_date = _month_offset(purchase_date, number - 1)
        invoice, _ = Invoice.objects.get_or_create(
            family=family,
            card=card,
            competence_date=competence_date,
            defaults={"due_date": _due_date(competence_date, card.due_day)},
        )
        installment_amount = Decimal(base_cents + (1 if number <= remainder else 0)) / 100
        Installment.objects.create(
            purchase=purchase,
            invoice=invoice,
            number=number,
            amount=installment_amount,
        )
    return purchase


@transaction.atomic
def settle_invoice(actor, invoice, account, amount, *, paid_at):
    require_family_membership(actor, invoice.family)
    _ensure_family(invoice.family, account)
    amount = _positive_amount(amount)
    outstanding = invoice.total_open
    if amount > outstanding:
        raise ValidationError("O pagamento excede o valor aberto da fatura.")
    payment = InvoicePayment.objects.create(
        invoice=invoice,
        account=account,
        amount=amount,
        paid_at=paid_at,
    )
    if amount == outstanding:
        invoice.installments.filter(status=Installment.Status.OPEN).update(
            status=Installment.Status.PAID
        )
        invoice.status = Invoice.Status.PAID
        invoice.save(update_fields=["status"])
    return payment
