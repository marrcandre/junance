from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from identity.services import get_active_family
from ledger.forms import TransactionForm
from ledger.models import Account
from ledger.queries import family_expenses
from ledger.services import record_expense, record_income


def _family_or_redirect(request):
    family = get_active_family(request)
    return family or redirect("identity:family_list")


@login_required
def account_list(request):
    family = _family_or_redirect(request)
    if not hasattr(family, "id"):
        return family
    accounts = Account.objects.filter(family=family, active=True)
    return render(request, "ledger/account_list.html", {"family": family, "accounts": accounts})


@login_required
def transaction_list(request):
    family = _family_or_redirect(request)
    if not hasattr(family, "id"):
        return family
    expenses = family_expenses(family)
    return render(request, "ledger/transaction_list.html", {"family": family, "expenses": expenses})


@login_required
def transaction_create(request):
    family = _family_or_redirect(request)
    if not hasattr(family, "id"):
        return family
    form = TransactionForm(family, request.POST or None)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        if data["kind"] == "income":
            record_income(
                request.user,
                family,
                data["account"],
                data["category"],
                data["amount"],
                transaction_date=data["transaction_date"],
                competence_date=data["competence_date"],
                description=data["description"],
            )
        else:
            record_expense(
                request.user,
                family,
                data["account"],
                data["category"],
                data["amount"],
                transaction_date=data["transaction_date"],
                competence_date=data["competence_date"],
                description=data["description"],
            )
        return redirect("ledger:transaction_list")
    return render(request, "ledger/transaction_form.html", {"form": form, "family": family})
