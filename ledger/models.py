from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from identity.models import Family

MONEY_VALIDATOR = MinValueValidator(Decimal("0.01"))


class Account(models.Model):
    class Kind(models.TextChoices):
        CHECKING = "checking", "Conta corrente"
        SAVINGS = "savings", "Poupança"
        CASH = "cash", "Dinheiro"
        OTHER = "other", "Outra"

    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="accounts")
    name = models.CharField(max_length=150)
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.CHECKING)
    initial_balance = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["family", "name"], name="unique_account_name_family")
        ]
        ordering = ["name", "id"]

    def __str__(self):
        return self.name


class Category(models.Model):
    class Kind(models.TextChoices):
        INCOME = "income", "Receita"
        EXPENSE = "expense", "Despesa"

    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=150)
    kind = models.CharField(max_length=20, choices=Kind.choices)
    active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["family", "name", "kind"], name="unique_category_kind_family"
            )
        ]
        ordering = ["kind", "name", "id"]

    def __str__(self):
        return self.name


class EventBase(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="%(class)ss")
    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="%(class)ss",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="%(class)ss",
    )
    amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MONEY_VALIDATOR])
    transaction_date = models.DateField()
    competence_date = models.DateField()
    paid_at = models.DateField(null=True, blank=True)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Income(EventBase):
    class Meta:
        ordering = ["-transaction_date", "-id"]


class Expense(EventBase):
    class Meta:
        ordering = ["-transaction_date", "-id"]


class Transfer(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="transfers")
    source_account = models.ForeignKey(
        Account, on_delete=models.PROTECT, related_name="outgoing_transfers"
    )
    destination_account = models.ForeignKey(
        Account, on_delete=models.PROTECT, related_name="incoming_transfers"
    )
    amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MONEY_VALIDATOR])
    transaction_date = models.DateField()
    competence_date = models.DateField()
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-transaction_date", "-id"]
