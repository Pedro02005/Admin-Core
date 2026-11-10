from django.db import models
from django.conf import settings
from django.db.models import F, Q

from django.core.exceptions import ValidationError

class Reserva(models.Model):

    ESTADOS = [
        ("CONFIRMADA", "Confirmada"),
        ("CANCELADA", "Cancelada"),
    ]

    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="reservas"
    )

    cancha = models.ForeignKey(
        "complejos.Cancha",
        on_delete=models.PROTECT,
        related_name="reservas"
    )

    inicio = models.DateTimeField()
    fin = models.DateTimeField()

    estado = models.CharField(
        max_length=12,
        choices=ESTADOS,
        default="CONFIRMADA"
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    clave_solicitud = models.UUIDField(unique=True)

    cancelable_hasta = models.DateTimeField()

    class Meta:
        ordering = ["-inicio"]

        constraints = [
            models.CheckConstraint(
                condition=Q(inicio__lt=F("fin")),
                name="reserva_inicio_menor_fin"
            ),
            models.CheckConstraint(
                condition=Q(total__gte=0),
                name="reserva_total_no_negativo"
            ),
        ]

    def __str__(self):
        return f"Reserva {self.id} - {self.cancha}"
    
    def clean(self):
        super().clean()

        if not self.cancha_id or not self.inicio or not self.fin:
            return

        if self.inicio >= self.fin:
            raise ValidationError(
                "El inicio debe ser anterior al fin."
            )

        if self.estado == "CONFIRMADA":

            reservas = Reserva.objects.filter(
                cancha_id=self.cancha_id,
                estado="CONFIRMADA",
                inicio__lt=self.fin,
                fin__gt=self.inicio
            ).exclude(pk=self.pk)

            if reservas.exists():
                raise ValidationError(
                    "Ya existe una reserva confirmada "
                    "para esta cancha en ese horario."
                )