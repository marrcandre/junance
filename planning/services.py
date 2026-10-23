from datetime import date

from django.core.exceptions import PermissionDenied
from django.db import transaction

from audit.models import AuditEvent
from audit.services import record_audit_event
from identity.services import require_family_membership
from ledger.models import Category
from planning.models import Budget


def _month_start(value):
    if isinstance(value, str):
        value = date.fromisoformat(value)
    return value.replace(day=1)


@transaction.atomic
def create_budget(actor, family, category, amount, *, competence_date):
    require_family_membership(actor, family)
    if category.family_id != family.id:
        raise PermissionDenied("A categoria não pertence à família autorizada.")
    budget = Budget(
        family=family,
        category=category,
        amount=amount,
        competence_date=_month_start(competence_date),
    )
    budget.full_clean()
    budget.save()
    return budget


def _ensure_budget_category(family, category):
    if category.family_id != family.id:
        raise PermissionDenied("A categoria não pertence à família autorizada.")
    if category.kind != Category.Kind.EXPENSE:
        raise PermissionDenied("O orçamento precisa usar uma categoria de despesa.")


def _budget_snapshot(budget):
    return {
        "category_id": budget.category_id,
        "amount": str(budget.amount),
        "competence_date": budget.competence_date.isoformat(),
    }


@transaction.atomic
def update_budget(actor, budget, *, category, amount, competence_date):
    require_family_membership(actor, budget.family)
    _ensure_budget_category(budget.family, category)
    before = _budget_snapshot(budget)
    budget.category = category
    budget.amount = amount
    budget.competence_date = _month_start(competence_date)
    budget.full_clean()
    budget.save()
    record_audit_event(
        actor,
        budget.family,
        AuditEvent.Action.UPDATE,
        budget,
        before=before,
        after=_budget_snapshot(budget),
    )
    return budget


@transaction.atomic
def delete_budget(actor, budget, *, reason):
    require_family_membership(actor, budget.family)
    before = _budget_snapshot(budget)
    record_audit_event(
        actor,
        budget.family,
        AuditEvent.Action.CANCEL,
        budget,
        reason=reason,
        before=before,
        after={"deleted": True},
    )
    budget.delete()
