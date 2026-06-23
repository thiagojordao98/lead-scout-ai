from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


class Organization(models.Model):
    name = models.CharField(max_length=255)
    credits_balance = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members",
    )
    role = models.CharField(
        max_length=20,
        choices=[("OWNER", "Dono"), ("SALES_REP", "Vendedor")],
        default="OWNER",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    @property
    def is_active_plan(self):
        try:
            user_plan = self.user_plan
        except Exception:
            return False
        return user_plan.status == "ACTIVE"

    def __str__(self):
        return self.email


