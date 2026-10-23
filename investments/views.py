from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from identity.services import get_active_family
from investments.models import InvestmentPosition


@login_required
def position_list(request):
    family = get_active_family(request)
    if family is None:
        return redirect("identity:family_list")
    positions = InvestmentPosition.objects.filter(family=family).order_by("asset_name")
    return render(
        request,
        "investments/position_list.html",
        {"family": family, "positions": positions},
    )
