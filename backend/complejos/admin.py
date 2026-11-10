from django.contrib import admin

from .models import (
    Complejo,
    Cancha,
    HorarioAtencion,
    Tarifa,
    Bloqueo,
)

from django.urls import path
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied

from .forms import TarifaAdminForm


class CanchaInline(admin.TabularInline):
    model = Cancha
    extra = 1
    fields = (
        "nombre",
        "deporte",
        "capacidad",
        "activa",
    )


@admin.register(Complejo)
class ComplejoAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "nombre",
        "ciudad",
        "activo",
    )

    search_fields = (
        "nombre",
        "ciudad",
    )

    list_filter = (
        "ciudad",
        "activo",
    )

    inlines = [CanchaInline]


@admin.register(Cancha)
class CanchaAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "nombre",
        "complejo",
        "deporte",
        "capacidad",
        "activa",
    )

    search_fields = (
        "nombre",
        "complejo__nombre",
    )

    list_filter = (
        "complejo",
        "deporte",
        "activa",
    )

    autocomplete_fields = ["complejo"]
    

@admin.register(HorarioAtencion)
class HorarioAtencionAdmin(admin.ModelAdmin):

    list_display = (
        "cancha",
        "dia_semana",
        "apertura",
        "cierre",
    )

    list_filter = ("dia_semana", "cancha__complejo")

    search_fields = (
        "cancha__nombre",
        "cancha__complejo__nombre",
    )

    autocomplete_fields = ["cancha"]


@admin.register(Tarifa)
class TarifaAdmin(admin.ModelAdmin):

    form = TarifaAdminForm

    list_display = (
        "cancha",
        "dia_semana",
        "inicio",
        "fin",
        "valor_hora",
        "activa",
    )

    list_filter = (
        "dia_semana",
        "activa",
        "cancha__complejo",
    )

    search_fields = (
        "cancha__nombre",
        "cancha__complejo__nombre",
    )

    fields = (
        "complejo",
        "cancha",
        "dia_semana",
        "inicio",
        "fin",
        "valor_hora",
        "activa",
    )

    class Media:
        js = ("complejos/js/tarifa.js",)

    def get_urls(self):

        urls = super().get_urls()

        nuevas_urls = [
            path(
                "canchas-por-complejo/",
                self.admin_site.admin_view(
                    self.canchas_por_complejo
                ),
                name="complejos_tarifa_canchas"
            ),
        ]

        return nuevas_urls + urls

    def canchas_por_complejo(self, request):

        if not (
            self.has_add_permission(request)
            or self.has_change_permission(request)
        ):
            raise PermissionDenied

        complejo_id = request.GET.get("complejo_id")

        if complejo_id and complejo_id.isascii() and complejo_id.isdigit():
            canchas = Cancha.objects.filter(
                complejo_id=complejo_id
            ).order_by("nombre")
        else:
            canchas = Cancha.objects.none()

        datos = [
            {
                "id": cancha.id,
                "nombre": cancha.nombre,
            }
            for cancha in canchas
        ]

        return JsonResponse({"canchas": datos})


@admin.register(Bloqueo)
class BloqueoAdmin(admin.ModelAdmin):

    list_display = (
        "cancha",
        "inicio",
        "fin",
        "motivo",
        "activo",
    )

    list_filter = (
        "activo",
        "cancha__complejo",
    )

    search_fields = (
        "cancha__nombre",
        "motivo",
    )

    autocomplete_fields = [
        "cancha",
        "administrador",
    ]