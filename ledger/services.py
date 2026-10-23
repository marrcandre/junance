from decimal import Decimal

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from audit.models import AuditEvent
from audit.services import cancel_event, record_audit_event
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


def _event_snapshot(event):
    return {
        "account_id": event.account_id,
        "category_id": event.category_id,
        "amount": str(event.amount),
        "transaction_date": event.transaction_date.isoformat(),
        "competence_date": event.competence_date.isoformat(),
        "paid_at": event.paid_at.isoformat() if event.paid_at else None,
        "description": event.description,
        "is_void": event.is_void,
    }


def _update_event(
    actor,
    event,
    *,
    account,
    category,
    amount,
    transaction_date,
    competence_date,
    description,
    paid_at,
    expected_kind,
):
    require_family_membership(actor, event.family)
    if event.is_void:
        raise ValidationError("Um lançamento cancelado não pode ser alterado.")
    amount = _ensure_event_inputs(
        actor,
        event.family,
        account,
        category,
        amount,
        expected_kind,
    )
    before = _event_snapshot(event)
    event.account = account
    event.category = category
    event.amount = amount
    event.transaction_date = transaction_date
    event.competence_date = competence_date
    event.description = description
    event.paid_at = paid_at
    event.full_clean()
    event.save()
    record_audit_event(
        actor,
        event.family,
        AuditEvent.Action.UPDATE,
        event,
        before=before,
        after=_event_snapshot(event),
    )
    return event


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
def update_income(
    actor,
    income,
    *,
    account,
    category,
    amount,
    transaction_date,
    competence_date,
    description="",
    paid_at=None,
):
    if not isinstance(income, Income):
        raise ValidationError("O evento não é uma receita.")
    return _update_event(
        actor,
        income,
        account=account,
        category=category,
        amount=amount,
        transaction_date=transaction_date,
        competence_date=competence_date,
        description=description,
        paid_at=paid_at,
        expected_kind=Category.Kind.INCOME,
    )


@transaction.atomic
def update_expense(
    actor,
    expense,
    *,
    account,
    category,
    amount,
    transaction_date,
    competence_date,
    description="",
    paid_at=None,
):
    if not isinstance(expense, Expense):
        raise ValidationError("O evento não é uma despesa.")
    return _update_event(
        actor,
        expense,
        account=account,
        category=category,
        amount=amount,
        transaction_date=transaction_date,
        competence_date=competence_date,
        description=description,
        paid_at=paid_at,
        expected_kind=Category.Kind.EXPENSE,
    )


@transaction.atomic
def cancel_financial_event(actor, event, *, reason):
    if not isinstance(event, (Income, Expense)):
        raise ValidationError("O evento não é uma receita ou despesa.")
    return cancel_event(actor, event, reason=reason)


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
