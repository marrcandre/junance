from decimal import Decimal

from django.db.models import Sum

from ledger.models import Expense
from ledger.queries import monthly_totals
from planning.models import Budget


def monthly_summary(family, competence):
    totals = monthly_totals(family, competence)
    return {
        **totals,
        "balance": totals["income"] - totals["expense"],
    }


def budget_progress(family, competence, category):
    budget = Budget.objects.filter(
        family=family,
        category=category,
        competence_date=competence,
    ).first()
    planned = budget.amount if budget is not None else Decimal("0.00")
    spent = Expense.objects.filter(
        family=family,
        category=category,
        competence_date=competence,
        is_void=False,
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    return {"planned": planned, "spent": spent, "remaining": planned - spent}
