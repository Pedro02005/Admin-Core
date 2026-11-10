from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo

from rest_framework.exceptions import ValidationError

from complejos.models import Tarifa

from .disponibilidad import verificar_disponibilidad


ZONA = ZoneInfo("America/Guayaquil")


def cotizar_reserva(cancha, inicio, fin):

    disponible, motivo = verificar_disponibilidad(
        cancha,
        inicio,
        fin
    )

    if not disponible:
        raise ValidationError(motivo)

    inicio_local = inicio.astimezone(ZONA)
    fin_local = fin.astimezone(ZONA)

    dia = inicio_local.weekday()
    hora_inicio = inicio_local.time().replace(tzinfo=None)
    hora_fin = fin_local.time().replace(tzinfo=None)
    
    tarifas = Tarifa.objects.filter(
    cancha=cancha,
    dia_semana=dia,
    activa=True,
    inicio__lt=hora_fin,
    fin__gt=hora_inicio,
    ).order_by("inicio")

    cursor = inicio_local
    total = Decimal("0.00")
    detalles = []

    for tarifa in tarifas:

        fecha = inicio_local.date()

        inicio_tarifa = datetime.combine(
            fecha,
            tarifa.inicio,
            tzinfo=ZONA
        )

        fin_tarifa = datetime.combine(
            fecha,
            tarifa.fin,
            tzinfo=ZONA
        )

        if inicio_tarifa > cursor:
            raise ValidationError(
                "Existe una franja sin tarifa configurada."
            )

        if fin_tarifa <= cursor:
            continue

        tramo_inicio = cursor
        tramo_fin = min(fin_tarifa, fin_local)

        minutos = Decimal(
            str((tramo_fin - tramo_inicio).total_seconds())
        ) / Decimal("60")

        subtotal = (
            minutos * tarifa.valor_hora
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP
        )

        detalles.append({
            "tarifa_id": tarifa.id,
            "inicio": tramo_inicio.isoformat(),
            "fin": tramo_fin.isoformat(),
            "valor_hora": str(tarifa.valor_hora),
            "subtotal": str(subtotal),
        })

        total += subtotal
        cursor = tramo_fin

        if cursor >= fin_local:
            break

    if cursor < fin_local:
        raise ValidationError(
            "Las tarifas no cubren toda la reserva."
        )

    return {
        "cancha_id": cancha.id,
        "inicio": inicio_local.isoformat(),
        "fin": fin_local.isoformat(),
        "total": str(total),
        "moneda": "USD",
        "detalles": detalles,
    }