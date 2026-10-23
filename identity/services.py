from django.core.exceptions import PermissionDenied
from django.db import transaction

from identity.models import Family, FamilyMember, FamilyRole

ROLE_LEVELS = {
    FamilyRole.MEMBER: 1,
    FamilyRole.ADMIN: 2,
    FamilyRole.OWNER: 3,
}


@transaction.atomic
def create_family(user, name):
    family = Family.objects.create(name=name)
    FamilyMember.objects.create(family=family, user=user, role=FamilyRole.OWNER)
    return family


def require_family_membership(user, family, minimum_role=FamilyRole.MEMBER):
    try:
        membership = FamilyMember.objects.get(family=family, user=user)
    except FamilyMember.DoesNotExist as error:
        raise PermissionDenied("Usuário não pertence a esta família.") from error

    if ROLE_LEVELS[membership.role] < ROLE_LEVELS[minimum_role]:
        raise PermissionDenied("Usuário não possui o papel necessário.")
    return membership


@transaction.atomic
def add_family_member(actor, family, user, role=FamilyRole.MEMBER):
    require_family_membership(actor, family, minimum_role=FamilyRole.ADMIN)
    if role == FamilyRole.OWNER:
        raise PermissionDenied("Não é possível atribuir o papel de proprietário.")
    return FamilyMember.objects.create(family=family, user=user, role=role)


def get_active_family(request):
    memberships = FamilyMember.objects.filter(user=request.user).select_related("family")
    active_family_id = request.session.get("active_family_id")
    if active_family_id is not None:
        selected = memberships.filter(family_id=active_family_id).first()
        if selected is not None:
            return selected.family

    membership = memberships.order_by("family__name", "family_id").first()
    return membership.family if membership is not None else None
