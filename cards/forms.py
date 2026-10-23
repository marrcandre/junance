from django import forms

from cards.models import Card
from ledger.models import Category


class PurchaseForm(forms.Form):
    card = forms.ModelChoiceField(queryset=Card.objects.none())
    category = forms.ModelChoiceField(queryset=Category.objects.none())
    amount = forms.DecimalField(max_digits=14, decimal_places=2, min_value=0.01)
    purchase_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    installments = forms.IntegerField(min_value=1, initial=1)
    description = forms.CharField(required=False, max_length=255)

    def __init__(self, family, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["card"].queryset = Card.objects.filter(family=family, active=True)
        self.fields["category"].queryset = Category.objects.filter(
            family=family, kind=Category.Kind.EXPENSE, active=True
        )
