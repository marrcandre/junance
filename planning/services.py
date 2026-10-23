from django.core.exceptions import PermissionDenied
from django.db import transaction

from identity.services import require_family_membership
from planning.models import Budget


@transaction.atomic
def create_budget(actor, family, category, amount, *, competence_date):
    require_family_membership(actor, family)
    if category.family_id != family.id:
        raise PermissionDenied("A categoria não pertence à família autorizada.")
    budget = Budget(
        family=family,
        category=category,
        amount=amount,
        competence_date=competence_date,
    )
    budget.full_clean()
    budget.save()
    return budget
