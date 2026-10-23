from decimal import Decimal

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from identity.services import require_family_membership
from investments.models import InvestmentPosition, InvestmentTransaction


def _positive(value):
    value = value if isinstance(value, Decimal) else Decimal(str(value))
    if value <= Decimal("0"):
        raise ValidationError("O valor deve ser positivo.")
    return value


@transaction.atomic
def record_contribution(actor, family, asset_name, quantity, amount, *, transaction_date):
    require_family_membership(actor, family)
    quantity = _positive(quantity)
    amount = _positive(amount)
    position, _ = InvestmentPosition.objects.get_or_create(
        family=family,
        asset_name=asset_name,
        defaults={"quantity": Decimal("0.00000000"), "cost_basis": Decimal("0.00")},
    )
    position.quantity += quantity
    position.cost_basis += amount
    position.save(update_fields=["quantity", "cost_basis"])
    InvestmentTransaction.objects.create(
        position=position,
        kind=InvestmentTransaction.Kind.CONTRIBUTION,
        quantity=quantity,
        amount=amount,
        transaction_date=transaction_date,
    )
    return position


@transaction.atomic
def record_withdrawal(actor, family, position, quantity, amount, *, transaction_date):
    require_family_membership(actor, family)
    if position.family_id != family.id:
        raise PermissionDenied("A posição não pertence à família autorizada.")
    quantity = _positive(quantity)
    amount = _positive(amount)
    if quantity > position.quantity:
        raise ValidationError("O resgate excede a quantidade da posição.")
    average_price = position.cost_basis / position.quantity
    position.quantity -= quantity
    position.cost_basis -= average_price * quantity
    position.save(update_fields=["quantity", "cost_basis"])
    return InvestmentTransaction.objects.create(
        position=position,
        kind=InvestmentTransaction.Kind.WITHDRAWAL,
        quantity=quantity,
        amount=amount,
        transaction_date=transaction_date,
    )
