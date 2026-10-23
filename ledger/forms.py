from django import forms

from ledger.models import Account, Category


class TransactionForm(forms.Form):
    kind = forms.ChoiceField(
        choices=[("expense", "Despesa"), ("income", "Receita")],
        initial="expense",
    )
    account = forms.ModelChoiceField(queryset=Account.objects.none())
    category = forms.ModelChoiceField(queryset=Category.objects.none())
    amount = forms.DecimalField(max_digits=14, decimal_places=2, min_value=0.01)
    transaction_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    competence_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    description = forms.CharField(required=False, max_length=255)

    def __init__(self, family, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["account"].queryset = Account.objects.filter(family=family, active=True)
        self.fields["category"].queryset = Category.objects.filter(family=family, active=True)
