from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from identity.forms import FamilyForm
from identity.models import FamilyMember
from identity.services import create_family


@login_required
def family_list(request):
    memberships = (
        FamilyMember.objects.filter(user=request.user)
        .select_related("family")
        .order_by("family__name", "family_id")
    )
    return render(request, "identity/family_list.html", {"memberships": memberships})


@login_required
def family_create(request):
    form = FamilyForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        create_family(request.user, form.cleaned_data["name"])
        return redirect("identity:family_list")
    return render(request, "identity/family_form.html", {"form": form})
