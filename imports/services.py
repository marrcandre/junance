import hashlib
from pathlib import Path

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from audit.models import AuditEvent
from audit.services import record_audit_event
from identity.services import require_family_membership
from imports.adapters.csv import parse_csv
from imports.adapters.ofx import parse_ofx
from imports.adapters.xlsx import parse_xlsx
from imports.models import ImportBatch, NormalizedEntry
from imports.validators import validate_entries

ADAPTERS = {"csv": parse_csv, "ofx": parse_ofx, "xlsx": parse_xlsx}


def _format_for(filename):
    suffix = Path(filename).suffix.lower().lstrip(".")
    if suffix not in ADAPTERS:
        raise ValidationError("Formato de importação não suportado.")
    return suffix


@transaction.atomic
def receive_file(actor, family, filename, content):
    require_family_membership(actor, family)
    content_hash = hashlib.sha256(content).hexdigest()
    existing = ImportBatch.objects.filter(family=family, content_hash=content_hash).first()
    if existing is not None:
        return existing
    return ImportBatch.objects.create(
        family=family,
        created_by=actor,
        filename=filename,
        source_format=_format_for(filename),
        content_hash=content_hash,
        content=content,
    )


@transaction.atomic
def preview_import(actor, batch):
    require_family_membership(actor, batch.family)
    if batch.status == ImportBatch.Status.CONFIRMED:
        return list(batch.entries.all())
    entries = ADAPTERS[batch.source_format](bytes(batch.content))
    errors = validate_entries(entries)
    if errors:
        batch.status = ImportBatch.Status.REJECTED
        batch.save(update_fields=["status"])
        raise ValidationError(errors)
    batch.entries.all().delete()
    normalized = [
        NormalizedEntry.objects.create(
            batch=batch,
            external_id=entry.external_id,
            transaction_date=entry.transaction_date,
            amount=entry.amount,
            description=entry.description,
            raw_data=entry.raw_data,
            candidate_type="income" if entry.amount > 0 else "expense",
        )
        for entry in entries
    ]
    batch.status = ImportBatch.Status.PREVIEWED
    batch.save(update_fields=["status"])
    return normalized


@transaction.atomic
def confirm_import(actor, batch):
    require_family_membership(actor, batch.family)
    if batch.status == ImportBatch.Status.CONFIRMED:
        return batch
    if batch.status != ImportBatch.Status.PREVIEWED:
        preview_import(actor, batch)
    batch.status = ImportBatch.Status.CONFIRMED
    batch.confirmed_at = timezone.now()
    batch.save(update_fields=["status", "confirmed_at"])
    record_audit_event(
        actor,
        batch.family,
        AuditEvent.Action.CREATE,
        batch,
        reason="Confirmação de importação revisada",
        after={"status": batch.status, "entries": batch.entries.count()},
    )
    return batch
