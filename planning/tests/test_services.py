from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from identity.services import create_family
from ledger.models import Category
from ledger.services import create_category
from planning.services import create_budget

User = get_user_model()


@pytest.mark.django_db
def test_create_budget_requires_family_category_and_decimal_amount():
    user = User.objects.create_user(username="ana")
    family = create_family(user, "Casa")
    category = create_category(family, "Mercado", kind=Category.Kind.EXPENSE)

    budget = create_budget(
        user,
        family,
        category,
        Decimal("100.00"),
        competence_date=date(2026, 2, 1),
    )

    assert budget.amount == Decimal("100.00")
    assert budget.family == family
