import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_dashboard_returns_successful_response(client):
    response = client.get(reverse("core:dashboard"))

    assert response.status_code == 200
    assert "Junance" in response.content.decode()
