from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from cards.forms import PurchaseForm
from cards.models import Invoice
from cards.queries import family_cards
from cards.services import record_card_purchase
from identity.services import get_active_family


def _family_or_redirect(request):
    family = get_active_family(request)
    return family or redirect("identity:family_list")


@login_required
def card_list(request):
    family = _family_or_redirect(request)
    if not hasattr(family, "id"):
        return family
    return render(
        request,
        "cards/card_list.html",
        {"family": family, "cards": family_cards(family)},
    )


@login_required
def purchase_create(request):
    family = _family_or_redirect(request)
    if not hasattr(family, "id"):
        return family
    form = PurchaseForm(family, request.POST or None)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        record_card_purchase(
            request.user,
            family,
            data["card"],
            data["category"],
            data["amount"],
            purchase_date=data["purchase_date"],
            installments=data["installments"],
            description=data["description"],
        )
        return redirect("cards:card_list")
    return render(request, "cards/purchase_form.html", {"form": form, "family": family})


@login_required
def invoice_detail(request, pk):
    family = _family_or_redirect(request)
    if not hasattr(family, "id"):
        return family
    invoice = get_object_or_404(Invoice.objects.select_related("card"), pk=pk, family=family)
    return render(request, "cards/invoice_detail.html", {"family": family, "invoice": invoice})
