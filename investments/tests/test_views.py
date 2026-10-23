import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from identity.services import create_family

User = get_user_model()


@pytest.mark.django_db
def test_position_list_is_scoped_to_active_family(client):
    user = User.objects.create_user(username="ana")
    create_family(user, "Casa")
    client.force_login(user)

    response = client.get(reverse("investments:position_list"))

    assert response.status_code == 200
    assert "Investimentos" in response.content.decode()
