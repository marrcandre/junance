import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from identity.services import create_family
from ledger.models import Category
from ledger.services import create_account, create_category, record_expense, record_income

User = get_user_model()


@pytest.mark.django_db
def test_monthly_report_requires_family_context(client):
    user = User.objects.create_user(username="ana")
    create_family(user, "Casa")
    client.force_login(user)

    response = client.get(reverse("planning:monthly"), {"month": "2026-02-01"})

    assert response.status_code == 200
    assert "Resumo mensal" in response.content.decode()


@pytest.mark.django_db
def test_monthly_report_page_shows_selected_month_entries_only(client):
    user = User.objects.create_user(username="ana")
    family = create_family(user, "Casa")
    account = create_account(family, "Conta")
    income_category = create_category(family, "Salário", kind=Category.Kind.INCOME)
    expense_category = create_category(family, "Mercado", kind=Category.Kind.EXPENSE)
    record_income(
        user,
        family,
        account,
        income_category,
        "100.00",
        transaction_date="2026-02-05",
        competence_date="2026-02-01",
        description="Entrada selecionada",
    )
    record_expense(
        user,
        family,
        account,
        expense_category,
        "40.00",
        transaction_date="2026-02-10",
        competence_date="2026-02-01",
        description="Despesa selecionada",
    )
    record_expense(
        user,
        family,
        account,
        expense_category,
        "20.00",
        transaction_date="2026-01-10",
        competence_date="2026-01-01",
        description="Despesa de outro mês",
    )
    client.force_login(user)

    response = client.get(reverse("planning:monthly"), {"month": "2026-02-01"})
    content = response.content.decode()

    assert response.status_code == 200
    assert "Entrada selecionada" in content
    assert "Despesa selecionada" in content
    assert "Despesa de outro mês" not in content
    assert "Fevereiro de 2026" in content


@pytest.mark.django_db
def test_monthly_report_accepts_month_picker_format(client):
    user = User.objects.create_user(username="ana")
    create_family(user, "Casa")
    client.force_login(user)

    response = client.get(reverse("planning:monthly"), {"month": "2026-02"})

    assert response.status_code == 200
    assert "Fevereiro de 2026" in response.content.decode()
