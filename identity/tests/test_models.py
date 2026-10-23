import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from identity.models import Family, FamilyMember, FamilyRole

User = get_user_model()


@pytest.mark.django_db
def test_family_member_has_explicit_role_and_unique_user_per_family():
    user = User.objects.create_user(username="ana")
    family = Family.objects.create(name="Casa")

    member = FamilyMember.objects.create(
        family=family,
        user=user,
        role=FamilyRole.OWNER,
    )

    assert member.role == FamilyRole.OWNER
    assert member.family_id == family.id
    assert member.user_id == user.id

    with pytest.raises(IntegrityError):
        FamilyMember.objects.create(
            family=family,
            user=user,
            role=FamilyRole.MEMBER,
        )


@pytest.mark.django_db
def test_family_member_requires_family():
    user = User.objects.create_user(username="bruno")

    with pytest.raises(IntegrityError):
        FamilyMember.objects.create(
            user=user,
            role=FamilyRole.MEMBER,
        )
