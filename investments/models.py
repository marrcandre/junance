from django.db import models

from identity.models import Family
from ledger.models import MONEY_VALIDATOR


class InvestmentPosition(models.Model):
    family = models.ForeignKey(
        Family,
        on_delete=models.CASCADE,
        related_name="investment_positions",
    )
    asset_name = models.CharField(max_length=150)
    quantity = models.DecimalField(max_digits=18, decimal_places=8, validators=[MONEY_VALIDATOR])
    cost_basis = models.DecimalField(max_digits=14, decimal_places=2, validators=[MONEY_VALIDATOR])

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["family", "asset_name"], name="unique_investment_asset_family"
            )
        ]


class InvestmentTransaction(models.Model):
    class Kind(models.TextChoices):
        CONTRIBUTION = "contribution", "Aporte"
        WITHDRAWAL = "withdrawal", "Resgate"

    position = models.ForeignKey(
        InvestmentPosition, on_delete=models.PROTECT, related_name="transactions"
    )
    kind = models.CharField(max_length=20, choices=Kind.choices)
    quantity = models.DecimalField(max_digits=18, decimal_places=8, validators=[MONEY_VALIDATOR])
    amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MONEY_VALIDATOR])
    transaction_date = models.DateField()
