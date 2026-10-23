from datetime import timedelta
from decimal import Decimal

from django.db.models import Q, Sum

from cards.models import Invoice
from ledger.models import Category, Expense, Income, Transfer
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
    transfers = Transfer.objects.filter(
        family=family,
        is_void=False,
        competence_date__range=(start_date, end_date),
    ).select_related("source_account", "destination_account")
    invoices = Invoice.objects.filter(
        family=family,
        competence_date=competence,
    ).select_related("card")
    budget_map = {
        budget.category_id: budget
        for budget in Budget.objects.filter(
            family=family, competence_date=competence
        ).select_related("category")
    }
    budget_categories = (
        Category.objects.filter(
            family=family,
            kind=Category.Kind.EXPENSE,
        )
        .filter(
            Q(pk__in=budget_map)
            | Q(
                expenses__family=family,
                expenses__is_void=False,
                expenses__competence_date__range=(start_date, end_date),
            )
        )
        .distinct()
        .order_by("name", "id")
    )
    budgets = []
    for category in budget_categories:
        budget = budget_map.get(category.pk)
        realized = expenses.filter(category=category).aggregate(total=Sum("amount"))["total"]
        realized = realized or Decimal("0.00")
        planned = budget.amount if budget is not None else Decimal("0.00")
        budgets.append(
            {
                "budget": budget,
                "category": category,
                "planned": planned,
                "realized": realized,
                "balance": planned - realized,
            }
        )
    return {
        "summary": monthly_summary(family, competence),
        "incomes": incomes,
        "expenses": expenses,
        "expense_categories": categories,
        "budgets": budgets,
        "transfers": transfers,
        "invoices": invoices,
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
