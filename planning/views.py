from datetime import date

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from identity.services import get_active_family
from planning.queries import monthly_summary


def _month(value):
    try:
        parsed = date.fromisoformat(value)
    except TypeError, ValueError:
        return date.today().replace(day=1)
    return parsed.replace(day=1)


@login_required
def monthly(request):
    family = get_active_family(request)
    if family is None:
        return redirect("identity:family_list")
    competence = _month(request.GET.get("month"))
    return render(
        request,
        "planning/monthly.html",
        {
            "family": family,
            "competence": competence,
            "summary": monthly_summary(family, competence),
        },
    )


@login_required
def budget_create(request):
    family = get_active_family(request)
    if family is None:
        return redirect("identity:family_list")
    return render(request, "planning/budget_form.html", {"family": family})
