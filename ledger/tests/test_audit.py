from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from audit.models import AuditEvent
from audit.services import cancel_event
from identity.services import create_family
from ledger.models import Category
from ledger.queries import family_expenses
from ledger.services import create_account, create_category, record_expense

User = get_user_model()


@pytest.mark.django_db
def test_cancelled_expense_is_retained_in_audit_but_excluded_from_active_query():
    user = User.objects.create_user(username="ana")
    family = create_family(user, "Casa")
    account = create_account(family, "Conta")
    category = create_category(family, "Mercado", kind=Category.Kind.EXPENSE)
    expense = record_expense(
        user,
        family,
        account,
        category,
        Decimal("25.00"),
        transaction_date=date(2026, 1, 10),
        competence_date=date(2026, 1, 1),
    )

    cancel_event(user, expense, reason="Corrigir histórico")

    assert list(family_expenses(family)) == []
    assert AuditEvent.objects.filter(entity_id=expense.id).count() == 1
