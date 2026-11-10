from django.urls import path

from .views import ConfirmarReservaView

from .views import (
    DisponibilidadView,
    CotizarView,
)

urlpatterns = [
    path(
        "canchas/<int:cancha_id>/disponibilidad/",
        DisponibilidadView.as_view(),
        name="disponibilidad"
    ),

    path(
        "reservas/cotizar/",
        CotizarView.as_view(),
        name="cotizar"
    ),
    
    path(
    "reservas/",
    ConfirmarReservaView.as_view(),
    name="confirmar-reserva"
),
]