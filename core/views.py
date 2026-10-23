from datetime import date

from django.shortcuts import render

from identity.services import get_active_family
from ledger.queries import family_accounts
from planning.queries import monthly_summary


def dashboard(request):
    family = get_active_family(request) if request.user.is_authenticated else None
    accounts = family_accounts(family) if family is not None else []
    competence = date.today().replace(day=1)
    summary = monthly_summary(family, competence) if family is not None else None
    return render(
        request,
        "core/dashboard.html",
        {
            "family": family,
            "accounts": accounts,
            "summary": summary,
            "competence": competence,
        },
    )
