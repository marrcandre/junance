from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from identity.services import create_family
from ledger.models import Category
from ledger.queries import family_expenses, monthly_totals
from ledger.services import create_account, create_category, record_expense, record_transfer

User = get_user_model()


@pytest.mark.django_db
def test_queries_filter_by_family_and_competence_without_counting_transfer():
    user = User.objects.create_user(username="ana")
    other_user = User.objects.create_user(username="bruno")
    family = create_family(user, "Casa")
    other_family = create_family(other_user, "Outra")
    account = create_account(family, "Conta")
    other_account = create_account(other_family, "Outra conta")
    category = create_category(family, "Mercado", kind=Category.Kind.EXPENSE)
    other_category = create_category(other_family, "Outra", kind=Category.Kind.EXPENSE)
    record_expense(
        user,
        family,
        account,
        category,
        Decimal("30.00"),
        transaction_date=date(2026, 1, 4),
        competence_date=date(2026, 1, 1),
    )
    record_expense(
        other_user,
        other_family,
        other_account,
        other_category,
        Decimal("90.00"),
        transaction_date=date(2026, 1, 4),
        competence_date=date(2026, 1, 1),
    )
    record_transfer(
        user,
        family,
        account,
        create_account(family, "Poupança"),
        Decimal("100.00"),
        transaction_date=date(2026, 1, 5),
        competence_date=date(2026, 1, 1),
    )

    expenses = list(family_expenses(family, date(2026, 1, 1), date(2026, 1, 31)))
    assert len(expenses) == 1
    assert expenses[0].amount == Decimal("30.00")
    assert monthly_totals(family, date(2026, 1, 1)) == {
        "income": Decimal("0.00"),
        "expense": Decimal("30.00"),
    }
