from decimal import Decimal

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from identity.services import require_family_membership
from ledger.models import Account, Category, Expense, Income, Transfer


def create_account(family, name, kind=Account.Kind.CHECKING, initial_balance=Decimal("0.00")):
    account = Account(
        family=family,
        name=name,
        kind=kind,
        initial_balance=initial_balance,
    )
    account.full_clean()
    account.save()
    return account


def create_category(family, name, kind):
    category = Category(family=family, name=name, kind=kind)
    category.full_clean()
    category.save()
    return category


def _ensure_family_object(family, obj):
    if obj.family_id != family.id:
        raise PermissionDenied("O objeto não pertence à família autorizada.")


def _ensure_amount(amount):
    if not isinstance(amount, Decimal):
        amount = Decimal(str(amount))
    if amount <= Decimal("0.00"):
        raise ValidationError("O valor deve ser positivo.")
    return amount


def _ensure_event_inputs(actor, family, account, category, amount, expected_kind):
    require_family_membership(actor, family)
    _ensure_family_object(family, account)
    _ensure_family_object(family, category)
    if category.kind != expected_kind:
        raise ValidationError("A categoria não corresponde ao tipo da movimentação.")
    return _ensure_amount(amount)


@transaction.atomic
def record_income(
    actor,
    family,
    account,
    category,
    amount,
    *,
    transaction_date,
    competence_date,
    description="",
    paid_at=None,
):
    amount = _ensure_event_inputs(actor, family, account, category, amount, Category.Kind.INCOME)
    income = Income(
        family=family,
        account=account,
        category=category,
        amount=amount,
        transaction_date=transaction_date,
        competence_date=competence_date,
        paid_at=paid_at,
        description=description,
    )
    income.full_clean()
    income.save()
    return income


@transaction.atomic
def record_expense(
    actor,
    family,
    account,
    category,
    amount,
    *,
    transaction_date,
    competence_date,
    description="",
    paid_at=None,
):
    amount = _ensure_event_inputs(actor, family, account, category, amount, Category.Kind.EXPENSE)
    expense = Expense(
        family=family,
        account=account,
        category=category,
        amount=amount,
        transaction_date=transaction_date,
        competence_date=competence_date,
        paid_at=paid_at,
        description=description,
    )
    expense.full_clean()
    expense.save()
    return expense


@transaction.atomic
def record_transfer(
    actor,
    family,
    source_account,
    destination_account,
    amount,
    *,
    transaction_date,
    competence_date,
    description="",
):
    require_family_membership(actor, family)
    _ensure_family_object(family, source_account)
    _ensure_family_object(family, destination_account)
    if source_account.pk == destination_account.pk:
        raise ValidationError("A transferência precisa de contas diferentes.")
    transfer = Transfer(
        family=family,
        source_account=source_account,
        destination_account=destination_account,
        amount=_ensure_amount(amount),
        transaction_date=transaction_date,
        competence_date=competence_date,
        description=description,
    )
    transfer.full_clean()
    transfer.save()
    return transfer
