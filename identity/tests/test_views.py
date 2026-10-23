import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from identity.services import create_family

User = get_user_model()


@pytest.mark.django_db
def test_authenticated_user_can_create_family(client):
    user = User.objects.create_user(username="ana", password="senha-segura")
    client.force_login(user)

    response = client.post(reverse("identity:family_create"), {"name": "Casa"})

    assert response.status_code == 302
    assert response.url == reverse("identity:family_list")


@pytest.mark.django_db
def test_family_list_does_not_reveal_another_users_family(client):
    user = User.objects.create_user(username="ana")
    other_user = User.objects.create_user(username="bruno")
    own_family = create_family(user, "Casa de Ana")
    other_family = create_family(other_user, "Casa de Bruno")
    client.force_login(user)

    response = client.get(reverse("identity:family_list"))
    content = response.content.decode()

    assert response.status_code == 200
    assert own_family.name in content
    assert other_family.name not in content


def test_anonymous_user_is_redirected_to_login(client):
    response = client.get(reverse("identity:family_list"))

    assert response.status_code == 302
    assert response.url.startswith("/accounts/login/")
