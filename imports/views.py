from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from identity.services import get_active_family
from imports.models import ImportBatch
from imports.services import confirm_import, preview_import, receive_file


@login_required
def upload(request):
    family = get_active_family(request)
    if family is None:
        return redirect("identity:family_list")
    if request.method == "POST" and request.FILES.get("file"):
        batch = receive_file(
            request.user,
            family,
            request.FILES["file"].name,
            request.FILES["file"].read(),
        )
        return redirect("imports:preview", pk=batch.pk)
    return render(request, "imports/upload.html", {"family": family})


@login_required
def preview(request, pk):
    family = get_active_family(request)
    batch = get_object_or_404(ImportBatch, pk=pk, family=family)
    entries = preview_import(request.user, batch)
    return render(request, "imports/preview.html", {"batch": batch, "entries": entries})


@login_required
def confirm(request, pk):
    family = get_active_family(request)
    batch = get_object_or_404(ImportBatch, pk=pk, family=family)
    if request.method == "POST":
        confirm_import(request.user, batch)
        return redirect("imports:upload")
    return redirect("imports:preview", pk=pk)
