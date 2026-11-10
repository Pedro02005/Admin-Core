from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo

from django.utils import timezone
from rest_framework.exceptions import ValidationError

from complejos.models import (
    Cancha,
    HorarioAtencion,
    Bloqueo,
)
from reservas.models import Reserva


ZONA = ZoneInfo("America/Guayaquil")


def validar_intervalo(inicio, fin):

    if timezone.is_naive(inicio) or timezone.is_naive(fin):
        raise ValidationError(
            "Las fechas deben incluir zona horaria."
        )

    inicio_local = inicio.astimezone(ZONA)
    fin_local = fin.astimezone(ZONA)
    ahora = timezone.now()

    if inicio <= ahora:
        raise ValidationError(
            "La reserva debe comenzar en el futuro."
        )

    if inicio > ahora + timedelta(days=30):
        raise ValidationError(
            "Solo puedes reservar con hasta 30 días de anticipación."
        )

    if (
        inicio_local.minute not in [0, 30]
        or inicio_local.second != 0
        or inicio_local.microsecond != 0
    ):
        raise ValidationError(
            "El inicio debe ser en punto o a la media hora."
        )

    duracion = (fin - inicio).total_seconds() / 60

    if duracion < 60 or duracion > 180:
        raise ValidationError(
            "La duración debe estar entre 60 y 180 minutos."
        )

    if duracion % 30 != 0:
        raise ValidationError(
            "La duración debe aumentar en intervalos de 30 minutos."
        )

    if inicio_local.date() != fin_local.date():
        raise ValidationError(
            "Por ahora no permitimos reservas que crucen medianoche."
        )


def verificar_disponibilidad(cancha, inicio, fin):

    validar_intervalo(inicio, fin)

    if not cancha.activa or not cancha.complejo.activo:
        return False, "La cancha o el complejo están inactivos."

    inicio_local = inicio.astimezone(ZONA)
    fin_local = fin.astimezone(ZONA)

    dia = inicio_local.weekday()
    hora_inicio = inicio_local.time().replace(tzinfo=None)
    hora_fin = fin_local.time().replace(tzinfo=None)

    horarios = HorarioAtencion.objects.filter(
        cancha=cancha,
        dia_semana=dia,
        apertura__lte=hora_inicio,
        cierre__gte=hora_fin,
    )

    if not horarios.exists():
        return False, "El intervalo está fuera del horario de atención."

    bloqueado = Bloqueo.objects.filter(
        cancha=cancha,
        activo=True,
        inicio__lt=fin,
        fin__gt=inicio,
    ).exists()

    if bloqueado:
        return False, "La cancha está bloqueada en ese horario."

    ocupado = Reserva.objects.filter(
        cancha=cancha,
        estado="CONFIRMADA",
        inicio__lt=fin,
        fin__gt=inicio,
    ).exists()

    if ocupado:
        return False, "La cancha ya tiene una reserva confirmada."

    return True, "Cancha disponible."