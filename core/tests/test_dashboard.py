import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from identity.services import create_family
from ledger.services import create_account

User = get_user_model()


@pytest.mark.django_db
def test_dashboard_returns_successful_response(client):
    response = client.get(reverse("core:dashboard"))

    assert response.status_code == 200
    assert "Junance" in response.content.decode()


@pytest.mark.django_db
def test_dashboard_guides_authenticated_user_without_family(client):
    user = User.objects.create_user(username="ana")
    client.force_login(user)

    response = client.get(reverse("core:dashboard"))

    assert response.status_code == 200
    assert "Crie sua primeira família" in response.content.decode()
    assert reverse("identity:family_create") in response.content.decode()


@pytest.mark.django_db
def test_dashboard_guides_family_without_accounts_to_create_account(client):
    user = User.objects.create_user(username="ana")
    family = create_family(user, "Casa")
    client.force_login(user)

    response = client.get(reverse("core:dashboard"))

    assert response.status_code == 200
    assert family.name in response.content.decode()
    assert "Cadastre sua primeira conta" in response.content.decode()
    assert reverse("ledger:account_create") in response.content.decode()


@pytest.mark.django_db
def test_dashboard_shows_account_and_monthly_summary(client):
    user = User.objects.create_user(username="ana")
    family = create_family(user, "Casa")
    account = create_account(family, "Conta principal")
    client.force_login(user)

    response = client.get(reverse("core:dashboard"))
    content = response.content.decode()

    assert response.status_code == 200
    assert account.name in content
    assert "Receitas do mês" in content
    assert "Despesas do mês" in content


@pytest.mark.django_db
def test_dashboard_navigation_contains_links_to_main_modules(client):
    user = User.objects.create_user(username="ana")
    client.force_login(user)

    response = client.get(reverse("core:dashboard"))
    content = response.content.decode()

    for route_name in (
        "core:dashboard",
        "identity:family_list",
        "ledger:account_list",
        "ledger:transaction_list",
        "cards:card_list",
        "imports:upload",
        "planning:monthly",
        "investments:position_list",
    ):
        assert reverse(route_name) in content
