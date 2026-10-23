from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from identity.models import Family
from ledger.models import Account, Category

MONEY_VALIDATOR = MinValueValidator(Decimal("0.01"))


class Card(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="cards")
    name = models.CharField(max_length=150)
    last_four = models.CharField(max_length=4)
    closing_day = models.PositiveSmallIntegerField(default=1, validators=[MaxValueValidator(31)])
    due_day = models.PositiveSmallIntegerField(default=10, validators=[MaxValueValidator(31)])
    active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["family", "name"], name="unique_card_name_family")
        ]
        ordering = ["name", "id"]


class Invoice(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Aberta"
        PAID = "paid", "Paga"

    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="invoices")
    card = models.ForeignKey(Card, on_delete=models.PROTECT, related_name="invoices")
    competence_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["card", "competence_date"], name="unique_card_invoice_competence"
            )
        ]
        ordering = ["-competence_date", "-id"]

    @property
    def total_open(self):
        return self.installments.filter(status=Installment.Status.OPEN).aggregate(
            total=models.Sum("amount")
        )["total"] or Decimal("0.00")


class Purchase(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="card_purchases")
    card = models.ForeignKey(Card, on_delete=models.PROTECT, related_name="purchases")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="card_purchases")
    amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MONEY_VALIDATOR])
    purchase_date = models.DateField()
    description = models.CharField(max_length=255, blank=True)
    installments_count = models.PositiveSmallIntegerField(default=1)


class Installment(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Aberta"
        PAID = "paid", "Paga"

    purchase = models.ForeignKey(Purchase, on_delete=models.PROTECT, related_name="installments")
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name="installments")
    number = models.PositiveSmallIntegerField()
    amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MONEY_VALIDATOR])
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["purchase", "number"], name="unique_purchase_installment_number"
            )
        ]
        ordering = ["purchase_id", "number"]


class InvoicePayment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, related_name="payments")
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="invoice_payments")
    amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MONEY_VALIDATOR])
    paid_at = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
