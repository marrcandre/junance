import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from cards.models import Card
from identity.services import create_family

User = get_user_model()


@pytest.mark.django_db
def test_card_list_does_not_reveal_another_family(client):
    user = User.objects.create_user(username="ana")
    other_user = User.objects.create_user(username="bruno")
    family = create_family(user, "Casa")
    other_family = create_family(other_user, "Outra")
    Card.objects.create(family=family, name="Meu cartão", last_four="1234")
    Card.objects.create(family=other_family, name="Outro cartão", last_four="5678")
    client.force_login(user)

    response = client.get(reverse("cards:card_list"))
    content = response.content.decode()

    assert response.status_code == 200
    assert "Meu cartão" in content
    assert "Outro cartão" not in content
