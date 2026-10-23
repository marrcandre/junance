from pathlib import Path

from django.conf import settings


def test_foundation_is_marked_complete_in_project_documentation():
    project_root = Path(settings.BASE_DIR)
    roadmap = (project_root / ".ai" / "roadmap.md").read_text()

    assert "Estado: concluída." in roadmap
