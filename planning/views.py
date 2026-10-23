from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from identity.services import get_active_family
from ledger.models import Expense, Income
from ledger.services import (
    cancel_financial_event,
    record_expense,
    record_income,
    update_expense,
    update_income,
)
from planning.forms import BudgetForm, MonthlyTransactionForm
from planning.models import Budget
from planning.queries import monthly_report
from planning.services import create_budget, delete_budget, update_budget

MONTH_NAMES = (
    "janeiro",
    "fevereiro",
    "março",
    "abril",
    "maio",
    "junho",
    "julho",
    "agosto",
    "setembro",
    "outubro",
    "novembro",
    "dezembro",
)


def _month(value):
    try:
        if value and len(value) == 7:
            value = f"{value}-01"
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
    report = monthly_report(family, competence)
    return render(
        request,
        "planning/monthly.html",
        {
            "family": family,
            "competence": competence,
            "summary": report["summary"],
            "report": report,
            "month_label": f"{MONTH_NAMES[competence.month - 1].capitalize()} de {competence.year}",
        },
    )


def _transaction_type(kind):
    if kind == "income":
        return Income
    if kind == "expense":
        return Expense
    raise Http404("Tipo de lançamento inválido.")


def _transaction_form_context(request, family, kind, *, instance=None):
    initial = None
    if instance is not None and not request.POST:
        initial = {
            "account": instance.account_id,
            "category": instance.category_id,
            "amount": instance.amount,
            "transaction_date": instance.transaction_date,
            "competence_date": instance.competence_date,
            "paid_at": instance.paid_at,
            "description": instance.description,
        }
    form = MonthlyTransactionForm(
        family,
        kind,
        request.POST or None,
        initial=initial,
    )
    return form


def _monthly_redirect(request, competence):
    url = f"{reverse('planning:monthly')}?month={competence:%Y-%m}"
    if request.htmx:
        response = HttpResponse(status=204)
        response["HX-Redirect"] = url
        return response
    return redirect(url)


def _budget_form_context(request, family, *, competence, instance=None):
    return BudgetForm(
        family,
        request.POST or None,
        instance=instance,
        competence=competence,
    )


def _render_budget_form(request, family, form, *, competence, instance=None):
    context = {
        "family": family,
        "form": form,
        "competence": competence,
        "budget": instance,
        "form_title": "Editar orçamento" if instance else "Novo orçamento",
    }
    template = "planning/_budget_form.html" if request.htmx else "planning/budget_form.html"
    status = 422 if request.method == "POST" else 200
    return render(request, template, context, status=status)


def _render_transaction_form(request, family, kind, form, *, instance=None, competence=None):
    if instance is not None:
        form_title = "Editar entrada" if kind == "income" else "Editar saída"
    else:
        form_title = "Nova entrada" if kind == "income" else "Nova saída"
    context = {
        "family": family,
        "form": form,
        "kind": kind,
        "transaction": instance,
        "competence": competence,
        "form_title": form_title,
    }
    template = (
        "planning/_transaction_form.html" if request.htmx else "planning/transaction_form.html"
    )
    return render(request, template, context, status=422 if request.method == "POST" else 200)


@login_required
def transaction_create(request, kind):
    family = get_active_family(request)
    if family is None:
        return redirect("identity:family_list")
    if kind not in {"income", "expense"}:
        raise Http404("Tipo de lançamento inválido.")
    competence = _month(request.GET.get("month"))
    form = _transaction_form_context(request, family, kind)
    if request.method == "POST" and form.is_valid():
        try:
            data = form.cleaned_data
            service = record_income if kind == "income" else record_expense
            service(
                request.user,
                family,
                data["account"],
                data["category"],
                data["amount"],
                transaction_date=data["transaction_date"],
                competence_date=data["competence_date"],
                paid_at=data["paid_at"],
                description=data["description"],
            )
        except ValidationError as error:
            form.add_error(None, error)
        else:
            messages.success(request, "Entrada criada." if kind == "income" else "Saída criada.")
            return _monthly_redirect(request, data["competence_date"])
    return _render_transaction_form(request, family, kind, form, competence=competence)


@login_required
def transaction_edit(request, kind, pk):
    family = get_active_family(request)
    if family is None:
        return redirect("identity:family_list")
    model = _transaction_type(kind)
    instance = model.objects.filter(family=family, pk=pk).first()
    if instance is None:
        raise Http404("Lançamento não encontrado.")
    competence = _month(request.GET.get("month"))
    form = _transaction_form_context(request, family, kind, instance=instance)
    if request.method == "POST" and form.is_valid():
        try:
            data = form.cleaned_data
            service = update_income if kind == "income" else update_expense
            service(
                request.user,
                instance,
                account=data["account"],
                category=data["category"],
                amount=data["amount"],
                transaction_date=data["transaction_date"],
                competence_date=data["competence_date"],
                paid_at=data["paid_at"],
                description=data["description"],
            )
        except ValidationError as error:
            form.add_error(None, error)
        else:
            messages.success(request, "Lançamento atualizado.")
            return _monthly_redirect(request, data["competence_date"])
    return _render_transaction_form(
        request,
        family,
        kind,
        form,
        instance=instance,
        competence=competence,
    )


@login_required
def transaction_cancel(request, kind, pk):
    if request.method != "POST":
        raise Http404("Cancelamento exige POST.")
    family = get_active_family(request)
    if family is None:
        return redirect("identity:family_list")
    model = _transaction_type(kind)
    instance = model.objects.filter(family=family, pk=pk).first()
    if instance is None:
        raise Http404("Lançamento não encontrado.")
    try:
        cancel_financial_event(
            request.user,
            instance,
            reason=request.POST.get("reason", "Cancelado pela tela de planejamento"),
        )
    except ValidationError as error:
        messages.error(request, str(error))
    else:
        messages.success(request, "Lançamento cancelado.")
    return _monthly_redirect(request, _month(request.GET.get("month")))


@login_required
def budget_create(request):
    family = get_active_family(request)
    if family is None:
        return redirect("identity:family_list")
    competence = _month(request.GET.get("month"))
    form = _budget_form_context(request, family, competence=competence)
    if request.method == "POST":
        if form.is_valid():
            try:
                data = form.cleaned_data
                create_budget(
                    request.user,
                    family,
                    data["category"],
                    data["amount"],
                    competence_date=data["competence_date"],
                )
            except ValidationError as error:
                form.add_error(None, error)
            else:
                messages.success(request, "Orçamento criado.")
                return _monthly_redirect(request, data["competence_date"])
    return _render_budget_form(request, family, form, competence=competence)


@login_required
def budget_edit(request, pk):
    family = get_active_family(request)
    if family is None:
        return redirect("identity:family_list")
    budget = Budget.objects.filter(family=family, pk=pk).select_related("category").first()
    if budget is None:
        raise Http404("Orçamento não encontrado.")
    competence = _month(request.GET.get("month") or budget.competence_date.isoformat())
    form = _budget_form_context(request, family, competence=competence, instance=budget)
    if request.method == "POST" and form.is_valid():
        try:
            data = form.cleaned_data
            update_budget(
                request.user,
                budget,
                category=data["category"],
                amount=data["amount"],
                competence_date=data["competence_date"],
            )
        except ValidationError as error:
            form.add_error(None, error)
        else:
            messages.success(request, "Orçamento atualizado.")
            return _monthly_redirect(request, data["competence_date"])
    return _render_budget_form(request, family, form, competence=competence, instance=budget)


@login_required
def budget_delete(request, pk):
    if request.method != "POST":
        raise Http404("Exclusão exige POST.")
    family = get_active_family(request)
    if family is None:
        return redirect("identity:family_list")
    budget = Budget.objects.filter(family=family, pk=pk).first()
    if budget is None:
        raise Http404("Orçamento não encontrado.")
    delete_budget(
        request.user,
        budget,
        reason=request.POST.get("reason", "Excluído na tela de planejamento"),
    )
    messages.success(request, "Orçamento excluído.")
    return _monthly_redirect(request, _month(request.GET.get("month")))
