from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from identity.services import create_family
from ledger.models import Category
from ledger.services import create_account, create_category

User = get_user_model()


@pytest.mark.django_db
def test_account_list_does_not_reveal_another_family(client):
    user = User.objects.create_user(username="ana")
    other_user = User.objects.create_user(username="bruno")
    family = create_family(user, "Casa")
    other_family = create_family(other_user, "Outra")
    create_account(family, "Conta de Ana")
    create_account(other_family, "Conta de Bruno")
    client.force_login(user)

    response = client.get(reverse("ledger:account_list"))
    content = response.content.decode()

    assert response.status_code == 200
    assert "Conta de Ana" in content
    assert "Conta de Bruno" not in content


@pytest.mark.django_db
def test_transaction_form_records_expense_in_active_family(client):
    user = User.objects.create_user(username="ana")
    family = create_family(user, "Casa")
    account = create_account(family, "Conta")
    category = create_category(family, "Mercado", kind=Category.Kind.EXPENSE)
    client.force_login(user)

    response = client.post(
        reverse("ledger:transaction_create"),
        {
            "kind": "expense",
            "account": account.id,
            "category": category.id,
            "amount": "12.50",
            "transaction_date": "2026-01-10",
            "competence_date": "2026-01-01",
            "description": "Feira",
        },
    )

    assert response.status_code == 302
    assert response.url == reverse("ledger:transaction_list")
    assert account.expenses.get().amount == Decimal("12.50")
