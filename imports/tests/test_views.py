import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from identity.services import create_family
from imports.models import ImportBatch

User = get_user_model()


@pytest.mark.django_db
def test_import_upload_requires_authentication(client):
    response = client.get(reverse("imports:upload"))

    assert response.status_code == 302
    assert response.url.startswith("/accounts/login/")


@pytest.mark.django_db
def test_import_preview_does_not_reveal_another_family(client):
    user = User.objects.create_user(username="ana")
    other_user = User.objects.create_user(username="bruno")
    family = create_family(user, "Casa")
    other_family = create_family(other_user, "Outra")
    assert family.id != other_family.id
    client.force_login(user)

    response = client.get(reverse("imports:upload"))

    assert response.status_code == 200
    assert "Importar" in response.content.decode()


@pytest.mark.django_db
def test_upload_creates_historical_account_for_active_family(client):
    user = User.objects.create_user(username="ana")
    family = create_family(user, "Casa")
    client.force_login(user)
    upload = SimpleUploadedFile(
        "statement.csv",
        b"external_id,date,amount,description\ntxn-001,2026-01-05,-42.50,Mercado\n",
        content_type="text/csv",
    )

    response = client.post(reverse("imports:upload"), {"file": upload})

    assert response.status_code == 302
    batch = ImportBatch.objects.get(family=family)
    assert batch.account.name == "Histórico da planilha"
    assert family.accounts.filter(name="Histórico da planilha").count() == 1
