from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError

from identity.services import create_family
from ledger.models import Category, Expense, Income, Transfer
from ledger.services import (
    cancel_financial_event,
    create_account,
    create_category,
    record_expense,
    record_income,
    record_transfer,
    update_expense,
    update_income,
)

User = get_user_model()


@pytest.mark.django_db
def test_record_income_and_expense_preserve_decimal_and_dates():
    user = User.objects.create_user(username="ana")
    family = create_family(user, "Casa")
    account = create_account(family, "Conta corrente", initial_balance=Decimal("100.00"))
    category = create_category(family, "Mercado", kind=Category.Kind.EXPENSE)
    income_category = create_category(family, "Salário", kind=Category.Kind.INCOME)

    income = record_income(
        user,
        family,
        account,
        income_category,
        Decimal("2500.10"),
        transaction_date=date(2026, 1, 5),
        competence_date=date(2026, 1, 1),
    )
    expense = record_expense(
        user,
        family,
        account,
        category,
        Decimal("42.35"),
        transaction_date=date(2026, 1, 8),
        competence_date=date(2026, 1, 1),
    )

    assert income.amount == Decimal("2500.10")
    assert expense.amount == Decimal("42.35")
    assert income.competence_date == date(2026, 1, 1)
    assert Income.objects.filter(family=family).count() == 1
    assert Expense.objects.filter(family=family).count() == 1


@pytest.mark.django_db
def test_transfer_requires_positive_amount_and_accounts_from_same_family():
    user = User.objects.create_user(username="ana")
    other_user = User.objects.create_user(username="bruno")
    family = create_family(user, "Casa")
    other_family = create_family(other_user, "Outra")
    source = create_account(family, "Origem")
    destination = create_account(family, "Destino")
    foreign = create_account(other_family, "Estrangeira")

    transfer = record_transfer(
        user,
        family,
        source,
        destination,
        Decimal("10.00"),
        transaction_date=date(2026, 1, 10),
        competence_date=date(2026, 1, 1),
    )

    assert transfer.amount == Decimal("10.00")
    assert Transfer.objects.filter(family=family).count() == 1

    with pytest.raises(ValidationError):
        record_transfer(
            user,
            family,
            source,
            source,
            Decimal("10.00"),
            transaction_date=date(2026, 1, 10),
            competence_date=date(2026, 1, 1),
        )

    with pytest.raises(PermissionDenied):
        record_transfer(
            user,
            family,
            source,
            foreign,
            Decimal("10.00"),
            transaction_date=date(2026, 1, 10),
            competence_date=date(2026, 1, 1),
        )


@pytest.mark.django_db
def test_financial_entities_require_family_authorization():
    user = User.objects.create_user(username="ana")
    other_user = User.objects.create_user(username="bruno")
    family = create_family(user, "Casa")
    other_family = create_family(other_user, "Outra")
    account = create_account(other_family, "Conta de Bruno")
    category = create_category(other_family, "Categoria de Bruno", kind=Category.Kind.EXPENSE)

    with pytest.raises(PermissionDenied):
        record_expense(
            user,
            family,
            account,
            category,
            Decimal("10.00"),
            transaction_date=date(2026, 1, 10),
            competence_date=date(2026, 1, 1),
        )


@pytest.mark.django_db
def test_update_income_changes_editable_fields_and_preserves_income_type():
    user = User.objects.create_user(username="ana")
    family = create_family(user, "Casa")
    account = create_account(family, "Conta")
    income_category = create_category(family, "Salário", kind=Category.Kind.INCOME)
    other_category = create_category(family, "Bônus", kind=Category.Kind.INCOME)
    income = record_income(
        user,
        family,
        account,
        income_category,
        Decimal("100.00"),
        transaction_date=date(2026, 1, 5),
        competence_date=date(2026, 1, 1),
        description="Salário",
    )

    updated = update_income(
        user,
        income,
        account=account,
        category=other_category,
        amount=Decimal("125.50"),
        transaction_date=date(2026, 1, 6),
        competence_date=date(2026, 1, 1),
        description="Bônus mensal",
        paid_at=date(2026, 1, 6),
    )

    assert updated.pk == income.pk
    assert updated.category == other_category
    assert updated.amount == Decimal("125.50")
    assert updated.description == "Bônus mensal"
    assert updated.paid_at == date(2026, 1, 6)


@pytest.mark.django_db
def test_update_expense_rejects_category_from_another_family():
    user = User.objects.create_user(username="ana")
    other_user = User.objects.create_user(username="bruno")
    family = create_family(user, "Casa")
    other_family = create_family(other_user, "Outra")
    account = create_account(family, "Conta")
    category = create_category(family, "Mercado", kind=Category.Kind.EXPENSE)
    foreign_category = create_category(other_family, "Mercado", kind=Category.Kind.EXPENSE)
    expense = record_expense(
        user,
        family,
        account,
        category,
        Decimal("20.00"),
        transaction_date=date(2026, 1, 5),
        competence_date=date(2026, 1, 1),
    )

    with pytest.raises(PermissionDenied):
        update_expense(
            user,
            expense,
            account=account,
            category=foreign_category,
            amount=Decimal("25.00"),
            transaction_date=date(2026, 1, 6),
            competence_date=date(2026, 1, 1),
            description="Tentativa",
            paid_at=None,
        )


@pytest.mark.django_db
def test_cancel_financial_event_voids_event_and_creates_audit_record():
    user = User.objects.create_user(username="ana")
    family = create_family(user, "Casa")
    account = create_account(family, "Conta")
    category = create_category(family, "Mercado", kind=Category.Kind.EXPENSE)
    expense = record_expense(
        user,
        family,
        account,
        category,
        Decimal("20.00"),
        transaction_date=date(2026, 1, 5),
        competence_date=date(2026, 1, 1),
    )

    audit_event = cancel_financial_event(user, expense, reason="Lançamento duplicado")

    expense.refresh_from_db()
    assert expense.is_void is True
    assert audit_event.reason == "Lançamento duplicado"
