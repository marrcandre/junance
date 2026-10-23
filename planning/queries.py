from datetime import timedelta
from decimal import Decimal

from django.db.models import Sum

from ledger.models import Expense, Income
from ledger.queries import monthly_totals
from planning.models import Budget


def monthly_summary(family, competence):
    totals = monthly_totals(family, competence)
    return {
        **totals,
        "balance": totals["income"] - totals["expense"],
    }


def monthly_report(family, competence):
    start_date = competence.replace(day=1)
    next_month = (start_date.replace(day=28) + timedelta(days=4)).replace(day=1)
    end_date = next_month - timedelta(days=1)
    incomes = Income.objects.filter(
        family=family,
        is_void=False,
        competence_date__range=(start_date, end_date),
    ).select_related("account", "category")
    expenses = Expense.objects.filter(
        family=family,
        is_void=False,
        competence_date__range=(start_date, end_date),
    ).select_related("account", "category")
    categories = (
        expenses.values("category__name")
        .annotate(total=Sum("amount"))
        .order_by("-total", "category__name")
    )
    return {
        "summary": monthly_summary(family, competence),
        "incomes": incomes,
        "expenses": expenses,
        "expense_categories": categories,
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
