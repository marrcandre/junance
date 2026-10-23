from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from identity.services import create_family
from ledger.models import Account, Category

User = get_user_model()


@pytest.mark.django_db
def test_account_and_category_are_owned_by_family():
    user = User.objects.create_user(username="ana")
    family = create_family(user, "Casa")

    account = Account.objects.create(
        family=family,
        name="Carteira",
        initial_balance=Decimal("1.20"),
    )
    category = Category.objects.create(family=family, name="Salário", kind=Category.Kind.INCOME)

    assert account.initial_balance == Decimal("1.20")
    assert category.family == family
