from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction

from audit.models import AuditEvent
from identity.services import require_family_membership


def _snapshot(event):
    snapshot = {}
    for field in event._meta.fields:
        if field.name in {"id", "created_at"}:
            continue
        key = field.attname if field.is_relation else field.name
        value = getattr(event, key)
        if hasattr(value, "isoformat"):
            value = value.isoformat()
        snapshot[key] = str(value) if field.name == "amount" else value
    return snapshot


@transaction.atomic
def record_audit_event(actor, family, action, entity, *, reason="", before=None, after=None):
    require_family_membership(actor, family)
    if entity.family_id != family.id:
        raise PermissionDenied("O evento não pertence à família autorizada.")
    return AuditEvent.objects.create(
        family=family,
        actor=actor,
        action=action,
        entity_type=entity._meta.label_lower,
        entity_id=entity.pk,
        before=before,
        after=after,
        reason=reason,
    )


@transaction.atomic
def cancel_event(actor, event, *, reason):
    require_family_membership(actor, event.family)
    if event.is_void:
        raise ValidationError("O evento já foi cancelado.")
    before = _snapshot(event)
    event.is_void = True
    event.save(update_fields=["is_void"])
    return record_audit_event(
        actor,
        event.family,
        AuditEvent.Action.CANCEL,
        event,
        reason=reason,
        before=before,
        after=_snapshot(event),
    )


def delete_event(actor, event, *, reason):
    require_family_membership(actor, event.family)
    raise ValidationError("Eventos financeiros não podem ser apagados fisicamente.")
