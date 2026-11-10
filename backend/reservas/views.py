from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from complejos.models import Cancha, HorarioAtencion

from .serializers import (
    ConsultaDisponibilidadSerializer,
    CotizacionSerializer,
)
from .services.disponibilidad import verificar_disponibilidad
from .services.cotizacion import cotizar_reserva

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.permissions import IsAuthenticated

from .services.reserva import confirmar_reserva


ZONA = ZoneInfo("America/Guayaquil")


class DisponibilidadView(APIView):

    def get(self, request, cancha_id):

        cancha = get_object_or_404(
            Cancha,
            id=cancha_id
        )

        serializer = ConsultaDisponibilidadSerializer(
            data=request.query_params
        )

        serializer.is_valid(raise_exception=True)

        fecha = serializer.validated_data["fecha"]
        duracion = serializer.validated_data["duracion"]

        dia = fecha.weekday()

        horarios = HorarioAtencion.objects.filter(
            cancha=cancha,
            dia_semana=dia
        ).order_by("apertura")

        opciones = []

        for horario in horarios:

            inicio = datetime.combine(
                fecha,
                horario.apertura,
                tzinfo=ZONA
            )

            cierre = datetime.combine(
                fecha,
                horario.cierre,
                tzinfo=ZONA
            )

            # Alinear al siguiente minuto 00 o 30.
            if inicio.minute not in (0, 30) or inicio.second:
                minutos = (
                    (30 - inicio.minute % 30) % 30
                )

                inicio = inicio.replace(
                    second=0,
                    microsecond=0
                )

                if minutos == 0:
                    minutos = 30

                inicio += timedelta(minutes=minutos)

            while inicio + timedelta(minutes=duracion) <= cierre:

                fin = inicio + timedelta(minutes=duracion)

                try:
                    disponible, motivo = verificar_disponibilidad(
                        cancha,
                        inicio,
                        fin
                    )

                    if disponible:
                        # No ofrecer intervalos sin cobertura tarifaria.
                        cotizacion = cotizar_reserva(
                            cancha,
                            inicio,
                            fin
                        )

                        opciones.append({
                            "inicio": inicio.isoformat(),
                            "fin": fin.isoformat(),
                            "total": cotizacion["total"],
                            "moneda": "USD"
                        })

                except ValidationError:
                    pass

                inicio += timedelta(minutes=30)

        return Response({
            "cancha": cancha.nombre,
            "fecha": fecha,
            "duracion": duracion,
            "opciones": opciones
        })


class CotizarView(APIView):

    def post(self, request):

        serializer = CotizacionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        datos = serializer.validated_data

        cotizacion = cotizar_reserva(
            datos["cancha"],
            datos["inicio"],
            datos["fin"]
        )

        return Response(cotizacion)
    
    
class ConfirmarReservaView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = CotizacionSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        datos = serializer.validated_data

        try:
            reserva = confirmar_reserva(
                cliente=request.user,
                cancha=datos["cancha"],
                inicio=datos["inicio"],
                fin=datos["fin"]
            )

        except DjangoValidationError as error:
            raise ValidationError(error.messages)

        return Response(
            {
                "id": reserva.id,
                "cliente": reserva.cliente.username,
                "cancha": reserva.cancha.nombre,
                "inicio": reserva.inicio,
                "fin": reserva.fin,
                "estado": reserva.estado,
                "total": str(reserva.total),
                "cancelable_hasta": reserva.cancelable_hasta
            },
            status=201
        )