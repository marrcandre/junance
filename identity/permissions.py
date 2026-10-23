from identity.models import FamilyRole
from identity.services import require_family_membership


def require_member_management(user, family):
    return require_family_membership(user, family, minimum_role=FamilyRole.ADMIN)
