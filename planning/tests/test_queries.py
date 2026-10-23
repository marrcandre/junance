from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from identity.services import create_family
from ledger.models import Category
from ledger.services import (
    create_account,
    create_category,
    record_expense,
    record_income,
    record_transfer,
)
from planning.models import Budget
from planning.queries import budget_progress, monthly_summary

User = get_user_model()


@pytest.mark.django_db
def test_monthly_summary_uses_competence_and_excludes_transfers():
    user = User.objects.create_user(username="ana")
    family = create_family(user, "Casa")
    account = create_account(family, "Conta")
    destination = create_account(family, "Poupança")
    expense_category = create_category(family, "Mercado", kind=Category.Kind.EXPENSE)
    income_category = create_category(family, "Salário", kind=Category.Kind.INCOME)
    record_expense(
        user,
        family,
        account,
        expense_category,
        Decimal("40.00"),
        transaction_date=date(2026, 2, 10),
        competence_date=date(2026, 2, 1),
    )
    record_income(
        user,
        family,
        account,
        income_category,
        Decimal("100.00"),
        transaction_date=date(2026, 2, 28),
        competence_date=date(2026, 2, 1),
    )
    record_transfer(
        user,
        family,
        account,
        destination,
        Decimal("200.00"),
        transaction_date=date(2026, 2, 15),
        competence_date=date(2026, 2, 1),
    )

    assert monthly_summary(family, date(2026, 2, 1)) == {
        "income": Decimal("100.00"),
        "expense": Decimal("40.00"),
        "balance": Decimal("60.00"),
    }


@pytest.mark.django_db
def test_budget_progress_is_scoped_to_family_and_competence():
    user = User.objects.create_user(username="ana")
    other_user = User.objects.create_user(username="bruno")
    family = create_family(user, "Casa")
    other_family = create_family(other_user, "Outra")
    category = create_category(family, "Mercado", kind=Category.Kind.EXPENSE)
    other_category = create_category(other_family, "Mercado", kind=Category.Kind.EXPENSE)
    account = create_account(family, "Conta")
    other_account = create_account(other_family, "Conta")
    Budget.objects.create(
        family=family,
        category=category,
        competence_date=date(2026, 2, 1),
        amount=Decimal("100.00"),
    )
    Budget.objects.create(
        family=other_family,
        category=other_category,
        competence_date=date(2026, 2, 1),
        amount=Decimal("900.00"),
    )
    record_expense(
        user,
        family,
        account,
        category,
        Decimal("40.00"),
        transaction_date=date(2026, 2, 10),
        competence_date=date(2026, 2, 1),
    )
    record_expense(
        other_user,
        other_family,
        other_account,
        other_category,
        Decimal("800.00"),
        transaction_date=date(2026, 2, 10),
        competence_date=date(2026, 2, 1),
    )

    assert budget_progress(family, date(2026, 2, 1), category) == {
        "planned": Decimal("100.00"),
        "spent": Decimal("40.00"),
        "remaining": Decimal("60.00"),
    }
