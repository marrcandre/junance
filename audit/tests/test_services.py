from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError

from audit.models import AuditEvent
from audit.services import cancel_event, delete_event
from identity.services import create_family
from ledger.models import Category
from ledger.services import create_account, create_category, record_expense

User = get_user_model()


@pytest.mark.django_db
def test_cancel_event_records_actor_reason_and_before_value():
    user = User.objects.create_user(username="ana")
    family = create_family(user, "Casa")
    account = create_account(family, "Conta")
    category = create_category(family, "Mercado", kind=Category.Kind.EXPENSE)
    expense = record_expense(
        user,
        family,
        account,
        category,
        Decimal("25.00"),
        transaction_date=date(2026, 1, 10),
        competence_date=date(2026, 1, 1),
    )

    audit_event = cancel_event(user, expense, reason="Lançamento duplicado")

    expense.refresh_from_db()
    assert expense.is_void is True
    assert audit_event.action == AuditEvent.Action.CANCEL
    assert audit_event.actor == user
    assert audit_event.reason == "Lançamento duplicado"
    assert audit_event.before["amount"] == "25.00"


@pytest.mark.django_db
def test_cannot_delete_financial_event_physically():
    user = User.objects.create_user(username="ana")
    family = create_family(user, "Casa")
    account = create_account(family, "Conta")
    category = create_category(family, "Mercado", kind=Category.Kind.EXPENSE)
    expense = record_expense(
        user,
        family,
        account,
        category,
        Decimal("25.00"),
        transaction_date=date(2026, 1, 10),
        competence_date=date(2026, 1, 1),
    )

    with pytest.raises(ValidationError):
        delete_event(user, expense, reason="Não apagar histórico")


@pytest.mark.django_db
def test_other_family_cannot_cancel_event():
    user = User.objects.create_user(username="ana")
    other_user = User.objects.create_user(username="bruno")
    family = create_family(user, "Casa")
    account = create_account(family, "Conta")
    category = create_category(family, "Mercado", kind=Category.Kind.EXPENSE)
    expense = record_expense(
        user,
        family,
        account,
        category,
        Decimal("25.00"),
        transaction_date=date(2026, 1, 10),
        competence_date=date(2026, 1, 1),
    )

    with pytest.raises(PermissionDenied):
        cancel_event(other_user, expense, reason="Tentativa")
