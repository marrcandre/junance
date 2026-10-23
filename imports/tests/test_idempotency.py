from pathlib import Path

import pytest
from django.contrib.auth import get_user_model

from identity.services import create_family
from imports.models import ImportBatch, NormalizedEntry
from imports.services import confirm_import, preview_import, receive_file
from ledger.models import Expense, Income
from ledger.services import create_account

User = get_user_model()
FIXTURE = Path(__file__).parent / "fixtures" / "statement.csv"


@pytest.mark.django_db
def test_confirming_same_file_twice_is_idempotent_and_auditable():
    user = User.objects.create_user(username="ana")
    family = create_family(user, "Casa")
    batch = receive_file(user, family, "statement.csv", FIXTURE.read_bytes())

    preview_import(user, batch)
    confirm_import(user, batch)
    confirm_import(user, batch)

    assert ImportBatch.objects.filter(family=family).count() == 1
    assert NormalizedEntry.objects.filter(batch=batch).count() == 2
    assert batch.refresh_from_db() is None
    assert batch.status == ImportBatch.Status.CONFIRMED


@pytest.mark.django_db
def test_confirming_import_creates_ledger_events_in_target_account():
    user = User.objects.create_user(username="ana")
    family = create_family(user, "Casa")
    account = create_account(family, "Histórico da planilha")
    batch = receive_file(
        user,
        family,
        "statement.csv",
        FIXTURE.read_bytes(),
        account=account,
    )

    preview_import(user, batch)
    confirm_import(user, batch)
    confirm_import(user, batch)

    assert Income.objects.filter(family=family, account=account).count() == 1
    assert Expense.objects.filter(family=family, account=account).count() == 1
