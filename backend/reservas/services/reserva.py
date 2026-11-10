from uuid import uuid4
from datetime import timedelta

from django.core.exceptions import ValidationError

from reservas.models import Reserva
from .cotizacion import cotizar_reserva


def confirmar_reserva(cliente, cancha, inicio, fin):

    # 1. Validar disponibilidad y calcular el precio
    cotizacion = cotizar_reserva(
        cancha,
        inicio,
        fin
    )

    # 2. Crear la reserva con el precio calculado
    reserva = Reserva(
        cliente=cliente,
        cancha=cancha,
        inicio=inicio,
        fin=fin,
        estado="CONFIRMADA",
        total=cotizacion["total"],
        clave_solicitud=uuid4(),
        cancelable_hasta=inicio - timedelta(hours=12)
    )

    # 3. Ejecutar las validaciones del modelo
    reserva.full_clean()

    # 4. Guardar en PostgreSQL
    reserva.save()

    return reserva