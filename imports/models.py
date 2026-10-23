from django.conf import settings
from django.db import models

from identity.models import Family
from ledger.models import Account


class ImportBatch(models.Model):
    class Status(models.TextChoices):
        RECEIVED = "received", "Recebido"
        PREVIEWED = "previewed", "Pré-visualizado"
        CONFIRMED = "confirmed", "Confirmado"
        REJECTED = "rejected", "Rejeitado"

    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="import_batches")
    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="import_batches",
    )
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    filename = models.CharField(max_length=255)
    source_format = models.CharField(max_length=20)
    content_hash = models.CharField(max_length=64)
    content = models.BinaryField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.RECEIVED)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["family", "content_hash"], name="unique_import_content_family"
            )
        ]


class NormalizedEntry(models.Model):
    batch = models.ForeignKey(ImportBatch, on_delete=models.CASCADE, related_name="entries")
    external_id = models.CharField(max_length=255)
    transaction_date = models.DateField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    description = models.CharField(max_length=255)
    raw_data = models.JSONField(default=dict)
    candidate_type = models.CharField(max_length=20, blank=True)
    duplicate = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["batch", "external_id"], name="unique_normalized_entry_batch_external"
            )
        ]
