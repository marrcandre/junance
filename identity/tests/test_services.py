from types import SimpleNamespace

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

from identity.models import Family, FamilyMember, FamilyRole
from identity.services import (
    add_family_member,
    create_family,
    get_active_family,
    require_family_membership,
)

User = get_user_model()


@pytest.mark.django_db
def test_create_family_adds_requesting_user_as_owner():
    user = User.objects.create_user(username="ana")

    family = create_family(user, "Casa")

    membership = FamilyMember.objects.get(family=family, user=user)
    assert family.name == "Casa"
    assert membership.role == FamilyRole.OWNER


@pytest.mark.django_db
def test_member_cannot_add_another_member_to_family():
    owner = User.objects.create_user(username="ana")
    member = User.objects.create_user(username="bruno")
    family = create_family(owner, "Casa")
    add_family_member(owner, family, member)

    with pytest.raises(PermissionDenied):
        add_family_member(member, family, User.objects.create_user(username="clara"))


@pytest.mark.django_db
def test_active_family_uses_selected_membership_only():
    user = User.objects.create_user(username="ana")
    first = create_family(user, "Casa")
    second = create_family(user, "Trabalho")
    request = SimpleNamespace(user=user, session={"active_family_id": second.id})

    assert get_active_family(request) == second

    request.session["active_family_id"] = 999999
    assert get_active_family(request) == first


@pytest.mark.django_db
def test_require_family_membership_rejects_other_family_and_insufficient_role():
    owner = User.objects.create_user(username="ana")
    member = User.objects.create_user(username="bruno")
    family = create_family(owner, "Casa")
    other_family = Family.objects.create(name="Outra")
    FamilyMember.objects.create(family=other_family, user=member, role=FamilyRole.MEMBER)

    with pytest.raises(PermissionDenied):
        require_family_membership(member, family)

    add_family_member(owner, family, member)
    with pytest.raises(PermissionDenied):
        require_family_membership(member, family, minimum_role=FamilyRole.ADMIN)
