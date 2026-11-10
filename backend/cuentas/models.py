from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from django.db.models.functions import Lower

from .validators import validar_cedula, validar_telefono


class Usuario(AbstractUser):

    ROLES = [
        ("CLIENTE", "Cliente"),
        ("ADMIN_COMPLEJO", "Administrador de complejo"),
        ("ADMIN_PLATAFORMA", "Administrador de plataforma"),
    ]

    email = models.EmailField(
        unique=True,
        validators=[EmailValidator()]
    )

    cedula = models.CharField(
        max_length=10,
        unique=True,
        null=True,
        blank=True,
        validators=[validar_cedula]
    )

    telefono = models.CharField(
        max_length=10,
        blank=True,
        validators=[validar_telefono]
    )

    rol = models.CharField(
        max_length=20,
        choices=ROLES,
        default="CLIENTE"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("email"),
                name="usuario_email_unico_sin_mayusculas"
            )
        ]

    def clean(self):
        super().clean()

        if self.email:
            self.email = self.email.strip().lower()

        if self.cedula == "":
            self.cedula = None

    def __str__(self):
        return f"{self.username} - {self.email}"
