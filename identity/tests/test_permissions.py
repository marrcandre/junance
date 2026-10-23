import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

from identity.models import FamilyRole
from identity.permissions import require_member_management
from identity.services import create_family

User = get_user_model()


@pytest.mark.django_db
def test_owner_can_manage_family_members():
    user = User.objects.create_user(username="ana")
    family = create_family(user, "Casa")

    assert require_member_management(user, family).role == FamilyRole.OWNER


@pytest.mark.django_db
def test_regular_member_cannot_manage_family_members():
    owner = User.objects.create_user(username="ana")
    member = User.objects.create_user(username="bruno")
    family = create_family(owner, "Casa")
    from identity.services import add_family_member

    add_family_member(owner, family, member)

    with pytest.raises(PermissionDenied):
        require_member_management(member, family)
