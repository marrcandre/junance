from calendar import monthrange
from decimal import Decimal

from django.db.models import Sum

from ledger.models import Account, Expense, Income


def family_accounts(family):
    return Account.objects.filter(family=family, active=True)


def family_expenses(family, start_date=None, end_date=None):
    queryset = Expense.objects.filter(family=family, is_void=False).select_related(
        "account", "category"
    )
    if start_date is not None:
        queryset = queryset.filter(competence_date__gte=start_date)
    if end_date is not None:
        queryset = queryset.filter(competence_date__lte=end_date)
    return queryset


def monthly_totals(family, month):
    start_date = month.replace(day=1)
    end_date = month.replace(day=monthrange(month.year, month.month)[1])
    income = Income.objects.filter(
        family=family,
        is_void=False,
        competence_date__range=(start_date, end_date),
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    expense = Expense.objects.filter(
        family=family,
        is_void=False,
        competence_date__range=(start_date, end_date),
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    return {"income": income, "expense": expense}
