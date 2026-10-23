from django import forms

from ledger.models import Account, Category
from planning.models import Budget


class MonthlyTransactionForm(forms.Form):
    account = forms.ModelChoiceField(queryset=Account.objects.none(), label="Conta")
    category = forms.ModelChoiceField(queryset=Category.objects.none(), label="Categoria")
    amount = forms.DecimalField(
        max_digits=14,
        decimal_places=2,
        min_value=0.01,
        label="Valor",
        widget=forms.NumberInput(attrs={"step": "0.01", "min": "0.01"}),
    )
    transaction_date = forms.DateField(
        label="Data da transação", widget=forms.DateInput(attrs={"type": "date"})
    )
    competence_date = forms.DateField(
        label="Competência", widget=forms.DateInput(attrs={"type": "date"})
    )
    paid_at = forms.DateField(
        label="Data de pagamento", required=False, widget=forms.DateInput(attrs={"type": "date"})
    )
    description = forms.CharField(label="Descrição", required=False, max_length=255)

    def __init__(self, family, kind, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kind = kind
        self.fields["account"].queryset = Account.objects.filter(family=family, active=True)
        self.fields["category"].queryset = Category.objects.filter(
            family=family,
            kind=kind,
            active=True,
        )


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ("category", "amount", "competence_date")
        widgets = {
            "competence_date": forms.DateInput(attrs={"type": "date"}),
            "amount": forms.NumberInput(attrs={"step": "0.01", "min": "0.01"}),
        }

    def __init__(self, family, *args, competence=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.filter(
            family=family,
            kind=Category.Kind.EXPENSE,
            active=True,
        )
        if competence is not None and not self.is_bound:
            self.initial.setdefault("competence_date", competence)

    def clean_competence_date(self):
        value = self.cleaned_data["competence_date"]
        return value.replace(day=1)
