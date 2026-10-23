import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from identity.services import create_family

User = get_user_model()


@pytest.mark.django_db
def test_monthly_report_requires_family_context(client):
    user = User.objects.create_user(username="ana")
    create_family(user, "Casa")
    client.force_login(user)

    response = client.get(reverse("planning:monthly"), {"month": "2026-02-01"})

    assert response.status_code == 200
    assert "Resumo mensal" in response.content.decode()
