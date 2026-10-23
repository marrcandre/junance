from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from identity.services import create_family
from investments.queries import calculate_return
from investments.services import record_contribution

User = get_user_model()


@pytest.mark.django_db
def test_return_is_calculated_from_position_value_not_income_expense():
    user = User.objects.create_user(username="ana")
    family = create_family(user, "Casa")
    position = record_contribution(
        user,
        family,
        "Fundo",
        Decimal("10.00"),
        Decimal("100.00"),
        transaction_date=date(2026, 1, 1),
    )

    assert calculate_return(position, Decimal("120.00")) == Decimal("20.00")
