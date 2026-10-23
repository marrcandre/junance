from django.db import models

from identity.models import Family
from ledger.models import MONEY_VALIDATOR, Category


class Budget(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="budgets")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="budgets")
    competence_date = models.DateField()
    amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MONEY_VALIDATOR])

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["family", "category", "competence_date"],
                name="unique_budget_category_competence",
            )
        ]
