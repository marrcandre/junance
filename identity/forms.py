from django import forms

from identity.models import Family


class FamilyForm(forms.ModelForm):
    class Meta:
        model = Family
        fields = ["name"]
