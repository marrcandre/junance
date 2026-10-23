import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from identity.services import create_family

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
