from collections import Counter


def validate_entries(entries):
    errors = []
    duplicates = [
        key for key, count in Counter(entry.external_id for entry in entries).items() if count > 1
    ]
    if duplicates:
        errors.append(f"Identificadores duplicados: {', '.join(duplicates)}")
    for entry in entries:
        if not entry.external_id:
            errors.append("Identificador externo vazio")
        if not entry.description:
            errors.append(f"Descrição vazia para {entry.external_id}")
    return errors
