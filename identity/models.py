from django.conf import settings
from django.db import models


class FamilyRole(models.TextChoices):
    OWNER = "owner", "Proprietário"
    ADMIN = "admin", "Administrador"
    MEMBER = "member", "Membro"


class Family(models.Model):
    name = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name", "id"]

    def __str__(self):
        return self.name


class FamilyMember(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="family_memberships",
    )
    role = models.CharField(max_length=20, choices=FamilyRole.choices)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["family", "user"],
                name="unique_family_member_user",
            )
        ]
        indexes = [
            models.Index(fields=["user", "family"], name="family_member_user_family_idx"),
        ]

    def __str__(self):
        return f"{self.user} em {self.family}"
