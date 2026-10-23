from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from audit.models import AuditEvent
from identity.services import create_family
from ledger.models import Category
from ledger.services import create_category
from planning.models import Budget
from planning.services import create_budget, delete_budget, update_budget

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


@pytest.mark.django_db
def test_update_budget_changes_amount_and_category_with_audit():
    user = User.objects.create_user(username="ana")
    family = create_family(user, "Casa")
    original = create_category(family, "Mercado", kind=Category.Kind.EXPENSE)
    replacement = create_category(family, "Lazer", kind=Category.Kind.EXPENSE)
    budget = create_budget(
        user, family, original, Decimal("100.00"), competence_date=date(2026, 2, 1)
    )

    updated = update_budget(
        user,
        budget,
        category=replacement,
        amount=Decimal("140.00"),
        competence_date=date(2026, 2, 1),
    )

    assert updated.category == replacement
    assert updated.amount == Decimal("140.00")
    assert AuditEvent.objects.filter(
        family=family, action=AuditEvent.Action.UPDATE, entity_id=budget.pk
    ).exists()


@pytest.mark.django_db
def test_delete_budget_is_physical_and_audited():
    user = User.objects.create_user(username="ana")
    family = create_family(user, "Casa")
    category = create_category(family, "Mercado", kind=Category.Kind.EXPENSE)
    budget = create_budget(
        user, family, category, Decimal("100.00"), competence_date=date(2026, 2, 1)
    )
    budget_id = budget.pk

    delete_budget(user, budget, reason="Planejamento revisado")

    assert not Budget.objects.filter(pk=budget_id).exists()
    event = AuditEvent.objects.get(entity_id=budget_id)
    assert event.action == AuditEvent.Action.CANCEL
    assert event.reason == "Planejamento revisado"


@pytest.mark.django_db
def test_budget_competence_is_normalized_and_unique_by_month():
    user = User.objects.create_user(username="ana")
    family = create_family(user, "Casa")
    category = create_category(family, "Mercado", kind=Category.Kind.EXPENSE)
    create_budget(user, family, category, Decimal("100.00"), competence_date=date(2026, 2, 15))

    with pytest.raises(ValidationError):
        create_budget(user, family, category, Decimal("120.00"), competence_date=date(2026, 2, 1))

    assert family.budgets.get().competence_date == date(2026, 2, 1)
