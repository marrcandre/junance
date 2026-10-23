from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from cards.models import Card
from cards.services import record_card_purchase
from identity.services import create_family
from ledger.models import Category, Transfer
from ledger.services import create_account, create_category, record_expense, record_income
from planning.models import Budget
from planning.services import create_budget

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


@pytest.mark.django_db
def test_monthly_page_has_separate_entry_and_expense_tables_with_actions(client):
    user = User.objects.create_user(username="ana")
    create_family(user, "Casa")
    client.force_login(user)

    response = client.get(reverse("planning:monthly"), {"month": "2026-02"})
    content = response.content.decode()

    assert response.status_code == 200
    assert "Nova entrada" in content
    assert "Nova saída" in content
    assert "Entradas do mês" in content
    assert "Saídas do mês" in content


@pytest.mark.django_db
def test_create_income_from_monthly_page_uses_selected_competence(client):
    user = User.objects.create_user(username="ana")
    family = create_family(user, "Casa")
    account = create_account(family, "Conta")
    category = create_category(family, "Salário", kind=Category.Kind.INCOME)
    client.force_login(user)

    response = client.post(
        reverse("planning:transaction_create", kwargs={"kind": "income"}),
        {
            "account": account.pk,
            "category": category.pk,
            "amount": "2500.00",
            "transaction_date": "2026-02-05",
            "competence_date": "2026-02-01",
            "description": "Salário de fevereiro",
        },
        QUERY_STRING="month=2026-02",
    )

    assert response.status_code == 302
    assert response.url == f"{reverse('planning:monthly')}?month=2026-02"
    assert family.incomes.get().description == "Salário de fevereiro"
    assert "Entrada criada." in client.get(response.url).content.decode()


@pytest.mark.django_db
def test_create_expense_from_monthly_page_returns_htmx_redirect_and_message(client):
    user = User.objects.create_user(username="ana")
    family = create_family(user, "Casa")
    account = create_account(family, "Conta")
    category = create_category(family, "Mercado", kind=Category.Kind.EXPENSE)
    client.force_login(user)

    response = client.post(
        reverse("planning:transaction_create", kwargs={"kind": "expense"}),
        {
            "account": account.pk,
            "category": category.pk,
            "amount": "40.00",
            "transaction_date": "2026-02-10",
            "competence_date": "2026-02-01",
            "description": "Feira",
        },
        QUERY_STRING="month=2026-02",
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 204
    assert response.headers["HX-Redirect"] == f"{reverse('planning:monthly')}?month=2026-02"
    assert family.expenses.get().description == "Feira"


@pytest.mark.django_db
def test_edit_and_cancel_expense_from_monthly_page(client):
    user = User.objects.create_user(username="ana")
    family = create_family(user, "Casa")
    account = create_account(family, "Conta")
    category = create_category(family, "Mercado", kind=Category.Kind.EXPENSE)
    expense = record_expense(
        user,
        family,
        account,
        category,
        "40.00",
        transaction_date="2026-02-10",
        competence_date="2026-02-01",
        description="Feira",
    )
    client.force_login(user)

    edit_response = client.post(
        reverse(
            "planning:transaction_edit",
            kwargs={"kind": "expense", "pk": expense.pk},
        ),
        {
            "account": account.pk,
            "category": category.pk,
            "amount": "45.00",
            "transaction_date": "2026-02-10",
            "competence_date": "2026-02-01",
            "description": "Feira atualizada",
        },
        QUERY_STRING="month=2026-02",
    )

    assert edit_response.status_code == 302
    expense.refresh_from_db()
    assert expense.amount == 45
    assert expense.description == "Feira atualizada"

    cancel_response = client.post(
        reverse(
            "planning:transaction_cancel",
            kwargs={"kind": "expense", "pk": expense.pk},
        ),
        {"reason": "Lançamento duplicado"},
        QUERY_STRING="month=2026-02",
    )

    assert cancel_response.status_code == 302
    expense.refresh_from_db()
    assert expense.is_void is True


@pytest.mark.django_db
def test_other_family_cannot_edit_monthly_transaction(client):
    user = User.objects.create_user(username="ana")
    other_user = User.objects.create_user(username="bruno")
    create_family(user, "Casa")
    other_family = create_family(other_user, "Outra")
    account = create_account(other_family, "Conta")
    category = create_category(other_family, "Mercado", kind=Category.Kind.EXPENSE)
    expense = record_expense(
        other_user,
        other_family,
        account,
        category,
        "40.00",
        transaction_date="2026-02-10",
        competence_date="2026-02-01",
    )
    client.force_login(user)

    response = client.post(
        reverse(
            "planning:transaction_edit",
            kwargs={"kind": "expense", "pk": expense.pk},
        ),
        {
            "account": account.pk,
            "category": category.pk,
            "amount": "45.00",
            "transaction_date": "2026-02-10",
            "competence_date": "2026-02-01",
            "description": "Tentativa",
        },
    )

    assert response.status_code == 404
    expense.refresh_from_db()
    assert expense.amount == 40


@pytest.mark.django_db
def test_monthly_page_shows_budgets_transfers_and_invoices_separately(client):
    user = User.objects.create_user(username="ana")
    family = create_family(user, "Casa")
    account = create_account(family, "Conta")
    destination = create_account(family, "Reserva")
    category = create_category(family, "Mercado", kind=Category.Kind.EXPENSE)
    create_budget(user, family, category, "100.00", competence_date="2026-02-01")
    Transfer.objects.create(
        family=family,
        source_account=account,
        destination_account=destination,
        amount="80.00",
        transaction_date="2026-02-04",
        competence_date="2026-02-01",
        description="Reserva mensal",
    )
    card = Card.objects.create(family=family, name="Cartão", last_four="1234")
    record_card_purchase(user, family, card, category, "120.00", purchase_date=date(2026, 2, 5))
    client.force_login(user)

    response = client.get(reverse("planning:monthly"), {"month": "2026-02"})
    content = response.content.decode()

    assert response.status_code == 200
    assert "Orçamento por categoria" in content
    assert "Mercado" in content
    assert "Transferências entre contas" in content
    assert "Reserva mensal" in content
    assert "Faturas de cartão" in content
    assert "Cartão" in content
    assert "R$ 0,00" in content


@pytest.mark.django_db
def test_budget_create_edit_delete_are_scoped_to_selected_month(client):
    user = User.objects.create_user(username="ana")
    family = create_family(user, "Casa")
    category = create_category(family, "Mercado", kind=Category.Kind.EXPENSE)
    client.force_login(user)

    create_response = client.post(
        reverse("planning:budget_create"),
        {"category": category.pk, "amount": "100.00", "competence_date": "2026-02-01"},
        QUERY_STRING="month=2026-02",
    )
    budget = Budget.objects.get(family=family)
    assert create_response.status_code == 302
    assert "Orçamento criado" in client.get(create_response.url).content.decode()

    edit_response = client.post(
        reverse("planning:budget_edit", kwargs={"pk": budget.pk}),
        {"category": category.pk, "amount": "125.00", "competence_date": "2026-02-01"},
        QUERY_STRING="month=2026-02",
    )
    assert edit_response.status_code == 302
    budget.refresh_from_db()
    assert budget.amount == 125

    delete_response = client.post(
        reverse("planning:budget_delete", kwargs={"pk": budget.pk}),
        {"reason": "Revisão"},
        QUERY_STRING="month=2026-02",
    )
    assert delete_response.status_code == 302
    assert not Budget.objects.filter(pk=budget.pk).exists()


@pytest.mark.django_db
def test_invalid_htmx_budget_form_stays_open_with_errors(client):
    user = User.objects.create_user(username="ana")
    family = create_family(user, "Casa")
    category = create_category(family, "Mercado", kind=Category.Kind.EXPENSE)
    client.force_login(user)

    response = client.post(
        reverse("planning:budget_create"),
        {"category": category.pk, "amount": "-1.00", "competence_date": "2026-02-01"},
        QUERY_STRING="month=2026-02",
        HTTP_HX_REQUEST="true",
    )

    assert response.status_code == 422
    assert "0.01" in response.content.decode()
    assert Budget.objects.count() == 0
